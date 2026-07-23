package com.example.intelligentbookplatform.service;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.example.intelligentbookplatform.model.User;
import com.example.intelligentbookplatform.repository.UserRepository;

@Service
@Transactional
public class UserService implements UserDetailsService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private PasswordEncoder passwordEncoder;
    
    public User registerUser(User user) {
        if (userRepository.findByUsername(user.getUsername()).isPresent()) {
            throw new RuntimeException("用户名已存在!");
        }
        if (userRepository.findByEmail(user.getEmail()).isPresent()) {
            throw new RuntimeException("邮箱已被注册!");
        }
        
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        return userRepository.save(user);
    }
    
    @Override
public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
    System.out.println("尝试登录用户: " + username);
    
    User user = userRepository.findByUsername(username)
            .orElseThrow(() -> {
                System.out.println("用户不存在: " + username);
                return new UsernameNotFoundException("用户不存在: " + username);
            });
    
    System.out.println("找到用户: " + user.getUsername());
    System.out.println("用户密码: " + user.getPassword());
    System.out.println("用户角色: " + user.getRole());
    
    return user;
}
    
    public User findByUsername(String username) {
        return userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }
    
    public User findById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("用户不存在"));
    }
}
