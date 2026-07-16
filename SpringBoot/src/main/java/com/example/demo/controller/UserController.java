package com.example.demo.controller;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper;
import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.baomidou.mybatisplus.core.toolkit.Wrappers;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.example.demo.LoginUser;
import com.example.demo.commom.Result;
import com.example.demo.dto.ReaderCreateRequest;
import com.example.demo.entity.BookWithUser;
import com.example.demo.entity.User;
import com.example.demo.mapper.BookWithUserMapper;
import com.example.demo.mapper.UserMapper;
import com.example.demo.utils.TokenUtils;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import javax.annotation.Resource;
import java.util.List;
import java.util.regex.Pattern;

@RestController
@RequestMapping("/user")
public class UserController {
    private static final int ADMIN_ROLE = 1;
    private static final int READER_ROLE = 2;
    private static final Pattern USERNAME_PATTERN = Pattern.compile("^[A-Za-z0-9_]{2,32}$");
    private static final Pattern PASSWORD_PATTERN = Pattern.compile("^\\S{6,64}$");
    private static final Pattern PHONE_PATTERN = Pattern.compile("^[0-9+\\-]{6,20}$");

    @Resource
    private UserMapper userMapper;
    @Resource
    private BookWithUserMapper bookWithUserMapper;

    @PostMapping("/register")
    public Result<?> register(@RequestBody User user) {
        if (user == null || StringUtils.isBlank(user.getUsername())) {
            return Result.error("-1", "用户名不能为空");
        }
        user.setUsername(user.getUsername().trim());
        if (userMapper.selectCount(Wrappers.<User>lambdaQuery().eq(User::getUsername, user.getUsername())) > 0) {
            return Result.error("-1", "用户名已重复");
        }
        try {
            userMapper.insert(user);
            return Result.success();
        } catch (DataIntegrityViolationException e) {
            return Result.error("-1", "用户名已重复");
        }
    }

    @CrossOrigin
    @PostMapping("/login")
    public Result<?> login(@RequestBody User user) {
        if (user == null || user.getUsername() == null || user.getPassword() == null) {
            return Result.error("-1", "用户名或密码错误");
        }
        User res = userMapper.selectOne(Wrappers.<User>lambdaQuery()
                .eq(User::getUsername, user.getUsername())
                .eq(User::getPassword, user.getPassword()));
        if (res == null) {
            return Result.error("-1", "用户名或密码错误");
        }
        String token = TokenUtils.genToken(res);
        res.setToken(token);
        LoginUser loginUser = new LoginUser();
        loginUser.addVisitCount();
        return Result.success(res);
    }

    @PostMapping
    public Result<?> save(@RequestBody ReaderCreateRequest request) {
        String validationError = validateCreateRequest(request);
        if (validationError != null) {
            return Result.error("-1", validationError);
        }
        if (!isAdmin(request.getOperatorId())) {
            return Result.error("-1", "只有管理员可以新增读者");
        }

        String username = request.getUsername().trim();
        if (userMapper.selectCount(Wrappers.<User>lambdaQuery().eq(User::getUsername, username)) > 0) {
            return Result.error("-1", "用户名已重复");
        }

        User reader = new User();
        reader.setUsername(username);
        reader.setPassword(request.getPassword());
        reader.setNickName(request.getNickName().trim());
        reader.setPhone(trimToNull(request.getPhone()));
        reader.setSex(trimToNull(request.getSex()));
        reader.setAddress(trimToNull(request.getAddress()));
        reader.setRole(READER_ROLE);
        try {
            userMapper.insert(reader);
            return Result.success();
        } catch (DataIntegrityViolationException e) {
            return Result.error("-1", "用户名已重复");
        }
    }

    @PutMapping("/password")
    public Result<?> update(@RequestParam Integer id, @RequestParam String password2) {
        UpdateWrapper<User> updateWrapper = new UpdateWrapper<>();
        updateWrapper.eq("id", id);
        User user = new User();
        user.setPassword(password2);
        userMapper.update(user, updateWrapper);
        return Result.success();
    }

    @PutMapping
    public Result<?> password(@RequestBody User user) {
        try {
            userMapper.updateById(user);
            return Result.success();
        } catch (DataIntegrityViolationException e) {
            return Result.error("-1", "用户名已重复");
        }
    }

    @PostMapping("/deleteBatch")
    public Result<?> deleteBatch(@RequestBody List<Integer> ids) {
        return Result.error("-1", "批量删除用户已停用，请逐个确认删除");
    }

