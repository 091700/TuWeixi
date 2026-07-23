package com.example.intelligentbookplatform.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.multipart.MultipartFile;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.service.YOLOService;

@Controller
public class VisualSearchController {
    
    @Autowired
    private YOLOService yoloService;
    
    @GetMapping("/visual-search")
    public String visualSearchPage() {
        return "visual-search";
    }
    
    @PostMapping("/visual-search")
    public String visualSearch(@RequestParam("image") MultipartFile imageFile, Model model) {
        try {
            List<Book> results = yoloService.searchByImage(imageFile);
            model.addAttribute("results", results);
            model.addAttribute("message", "搜索完成，找到 " + results.size() + " 本相关图书");
        } catch (Exception e) {
            model.addAttribute("error", "搜索失败: " + e.getMessage());
        }
        return "visual-search";
    }
}