package com.example.intelligentbookplatform.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.stereotype.Service;

import com.example.intelligentbookplatform.dto.SearchResult;
import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.repository.elasticsearch.BookSearchRepository;

@Service
public class SearchService {
    
    @Autowired
    private BookSearchRepository bookSearchRepository;
    
    // 修复：调用新的搜索方法
    public List<Book> searchBooks(String keyword) {
        SearchHits<Book> searchHits = bookSearchRepository.searchByKeyword(keyword);
        return searchHits.getSearchHits()
            .stream()
            .map(SearchHit::getContent)
            .collect(Collectors.toList());
    }

    // 高亮搜索方法也同步修改
    public List<SearchResult> searchBooksWithHighlight(String keyword) {
        SearchHits<Book> searchHits = bookSearchRepository.searchByKeyword(keyword);
        return searchHits.getSearchHits().stream()
                .map(this::convertToSearchResult)
                .collect(Collectors.toList());
    }
    
    private SearchResult convertToSearchResult(SearchHit<Book> searchHit) {
        Book book = searchHit.getContent();
        SearchResult result = new SearchResult();
        result.setBook(book);
        
        // 处理高亮（保持不变）
        if (searchHit.getHighlightFields() != null) {
            List<String> titleHighlights = searchHit.getHighlightFields().get("title");
            List<String> authorHighlights = searchHit.getHighlightFields().get("author");
            List<String> descriptionHighlights = searchHit.getHighlightFields().get("description");
            
            if (titleHighlights != null && !titleHighlights.isEmpty()) {
                result.setHighlightedTitle(titleHighlights.get(0));
            }
            if (authorHighlights != null && !authorHighlights.isEmpty()) {
                result.setHighlightedAuthor(authorHighlights.get(0));
            }
            if (descriptionHighlights != null && !descriptionHighlights.isEmpty()) {
                result.setHighlightedDescription(descriptionHighlights.get(0));
            }
        }
        
        return result;
    }
}