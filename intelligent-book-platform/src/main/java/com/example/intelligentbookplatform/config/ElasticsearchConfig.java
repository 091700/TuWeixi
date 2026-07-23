package com.example.intelligentbookplatform.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.elasticsearch.repository.config.EnableElasticsearchRepositories;

@Configuration
@EnableElasticsearchRepositories(basePackages = "com.example.intelligentbookplatform.repository.elasticsearch")
public class ElasticsearchConfig {
    // 专门管理 Elasticsearch 的 Repository
}