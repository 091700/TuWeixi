
package com.smart.interview;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.smart.interview.mapper")
public class SmartInterviewApplication {

    public static void main(String[] args) {
        SpringApplication.run(SmartInterviewApplication.class, args);
        System.out.println("==================================================");
        System.out.println("🚀 AI Interview Backend 启动成功！");
        System.out.println("📡 WebSocket 接口已就绪: ws://127.0.0.1:8081/ws/interview/{userId}/{jobRole}");
        System.out.println("==================================================");
    }
}