package com.example.demo.utils;

import cn.hutool.core.date.DateUtil;

import com.example.demo.entity.User;
import com.example.demo.mapper.UserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import javax.annotation.PostConstruct;
import javax.servlet.http.HttpServletRequest;
import java.util.Date;

@Component
public class TokenUtils {

    private static final Logger log = LoggerFactory.getLogger(TokenUtils.class);

    @Autowired
    private UserMapper userMapper;

    private static UserMapper staticUserMapper;

    @PostConstruct
    public void init() {
        staticUserMapper = userMapper;
    }

    /**
     * 生成token
     * @param user
     * @return
     */
    public static String genToken(User user) {
        return JWT.create().withExpiresAt(DateUtil.offsetDay(new Date(), 1)).withAudience(user.getId().toString())
                .sign(Algorithm.HMAC256(user.getPassword()));
    }

    /**
     * 获取token中的用户信息
     * @return
     */
    public static User getUser() {
        try {
            HttpServletRequest request = ((ServletRequestAttributes) RequestContextHolder.getRequestAttributes()).getRequest();
            String token = request.getHeader("token");
            String aud = JWT.decode(token).getAudience().get(0);
            Integer userId = Integer.valueOf(aud);
            return staticUserMapper.selectById(userId);
        } catch (Exception e) {
            log.error("解析token失败", e);
            return null;
        }
    }
}
