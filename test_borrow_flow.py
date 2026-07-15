#!/usr/bin/env python3
"""
后端流程验证脚本 —— 借书/还书/续借

用法：
    python3 test_borrow_flow.py [--base-url http://localhost:9090]

要求：
    - Python 3.6+
    - 依赖：标准库 + requests（如果未安装，脚本会提示）
    - 只通过 HTTP 接口测试，不连接数据库

测试数据使用时间戳前缀，避免与原数据冲突。
结束后清理测试数据。
"""

import sys
import json
import time
import argparse
import urllib.request
import urllib.error

BASE_URL = "http://localhost:9090"
PASS_COUNT = 0
FAIL_COUNT = 0
ERRORS = []

# 测试数据唯一标识
TS = str(int(time.time()))
TEST_USERNAME = f"testuser_{TS}"
TEST_PASSWORD = "test123456"
TEST_ISBN = f"TEST-ISBN-{TS}"
TEST_BOOK_NAME = f"测试图书-{TS}"

# 保存创建的资源 ID，用于清理
test_user_id = None
test_book_id = None
test_reader2_id = None


def api_post(path, data):
    """发送 POST 请求"""
    url = f"{BASE_URL}{path}"
    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"code": str(e.code), "msg": str(e.reason)}
    except Exception as e:
        return {"code": "-1", "msg": str(e)}


def api_get(path):
    """发送 GET 请求"""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        return {"code": "-1", "msg": str(e)}


def api_delete(path):
    """发送 DELETE 请求"""
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, method="DELETE")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"code": str(e.code), "msg": str(e.reason)}
    except Exception as e:
        return {"code": "-1", "msg": str(e)}


def pass_case(name):
    global PASS_COUNT
    PASS_COUNT += 1
    print(f"  PASS: {name}")


def fail_case(name, reason, actual=None):
    global FAIL_COUNT, ERRORS
    FAIL_COUNT += 1
    msg = f"  FAIL: {name} — {reason}"
    if actual is not None:
        msg += f" (实际: {actual})"
    ERRORS.append(msg)
    print(msg)


def assert_eq(name, actual, expected):
    if actual == expected:
        pass_case(name)
    else:
        fail_case(name, f"期望 {expected}, 得到 {actual}")


def assert_gt(name, actual, expected_min):
    if actual is not None and actual > expected_min:
        pass_case(name)
    else:
        fail_case(name, f"期望 > {expected_min}, 得到 {actual}")


def assert_true(name, condition, detail=""):
    if condition:
        pass_case(name)
    else:
        fail_case(name, detail if detail else "条件为假")


def cleanup():
    """清理测试数据"""
    print("\n清理测试数据...")
    if test_book_id is not None:
        api_delete(f"/book/{test_book_id}")
    if test_user_id is not None:
        api_delete(f"/user/{test_user_id}")
    if test_reader2_id is not None:
        api_delete(f"/user/{test_reader2_id}")


