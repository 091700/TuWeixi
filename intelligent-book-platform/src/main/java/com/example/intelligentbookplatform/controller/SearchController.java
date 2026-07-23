package com.example.intelligentbookplatform.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.service.BookService;

@Controller
public class SearchController {
    
    @Autowired
    private BookService bookService;
    
    @GetMapping("/search")
    public String search(@RequestParam String keyword, Model model) {
        // 调用修复后的搜索方法
        List<Book> results = bookService.searchBooksByKeyword(keyword);
        model.addAttribute("results", results);
        model.addAttribute("keyword", keyword);
        return "search-results";
    }
}