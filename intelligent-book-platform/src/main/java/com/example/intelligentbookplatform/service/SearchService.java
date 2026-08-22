package com.example.intelligentbookplatform.service;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.elasticsearch.core.SearchHit;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.stereotype.Service;

import com.example.intelligentbookplatform.dto.SearchResult;
import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.repository.BookRepository;
import com.example.intelligentbookplatform.repository.elasticsearch.BookSearchRepository;

@Service
public class SearchService {
    
    @Autowired(required = false)
    private BookSearchRepository bookSearchRepository;   // ES 可选
    
    @Autowired
    private BookRepository bookRepository;               // MySQL 兜底
    
    // 调用新的搜索方法（ES 可用时走 ES，否则走 MySQL 模糊搜索）
    public List<Book> searchBooks(String keyword) {
        if (bookSearchRepository != null) {
            try {
                SearchHits<Book> searchHits = bookSearchRepository.searchByKeyword(keyword);
                return searchHits.getSearchHits()
                    .stream()
                    .map(SearchHit::getContent)
                    .collect(Collectors.toList());
            } catch (Exception e) {
                System.err.println("ES 搜索失败，回退到 MySQL: " + e.getMessage());
            }
        }
        return bookRepository.findByKeyword(keyword);
    }

    // 高亮搜索方法（ES 不可用时退化为普通结果）
    public List<SearchResult> searchBooksWithHighlight(String keyword) {
        List<Book> books = searchBooks(keyword);
        return books.stream().map(book -> {
            SearchResult result = new SearchResult();
            result.setBook(book);
            result.setHighlightedTitle(book.getTitle());
            result.setHighlightedAuthor(book.getAuthor());
            result.setHighlightedDescription(book.getDescription());
            return result;
        }).collect(Collectors.toList());
    }
}