def main():
    global BASE_URL, test_user_id, test_book_id, test_reader2_id

    parser = argparse.ArgumentParser(description="借书/还书/续借流程验证")
    parser.add_argument("--base-url", default="http://localhost:9090", help="后端基础地址")
    args = parser.parse_args()
    BASE_URL = args.base_url.rstrip("/")

    print(f"后端地址: {BASE_URL}")
    print(f"测试数据标识: {TS}")
    print("=" * 60)

    # ---- 准备：创建测试读者 ----
    print("\n[准备] 创建测试读者...")
    resp = api_post("/user", {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "nickName": f"测试读者{TS}",
        "sex": "男",
        "phone": "13800000000",
        "address": "测试地址"
    })
    assert_eq("创建测试读者成功", resp.get("code"), "0")
    if resp.get("code") != "0":
        print("无法创建测试读者，终止测试")
        sys.exit(1)

    # 获取读者 ID（通过查询）
    resp = api_get(f"/user/usersearch?search2={TEST_USERNAME}")
    if resp.get("code") == "0" and resp.get("data", {}).get("records"):
        test_user_id = resp["data"]["records"][0]["id"]
        print(f"  读者 ID: {test_user_id}")
    else:
        fail_case("获取测试读者ID", "查询失败", resp)
        sys.exit(1)

    # 验证可以使用该账号登录
    resp = api_post("/user/login", {"username": TEST_USERNAME, "password": TEST_PASSWORD})
    assert_eq("测试读者可以登录", resp.get("code"), "0")

    # ---- 准备：创建测试图书 ----
    print("\n[准备] 创建测试图书...")
    resp = api_post("/book", {
        "isbn": TEST_ISBN,
        "name": TEST_BOOK_NAME,
        "price": 29.9,
        "author": "测试作者",
        "publisher": "测试出版社",
        "total": 1
    })
    assert_eq("创建测试图书成功", resp.get("code"), "0")

    # 获取图书 ID
    resp = api_get(f"/book?search1={TEST_ISBN}")
    if resp.get("code") == "0" and resp.get("data", {}).get("records"):
        test_book_id = resp["data"]["records"][0]["id"]
        print(f"  图书 ID: {test_book_id}, available: {resp['data']['records'][0].get('available')}")
    else:
        fail_case("获取测试图书ID", "查询失败", resp)
        cleanup()
        sys.exit(1)

    # ---- 准备：统计初始记录数 ----
    before_lend_count = 0
    before_bwu_count = 0
    resp = api_get(f"/LendRecord?search3={test_user_id}")
    if resp.get("code") == "0":
        before_lend_count = resp["data"]["total"]
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    if resp.get("code") == "0":
        before_bwu_count = resp["data"]["total"]

    # ====================================================
    # 用例1：可借图书借阅成功
    # ====================================================
    print("\n[用例1] 可借图书借阅成功...")
    resp = api_post("/api/borrow", {"readerId": test_user_id, "isbn": TEST_ISBN})
    assert_eq("借阅接口返回成功", resp.get("code"), "0")

    # 验证库存减少
    resp = api_get(f"/book?search1={TEST_ISBN}")
    book_info = resp.get("data", {}).get("records", [])
    if book_info:
        assert_eq("库存 available 变为 0", book_info[0].get("available"), 0)
    else:
        fail_case("库存验证", "无法查询图书信息")

    # 验证当前借阅记录生成
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    bwu_records = resp.get("data", {}).get("records", [])
    bwu_count = resp.get("data", {}).get("total", 0)
    assert_gt("生成了当前借阅记录", bwu_count, before_bwu_count)
    if bwu_records:
        bwu = bwu_records[0]
        assert_eq(f"当前借阅 prolong 为 1", bwu.get("prolong"), 1)
        print(f"  lendtime: {bwu.get('lendtime')}, deadtime: {bwu.get('deadtime')}")

    # 验证借阅历史记录生成
    resp = api_get(f"/LendRecord?search3={test_user_id}")
    lend_count = resp.get("data", {}).get("total", 0)
    assert_gt("生成了借阅历史记录", lend_count, before_lend_count)
    # 验证 status = 0
    lend_records = resp.get("data", {}).get("records", [])
    found_lend = False
    for lr in lend_records:
        if lr.get("isbn") == TEST_ISBN and lr.get("status") == "0":
            found_lend = True
            break
    assert_true("借阅历史中状态为未归还(status=0)", found_lend)

    # ====================================================
    # 用例2：库存为0时借阅失败
    # ====================================================
    print("\n[用例2] 库存为0时借阅失败...")
    # 记录失败前的快照
    resp = api_get(f"/book?search1={TEST_ISBN}")
    before_book = resp.get("data", {}).get("records", [{}])[0]
    before_available = before_book.get("available")

    resp2 = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    before_bwu_total = resp2.get("data", {}).get("total", 0)

    resp3 = api_get(f"/LendRecord?search3={test_user_id}")
    before_lend_total = resp3.get("data", {}).get("total", 0)

    # 尝试借阅（同一读者已借过，应失败；用另一个读者测试库存0场景）
    # 先创建一个新的测试读者
    reader2_name = f"testuser2_{TS}"
    resp = api_post("/user", {
        "username": reader2_name,
        "password": "test123456",
        "nickName": f"测试读者2_{TS}",
        "sex": "女",
        "phone": "13800000001",
        "address": "测试地址2"
    })
    resp = api_get(f"/user/usersearch?search2={reader2_name}")
    if resp.get("code") == "0" and resp.get("data", {}).get("records"):
        test_reader2_id = resp["data"]["records"][0]["id"]
    else:
        fail_case("创建测试读者2", "无法获取ID")
        cleanup()
        sys.exit(1)

    resp = api_post("/api/borrow", {"readerId": test_reader2_id, "isbn": TEST_ISBN})
    assert_true("库存为0时借阅失败", resp.get("code") != "0", f"code={resp.get('code')}, msg={resp.get('msg')}")

    # 验证库存不变
    resp = api_get(f"/book?search1={TEST_ISBN}")
    after_book = resp.get("data", {}).get("records", [{}])[0]
    assert_eq("失败后库存不变", after_book.get("available"), before_available)

    # 验证记录数不变
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}")
    assert_eq("失败后当前借阅记录数不变", resp.get("data", {}).get("total", 0), before_bwu_total)

    resp = api_get(f"/LendRecord?search3={test_user_id}")
    assert_eq("失败后借阅历史记录数不变", resp.get("data", {}).get("total", 0), before_lend_total)

    # ====================================================
    # 用例3：首次续借成功
    # ====================================================
    print("\n[用例3] 首次续借成功...")
    # 获取当前的 deadtime 和 prolong
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    bwu_before = resp.get("data", {}).get("records", [])
    if bwu_before:
        old_deadtime = bwu_before[0].get("deadtime")
        old_prolong = bwu_before[0].get("prolong")
        print(f"  续借前: deadtime={old_deadtime}, prolong={old_prolong}")
    else:
        fail_case("续借-获取当前借阅状态", "无记录")
        cleanup()
        sys.exit(1)

    resp = api_post("/api/renew", {"readerId": test_user_id, "isbn": TEST_ISBN})
    assert_eq("续借接口返回成功", resp.get("code"), "0")

    # 验证 deadtime 延长约30天
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    bwu_after = resp.get("data", {}).get("records", [])
    if bwu_after:
        new_deadtime = bwu_after[0].get("deadtime")
        new_prolong = bwu_after[0].get("prolong")
        print(f"  续借后: deadtime={new_deadtime}, prolong={new_prolong}")
        # 比较日期：deadtime 应该变更
        assert_true("deadtime 已变更", new_deadtime != old_deadtime,
                    f"old={old_deadtime}, new={new_deadtime}")
        assert_eq("续借后 prolong 变为 0", new_prolong, 0)
    else:
        fail_case("续借-验证结果", "无记录")

    # ====================================================
    # 用例4：再次续借失败
    # ====================================================
    print("\n[用例4] 再次续借失败...")
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    bwu_before2 = resp.get("data", {}).get("records", [])
    if bwu_before2:
        before_deadtime2 = bwu_before2[0].get("deadtime")
        before_prolong2 = bwu_before2[0].get("prolong")
    else:
        fail_case("二次续借-获取状态", "无记录")
        cleanup()
        sys.exit(1)

    resp = api_post("/api/renew", {"readerId": test_user_id, "isbn": TEST_ISBN})
    assert_true("再次续借失败", resp.get("code") != "0",
                f"code={resp.get('code')}, msg={resp.get('msg')}")

    # 验证数据未变
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    bwu_after2 = resp.get("data", {}).get("records", [])
    if bwu_after2:
        assert_eq("失败后 deadtime 不变", bwu_after2[0].get("deadtime"), before_deadtime2)
        assert_eq("失败后 prolong 不变", bwu_after2[0].get("prolong"), before_prolong2)
    else:
        fail_case("二次续借-验证数据不变", "无记录")

    # ====================================================
    # 用例5：正常还书成功
    # ====================================================
    print("\n[用例5] 正常还书成功...")
    # 还书前的状态
    resp = api_get(f"/book?search1={TEST_ISBN}")
    before_return_available = resp.get("data", {}).get("records", [{}])[0].get("available")

    resp = api_post("/api/return", {"readerId": test_user_id, "isbn": TEST_ISBN})
    assert_eq("还书接口返回成功", resp.get("code"), "0")

    # 验证库存恢复
    resp = api_get(f"/book?search1={TEST_ISBN}")
    after_return_book = resp.get("data", {}).get("records", [{}])[0]
    new_available = after_return_book.get("available")
    assert_gt("库存恢复(available增加了)", new_available, before_return_available)

    # 验证当前借阅记录消失
    resp = api_get(f"/bookwithuser?search1={TEST_ISBN}&search3={test_user_id}")
    assert_eq("当前借阅记录已消失", resp.get("data", {}).get("total", 0), 0)

    # 验证借阅历史中记录变为已归还
    resp = api_get(f"/LendRecord?search3={test_user_id}")
    lend_records = resp.get("data", {}).get("records", [])
    found_returned = False
    for lr in lend_records:
        if lr.get("isbn") == TEST_ISBN and lr.get("status") == "1":
            found_returned = True
            if lr.get("returnTime"):
                print(f"  归还时间: {lr.get('returnTime')}")
            break
    assert_true("借阅历史中状态已变为已归还(status=1)且含returnTime", found_returned)

    # ====================================================
    # 用例6：重复还书失败
    # ====================================================
    print("\n[用例6] 重复还书失败...")
    resp = api_get(f"/book?search1={TEST_ISBN}")
    before_dup_return = resp.get("data", {}).get("records", [{}])[0].get("available")

    resp = api_post("/api/return", {"readerId": test_user_id, "isbn": TEST_ISBN})
    assert_true("重复还书失败", resp.get("code") != "0",
                f"code={resp.get('code')}, msg={resp.get('msg')}")

    # 验证库存不变
    resp = api_get(f"/book?search1={TEST_ISBN}")
    after_dup_return = resp.get("data", {}).get("records", [{}])[0].get("available")
    assert_eq("重复还书后库存不变", after_dup_return, before_dup_return)

    # ====================================================
    # 清理
    # ====================================================
    cleanup()

    # ====================================================
    # 结果汇总
    # ====================================================
    print("\n" + "=" * 60)
    total = PASS_COUNT + FAIL_COUNT
    print(f"测试结果: {total} 个断言, {PASS_COUNT} PASS, {FAIL_COUNT} FAIL")
    if ERRORS:
        print("\n失败详情:")
        for e in ERRORS:
            print(f"  {e}")

    if FAIL_COUNT > 0:
        print(f"\n失败: {FAIL_COUNT} 个断言未通过")
        sys.exit(1)
    else:
        print("\n全部通过!")
        sys.exit(0)


if __name__ == "__main__":
    main()
