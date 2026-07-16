const { test } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

const baseURL = process.env.BASE_URL || 'http://localhost:9876';
const themes = [
  { id: 'atlas', label: '馆藏运营台' },
  { id: 'academy', label: '书院阅读风' },
  { id: 'command', label: '数字指挥舱' },
];
const viewports = [
  { name: '1440x900', width: 1440, height: 900 },
  { name: '1280x800', width: 1280, height: 800 },
  { name: '1024x768', width: 1024, height: 768 },
  { name: '768x1024', width: 768, height: 1024 },
];
const pages = [
  { id: 'dashboard', route: '/dashboard' },
  { id: 'book', route: '/book' },
  { id: 'user', route: '/user' },
  { id: 'bookwithuser', route: '/bookwithuser' },
  { id: 'lendrecord', route: '/lendrecord' },
  { id: 'person', route: '/person' },
  { id: 'password', route: '/password' },
  { id: 'register', route: '/register' },
];

function ensureDir(dir) { fs.mkdirSync(dir, { recursive: true }); }
function metric(page) {
  return page.evaluate(() => ({
    viewport: { width: window.innerWidth, height: window.innerHeight },
    bodyScroll: document.body.scrollWidth,
    docScroll: document.documentElement.scrollWidth,
    theme: document.documentElement.dataset.theme || null,
  }));
}

