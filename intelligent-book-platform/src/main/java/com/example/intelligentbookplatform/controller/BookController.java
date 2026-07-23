package com.example.intelligentbookplatform.controller;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.mvc.support.RedirectAttributes;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.model.User;
import com.example.intelligentbookplatform.service.BookService;

@Controller
@RequestMapping("/books")
public class BookController {

    @Autowired
    private BookService bookService;

    // 图书封面上传保存路径（在 application.properties 中配置）
    @Value("${upload.path}")
    private String uploadPath;

    // 1. 图书列表页
    @GetMapping
    public String listBooks(Model model) {
        List<Book> books = bookService.getAllBooks();
        model.addAttribute("books", books);
        return "index";
    }
    

    // 2. 图书详情页
    @GetMapping("/{id}")
    public String viewBook(@PathVariable Long id, Model model) {
        Book book = bookService.getBookById(id); // 调用修复后的方法
        model.addAttribute("book", book);
        return "book-detail";
    }
    @GetMapping("/my-books") // 保留原路径，支持 /books/my-books
    @RequestMapping(value = "/my-books", method = RequestMethod.GET) // 额外映射根路径的 /my-books
    public String myBooks(@AuthenticationPrincipal User user, Model model) {
        List<Book> myBooks = bookService.findBooksBySeller(user);
        model.addAttribute("myBooks", myBooks);
        return "my-books";
    }
    // 3. 发布图书页面
    @GetMapping("/new")
    public String showCreateForm(Model model) {
        model.addAttribute("book", new Book());
        return "book-form";
    }

    // 4. 提交发布图书（修复：调用正确的createBook方法）
    @PostMapping
    public String createBook(@ModelAttribute Book book,
                            @RequestParam("coverImage") MultipartFile coverImage,
                            @AuthenticationPrincipal User seller,
                            RedirectAttributes redirectAttributes) throws IOException {
        try {
            // 调用带封面和卖家参数的createBook方法
            Book savedBook = bookService.createBook(book, coverImage, seller);
            redirectAttributes.addFlashAttribute("message", "图书发布成功！");
            return "redirect:/books/" + savedBook.getId();
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "发布失败：" + e.getMessage());
            return "redirect:/books/new";
        }
    }

    // 5. 编辑图书页面
    @GetMapping("/{id}/edit")
    public String showEditForm(@PathVariable Long id, Model model, @AuthenticationPrincipal User user) {
        Book book = bookService.getBookById(id);
        if (!book.getSeller().getId().equals(user.getId())) {
            model.addAttribute("error", "没有权限编辑此图书");
            return "error";
        }
        model.addAttribute("book", book);
        return "book-form";
    }

    // 6. 提交编辑图书
    @PostMapping("/{id}")
    public String updateBook(@PathVariable Long id,
                            @ModelAttribute Book book,
                            @RequestParam("coverImage") MultipartFile coverImage,
                            @AuthenticationPrincipal User user,
                            RedirectAttributes redirectAttributes) throws IOException {
        try {
            Book existingBook = bookService.getBookById(id);
            if (!existingBook.getSeller().getId().equals(user.getId())) {
                redirectAttributes.addFlashAttribute("error", "没有权限编辑此图书");
                return "redirect:/books/" + id;
            }

            // 保留原有数据
            book.setId(id);
            book.setCreatedAt(existingBook.getCreatedAt());
            book.setSeller(user);
            book.setViewCount(existingBook.getViewCount());
            book.setPurchaseCount(existingBook.getPurchaseCount());

            // 处理新封面图片
            if (!coverImage.isEmpty()) {
                // 删除旧图片
                if (existingBook.getCoverImageUrl() != null) {
                    String oldFilename = existingBook.getCoverImageUrl().replace("/uploads/", "");
                    Files.deleteIfExists(Paths.get(uploadPath).resolve(oldFilename));
                }
                // 保存新图片
                String filename = System.currentTimeMillis() + "_" + coverImage.getOriginalFilename();
                Path filePath = Paths.get(uploadPath).resolve(filename);
                Files.copy(coverImage.getInputStream(), filePath);
                book.setCoverImageUrl("/uploads/" + filename);
            } else {
                book.setCoverImageUrl(existingBook.getCoverImageUrl());
            }

            bookService.updateBook(book);
            redirectAttributes.addFlashAttribute("message", "图书更新成功！");
            return "redirect:/books/" + id;
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "更新失败：" + e.getMessage());
            return "redirect:/books/" + id + "/edit";
        }
    }

    // 7. 删除图书
    @PostMapping("/{id}/delete")
    public String deleteBook(@PathVariable Long id,
                            @AuthenticationPrincipal User user,
                            RedirectAttributes redirectAttributes) {
        try {
            Book book = bookService.getBookById(id);
            if (!book.getSeller().getId().equals(user.getId())) {
                redirectAttributes.addFlashAttribute("error", "没有权限删除此图书");
                return "redirect:/books/" + id;
            }

            // 删除图片
            if (book.getCoverImageUrl() != null) {
                String filename = book.getCoverImageUrl().replace("/uploads/", "");
                Files.deleteIfExists(Paths.get(uploadPath).resolve(filename));
            }

            bookService.deleteBook(id);
            redirectAttributes.addFlashAttribute("message", "图书删除成功！");
            return "redirect:/my-books";
        } catch (Exception e) {
            redirectAttributes.addFlashAttribute("error", "删除失败：" + e.getMessage());
            return "redirect:/books/" + id;
        }
    }

    // 8. 同步所有图书到ES（使用bookService的同步方法）
    @GetMapping("/sync-all-to-es")
    @ResponseBody
    public String syncAllBooksToEs() {
        try {
            bookService.syncAllBooksToElasticsearch(); // 调用service层的同步方法
            return "同步完成：所有图书已同步到Elasticsearch";
        } catch (Exception e) {
            return "同步失败：" + e.getMessage();
        }
    }
}