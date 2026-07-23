package com.example.intelligentbookplatform.repository.elasticsearch;

import org.springframework.data.elasticsearch.annotations.Highlight;
import org.springframework.data.elasticsearch.annotations.HighlightField;
import org.springframework.data.elasticsearch.annotations.Query;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;
import org.springframework.stereotype.Repository;

import com.example.intelligentbookplatform.model.Book;

@Repository
public interface BookSearchRepository extends ElasticsearchRepository<Book, Long> {

    // 确保查询语句正确，使用IK分词器
    @Highlight(fields = {
        @HighlightField(name = "title"),
        @HighlightField(name = "author"),
        @HighlightField(name = "description")
    })
    @Query("{\n" +
           "  \"multi_match\": {\n" +
           "    \"query\": \"?0\",\n" +
           "    \"fields\": [\"title^2\", \"author^2\", \"description\"],\n" + // title和author权重更高
           "    \"analyzer\": \"ik_max_word\",\n" + // 中文分词
           "    \"fuzziness\": \"AUTO\"\n" + // 允许模糊匹配，提高容错性
           "  }\n" +
           "}")
    SearchHits<Book> searchByKeyword(String keyword);
}