package com.example.intelligentbookplatform.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.intelligentbookplatform.service.BookService;

@Controller
public class HomeController {

    @Autowired
    private BookService bookService;

    // 处理首页请求（/ 路径）
    @GetMapping("/")
    public String home(
            @RequestParam(defaultValue = "0") int page, // 分页参数，默认第0页
            Model model) {
        
        // 1. 传递热门浏览图书（匹配模板中的 ${popularByViews}）
        model.addAttribute("popularByViews", bookService.findPopularBooksByViews(5));
        
        // 2. 传递热销图书（匹配模板中的 ${popularByPurchases}）
        model.addAttribute("popularByPurchases", bookService.findPopularBooksByPurchases(5));
        
        // 3. 传递分页的最新图书（匹配模板中的 ${books.content}）
        Pageable pageable = PageRequest.of(page, 8); // 每页显示8本图书
        Page<?> booksPage = bookService.findAllBooks(pageable);
        model.addAttribute("books", booksPage); // 关键：传递 books 变量
        
        return "index"; // 跳转到 index.html 模板
    }
}