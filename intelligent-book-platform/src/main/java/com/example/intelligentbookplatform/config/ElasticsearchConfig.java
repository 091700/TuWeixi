package com.example.intelligentbookplatform.config;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.elasticsearch.repository.config.EnableElasticsearchRepositories;

/**
 * Elasticsearch Repository 启用配置
 * 通过 elasticsearch.enabled 控制（默认 false，避免启动期连接失败）
 */
@Configuration
@ConditionalOnProperty(name = "elasticsearch.enabled", havingValue = "true")
@EnableElasticsearchRepositories(basePackages = "com.example.intelligentbookplatform.repository.elasticsearch")
public class ElasticsearchConfig {
    // 仅当显式开启 elasticsearch.enabled=true 时启用 ES Repository
}