test('theme-v2 visual and interaction evidence', async ({ browser }) => {
  test.setTimeout(360000);
  const evidence = {
    generatedAt: new Date().toISOString(), baseURL,
    viewports: viewports.map((item) => item.name), themes: {},
    notes: ['API status records are captured from /api responses; 200 means transport success.'],
  };
  const screenshotDir = path.resolve('acceptance/screenshots/theme-v2');
  ensureDir(screenshotDir);
  const context = await browser.newContext({ viewport: { width: viewports[0].width, height: viewports[0].height } });
  const page = await context.newPage();
  const consoleErrors = [];
  const pageErrors = [];
  const apiResponses = [];
  page.on('console', (message) => { if (message.type() === 'error') consoleErrors.push(message.text()); });
  page.on('pageerror', (error) => pageErrors.push(String(error)));
  page.on('response', (response) => {
    if (response.url().includes('/api/')) apiResponses.push({ url: response.url(), status: response.status() });
  });

  await page.goto(`${baseURL}/login`, { waitUntil: 'load' });
  await page.evaluate(() => localStorage.removeItem('library-theme'));
  await page.reload({ waitUntil: 'load' });
  const defaultTheme = await page.evaluate(() => document.documentElement.dataset.theme);
  const navigationBeforeSwitch = page.url();

  for (const theme of themes) {
    await page.locator('button.theme-option').filter({ hasText: theme.label }).click();
    await page.waitForTimeout(120);
    await page.screenshot({ path: path.join(screenshotDir, `${theme.id}-login.png`), fullPage: true });
  }

  const code = (await page.locator('.ValidCode span').allTextContents()).join('');
  await page.locator('input[placeholder="用户名"]').fill('admin');
  await page.locator('input[placeholder="密码"]').fill('123456');
  await page.locator('input[placeholder="验证码"]').fill(code);
  await page.getByRole('button', { name: /进入系统/ }).click();
  await page.waitForURL('**/dashboard');
  await page.waitForTimeout(300);
  const loginUrlAfter = page.url();
  const sessionUser = await page.evaluate(() => !!sessionStorage.getItem('user'));
  const adminUser = await page.evaluate(() => JSON.parse(sessionStorage.getItem('user') || '{}'));
  const suffix = `${Date.now()}`.slice(-8);
  const temporaryReader = {
    username: `theme_v2_${suffix}`,
    password: 'ThemeV2#123',
    nickName: `多风格验收读者-${suffix}`,
    phone: '13800001234',
    sex: '女',
    address: '上海市多风格验收馆',
    role: 2,
    operatorId: adminUser.id,
  };
  let temporaryReaderId = null;

  try {
    const createResponse = await context.request.post(`${baseURL}/api/user`, { data: temporaryReader });
    const createBody = await createResponse.json();
    evidence.temporaryReader = {
      username: temporaryReader.username,
      nickName: temporaryReader.nickName,
      create: { httpStatus: createResponse.status(), body: createBody },
      filters: {},
    };
    if (createResponse.status() !== 200 || createBody.code !== '0') {
      throw new Error(`temporary reader creation failed: ${JSON.stringify(createBody)}`);
    }
    const createdSearchResponse = await context.request.get(`${baseURL}/api/user/usersearch`, {
      params: { pageNum: 1, pageSize: 10, search1: '', search2: temporaryReader.nickName, search3: '', search4: '' },
    });
    const createdSearchBody = await createdSearchResponse.json();
    const createdRecords = createdSearchBody.data && createdSearchBody.data.records || [];
    if (createdSearchBody.code !== '0' || createdSearchBody.data.total !== 1 || createdRecords.length !== 1) {
      throw new Error(`temporary reader search was not unique: ${JSON.stringify(createdSearchBody)}`);
    }
    temporaryReaderId = createdRecords[0].id;
    evidence.temporaryReader.readerId = temporaryReaderId;
    evidence.temporaryReader.createdSearch = {
      httpStatus: createdSearchResponse.status(), total: createdSearchBody.data.total,
      records: createdRecords.map((item) => ({ id: item.id, username: item.username, nickName: item.nickName })),
    };

  for (const theme of themes) {
    await page.goto(`${baseURL}/dashboard`, { waitUntil: 'load' });
    await page.waitForTimeout(180);
    await page.locator('header button.theme-option').filter({ hasText: theme.label }).click();
    await page.waitForTimeout(120);
    const themeRecord = evidence.themes[theme.id] = { pages: {}, persistence: null, switch: null };
    const beforeSwitch = await page.evaluate(() => ({ url: location.href, theme: document.documentElement.dataset.theme }));
    const other = themes.find((item) => item.id !== theme.id);
    await page.locator('header button.theme-option').filter({ hasText: other.label }).click();
    await page.waitForTimeout(120);
    const afterSwitch = await page.evaluate(() => ({ url: location.href, theme: document.documentElement.dataset.theme }));
    await page.locator('header button.theme-option').filter({ hasText: theme.label }).click();
    themeRecord.switch = { before: beforeSwitch, after: afterSwitch, noRefresh: beforeSwitch.url === afterSwitch.url };
    await page.reload({ waitUntil: 'load' });
    await page.waitForTimeout(180);
    themeRecord.persistence = await page.evaluate((id) => ({ theme: document.documentElement.dataset.theme, stored: localStorage.getItem('library-theme'), expected: id }), theme.id);

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height });
      for (const item of pages.filter((entry) => entry.id !== 'register')) {
        const apiStart = apiResponses.length;
        await page.goto(`${baseURL}${item.route}`, { waitUntil: 'load' });
        await page.waitForTimeout(180);
        if (item.id === 'user') {
          await page.locator('input[placeholder="请输入姓名"]').fill(temporaryReader.nickName);
          const filteredResponsePromise = page.waitForResponse((response) =>
            response.url().includes('/api/user/usersearch') && response.request().method() === 'GET'
          );
          await page.getByRole('button', { name: /查询/ }).click();
          const filteredResponse = await filteredResponsePromise;
          const filteredBody = await filteredResponse.json();
          const filteredRecords = filteredBody.data && filteredBody.data.records || [];
          if (filteredBody.code !== '0' || filteredBody.data.total !== 1 || filteredRecords.length !== 1) {
            throw new Error(`${theme.id} user filter did not return exactly one record`);
          }
          evidence.temporaryReader.filters[`${theme.id}:${viewport.name}`] = {
            httpStatus: filteredResponse.status(), total: filteredBody.data.total,
            records: filteredRecords.map((entry) => ({ id: entry.id, username: entry.username, nickName: entry.nickName })),
          };
        }
        const stats = await metric(page);
        const key = `${viewport.name}:${item.id}`;
        themeRecord.pages[key] = {
          ...stats,
          pageErrors: pageErrors.slice(),
          consoleErrors: consoleErrors.slice(),
          apiResponses: apiResponses.slice(apiStart),
          api200: apiResponses.slice(apiStart).filter((response) => response.status === 200).length,
        };
        if (viewport.name === '1440x900' && ['dashboard', 'book', 'user'].includes(item.id)) {
          await page.screenshot({ path: path.join(screenshotDir, `${theme.id}-${item.id}.png`), fullPage: true });
        }
        if (viewport.name === '1440x900' && item.id === 'book') {
          const button = page.getByRole('button', { name: /上架图书/ });
          if (await button.count()) {
            await button.click();
            const dialog = page.getByRole('dialog', { name: '上架图书' });
            await dialog.waitFor({ state: 'visible' });
            themeRecord.dialogSmoke = { book: true };
            await dialog.getByRole('button', { name: '取消' }).click();
          }
        }
        if (viewport.name === '1440x900' && item.id === 'user') {
          const button = page.getByRole('button', { name: /新增读者/ });
          if (await button.count()) {
            await button.click();
            const dialog = page.getByRole('dialog', { name: '新增读者' });
            await dialog.waitFor({ state: 'visible' });
            themeRecord.dialogSmoke = { ...(themeRecord.dialogSmoke || {}), user: true };
            await dialog.getByRole('button', { name: '取消' }).click();
          }
        }
        if (viewport.name === '1440x900' && ['bookwithuser', 'lendrecord'].includes(item.id)) {
          const overdue = page.getByText('仅看逾期未还', { exact: true });
          if (await overdue.count()) {
            await overdue.click();
            await page.getByRole('button', { name: /查询/ }).click();
            await page.waitForTimeout(180);
            themeRecord.interactions = {
              ...(themeRecord.interactions || {}),
              [`${item.id}OverdueFilter`]: true,
            };
          }
        }
        if (viewport.name === '1440x900' && item.id === 'person') {
          const nameInput = page.locator('.profile-form input').nth(1);
          const original = await nameInput.inputValue();
          await nameInput.fill(`${original} `);
          await nameInput.fill(original);
          themeRecord.interactions = { ...(themeRecord.interactions || {}), personEdit: true };
        }
        if (viewport.name === '1440x900' && item.id === 'password') {
          await page.getByRole('button', { name: '重置' }).click();
          themeRecord.interactions = { ...(themeRecord.interactions || {}), passwordReset: true };
        }
      }
    }
    await page.goto(`${baseURL}/register`, { waitUntil: 'load' });
    themeRecord.pages[`1440x900:register`] = await metric(page);
    await page.getByText('管理员', { exact: true }).click();
    const authorizeVisible = await page.locator('input[placeholder="请输入管理员注册码"]').isVisible();
    await page.getByText('读者', { exact: true }).click();
    themeRecord.interactions = {
      ...(themeRecord.interactions || {}),
      registerRoleToggle: authorizeVisible,
    };
  }
  } finally {
    evidence.temporaryReader = evidence.temporaryReader || {
      username: temporaryReader.username, nickName: temporaryReader.nickName, filters: {},
    };
    if (temporaryReaderId) {
      const deleteResponse = await context.request.delete(
        `${baseURL}/api/user/${temporaryReaderId}?operatorId=${encodeURIComponent(adminUser.id)}`,
      );
      const deleteBody = await deleteResponse.json();
      evidence.temporaryReader.cleanup = {
        delete: { httpStatus: deleteResponse.status(), body: deleteBody },
      };
    }
    const finalSearchResponse = await context.request.get(`${baseURL}/api/user/usersearch`, {
      params: { pageNum: 1, pageSize: 10, search1: '', search2: temporaryReader.nickName, search3: '', search4: '' },
    });
    const finalSearchBody = await finalSearchResponse.json();
    evidence.temporaryReader.cleanup = {
      ...(evidence.temporaryReader.cleanup || {}),
      finalSearch: {
        httpStatus: finalSearchResponse.status(), code: finalSearchBody.code,
        total: finalSearchBody.data && finalSearchBody.data.total,
        records: finalSearchBody.data && finalSearchBody.data.records || [],
      },
    };
  }

  evidence.summary = {
    defaultTheme, loginUrlAfter, sessionUser,
    loginStayedOnPageDuringThemeLoop: navigationBeforeSwitch === `${baseURL}/login`,
    consoleErrors, pageErrors,
    api200Count: apiResponses.filter((response) => response.status === 200).length,
    apiNon200: apiResponses.filter((response) => response.status !== 200),
    temporaryReaderCleanupPassed:
      evidence.temporaryReader.cleanup &&
      evidence.temporaryReader.cleanup.delete &&
      evidence.temporaryReader.cleanup.delete.httpStatus === 200 &&
      evidence.temporaryReader.cleanup.delete.body.code === '0' &&
      evidence.temporaryReader.cleanup.finalSearch.httpStatus === 200 &&
      evidence.temporaryReader.cleanup.finalSearch.code === '0' &&
      evidence.temporaryReader.cleanup.finalSearch.total === 0 &&
      evidence.temporaryReader.cleanup.finalSearch.records.length === 0,
  };
  fs.writeFileSync(path.join(screenshotDir, 'browser-check.json'), `${JSON.stringify(evidence, null, 2)}\n`);
  await context.close();
  if (!evidence.summary.temporaryReaderCleanupPassed) {
    throw new Error(`temporary reader cleanup failed: ${JSON.stringify(evidence.temporaryReader.cleanup)}`);
  }
});