    @DeleteMapping("/{id}")
    @Transactional(rollbackFor = Exception.class)
    public Result<?> delete(@PathVariable Integer id, @RequestParam Integer operatorId) {
        if (!isAdmin(operatorId)) {
            return Result.error("-1", "只有管理员可以删除读者");
        }
        User target = userMapper.selectByIdForUpdate(id);
        if (target == null) {
            return Result.error("-1", "读者不存在");
        }
        if (target.getRole() == null || target.getRole() != READER_ROLE) {
            return Result.error("-1", "只允许删除普通读者，管理员账号不能通过此接口删除");
        }
        Integer activeBorrowCount = bookWithUserMapper.selectCount(
                Wrappers.<BookWithUser>lambdaQuery().eq(BookWithUser::getId, id));
        if (activeBorrowCount != null && activeBorrowCount > 0) {
            return Result.error("-1", "该读者存在未归还图书，不能删除");
        }
        if (userMapper.deleteById(id) != 1) {
            return Result.error("-1", "读者删除失败");
        }
        return Result.success();
    }

    @GetMapping
    public Result<?> findPage(@RequestParam(defaultValue = "1") Integer pageNum,
                              @RequestParam(defaultValue = "10") Integer pageSize,
                              @RequestParam(defaultValue = "") String search) {
        LambdaQueryWrapper<User> wrappers = Wrappers.<User>lambdaQuery();
        if (StringUtils.isNotBlank(search)) {
            wrappers.like(User::getNickName, search);
        }
        wrappers.eq(User::getRole, READER_ROLE);
        Page<User> userPage = userMapper.selectPage(new Page<>(pageNum, pageSize), wrappers);
        return Result.success(userPage);
    }

    @GetMapping("/usersearch")
    public Result<?> findPage2(@RequestParam(defaultValue = "1") Integer pageNum,
                               @RequestParam(defaultValue = "10") Integer pageSize,
                               @RequestParam(defaultValue = "") String search1,
                               @RequestParam(defaultValue = "") String search2,
                               @RequestParam(defaultValue = "") String search3,
                               @RequestParam(defaultValue = "") String search4) {
        LambdaQueryWrapper<User> wrappers = Wrappers.<User>lambdaQuery();
        if (StringUtils.isNotBlank(search1)) {
            wrappers.like(User::getId, search1);
        }
        if (StringUtils.isNotBlank(search2)) {
            wrappers.like(User::getNickName, search2);
        }
        if (StringUtils.isNotBlank(search3)) {
            wrappers.like(User::getPhone, search3);
        }
        if (StringUtils.isNotBlank(search4)) {
            wrappers.like(User::getAddress, search4);
        }
        wrappers.eq(User::getRole, READER_ROLE);
        Page<User> userPage = userMapper.selectPage(new Page<>(pageNum, pageSize), wrappers);
        return Result.success(userPage);
    }

    private boolean isAdmin(Integer operatorId) {
        if (operatorId == null) {
            return false;
        }
        User operator = userMapper.selectById(operatorId);
        return operator != null && operator.getRole() != null && operator.getRole() == ADMIN_ROLE;
    }

    private String validateCreateRequest(ReaderCreateRequest request) {
        if (request == null) {
            return "读者信息不能为空";
        }
        if (request.getRole() != null && request.getRole() != READER_ROLE) {
            return "此入口只能创建普通读者";
        }
        String username = request.getUsername() == null ? "" : request.getUsername().trim();
        if (!USERNAME_PATTERN.matcher(username).matches()) {
            return "用户名必须为2到32位字母、数字或下划线";
        }
        if (request.getPassword() == null || !PASSWORD_PATTERN.matcher(request.getPassword()).matches()) {
            return "初始密码必须为6到64位非空白字符";
        }
        String nickName = request.getNickName() == null ? "" : request.getNickName().trim();
        if (nickName.isEmpty() || nickName.length() > 50) {
            return "姓名必填且不能超过50个字符";
        }
        String phone = trimToNull(request.getPhone());
        if (phone != null && !PHONE_PATTERN.matcher(phone).matches()) {
            return "电话号码必须为6到20位数字，可包含+或-";
        }
        String sex = trimToNull(request.getSex());
        if (sex != null && !"男".equals(sex) && !"女".equals(sex)) {
            return "性别只能为男或女";
        }
        String address = trimToNull(request.getAddress());
        if (address != null && address.length() > 255) {
            return "地址不能超过255个字符";
        }
        return null;
    }

    private String trimToNull(String value) {
        if (value == null) {
            return null;
        }
        String trimmed = value.trim();
        return trimmed.isEmpty() ? null : trimmed;
    }
}
