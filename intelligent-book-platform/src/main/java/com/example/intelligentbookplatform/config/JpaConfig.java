package com.example.intelligentbookplatform.config;

import org.springframework.context.annotation.ComponentScan;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.FilterType;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

@Configuration
@EnableJpaRepositories(basePackages = "com.example.intelligentbookplatform.repository",
        excludeFilters = @ComponentScan.Filter(type = FilterType.ASPECTJ, 
        pattern = "com.example.intelligentbookplatform.repository.elasticsearch.*"))
public class JpaConfig {
    // JPA 配置，排除 elasticsearch 包
}