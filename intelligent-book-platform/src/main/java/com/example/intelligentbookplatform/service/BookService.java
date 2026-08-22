package com.example.intelligentbookplatform.service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.core.SearchHits;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.model.User;
import com.example.intelligentbookplatform.repository.BookRepository;
import com.example.intelligentbookplatform.repository.elasticsearch.BookSearchRepository;

@Service
@Transactional
public class BookService {
    
    @Autowired
    private BookRepository bookRepository;
    
    @Autowired(required = false)
    private BookSearchRepository bookSearchRepository;   // ES 可选，未启用时为 null
    
    @Value("${upload.path}")
    private String uploadDir;

    public Book createBook(Book book, MultipartFile coverImage, User seller) throws IOException {
        return saveBook(book, coverImage, seller);
    }

    public Book saveBook(Book book, MultipartFile coverImage, User seller) throws IOException {
        if (coverImage != null && !coverImage.isEmpty()) {
            String normalizedUploadDir = uploadDir.endsWith("/") ? uploadDir : uploadDir + "/";
            String fileName = System.currentTimeMillis() + "_" + coverImage.getOriginalFilename();
            Path filePath = Paths.get(normalizedUploadDir + fileName);
            Files.createDirectories(filePath.getParent());
            Files.write(filePath, coverImage.getBytes());
            book.setCoverImageUrl("/uploads/" + fileName);
        }

        book.setSeller(seller);
        if (book.getViewCount() == null) book.setViewCount(0);
        if (book.getPurchaseCount() == null) book.setPurchaseCount(0);

        Book savedBook = bookRepository.save(book);
        // ES 同步（可选，关闭时跳过）
        if (bookSearchRepository != null) {
            try {
                bookSearchRepository.save(savedBook);
                System.out.println("ES 同步成功：" + savedBook.getTitle() + "（ID：" + savedBook.getId() + "）");
            } catch (Exception e) {
                System.err.println("ES 同步失败（不影响保存）：" + e.getMessage());
            }
        }
        return savedBook;
    }
    public Book updateBook(Book book) {
        Book updatedBook = bookRepository.save(book);
        if (bookSearchRepository != null) {
            try {
                bookSearchRepository.save(updatedBook);
                System.out.println("图书数据已在 Elasticsearch 更新: " + updatedBook.getTitle());
            } catch (Exception e) {
                System.err.println("Elasticsearch 更新失败（不影响更新）: " + e.getMessage());
            }
        }
        return updatedBook;
    }
    
    public void deleteBook(Long id) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("图书不存在"));

        bookRepository.deleteById(id);
        
        if (bookSearchRepository != null) {
            try {
                bookSearchRepository.deleteById(id);
                System.out.println("图书数据已从 Elasticsearch 删除: " + book.getTitle());
            } catch (Exception e) {
                System.err.println("从 Elasticsearch 删除失败（不影响删除）: " + e.getMessage());
            }
        }
    }

    public Book getBookById(Long id) {
        Book book = bookRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("图书不存在"));
        
        book.setViewCount(book.getViewCount() + 1);
        Book updatedBook = bookRepository.save(book);
        
        if (bookSearchRepository != null) {
            try {
                bookSearchRepository.save(updatedBook);
            } catch (Exception e) {
                System.err.println("同步浏览量到 Elasticsearch 失败（不影响浏览）: " + e.getMessage());
            }
        }
        return updatedBook;
    }

    public void syncAllBooksToElasticsearch() {
        if (bookSearchRepository == null) {
            System.out.println("ES 未启用，跳过同步");
            return;
        }
        try {
            List<Book> allBooks = bookRepository.findAll();
            bookSearchRepository.deleteAll();
            bookSearchRepository.saveAll(allBooks);
            System.out.println("成功同步 " + allBooks.size() + " 本图书到 Elasticsearch");
        } catch (Exception e) {
            System.err.println("初始化同步失败: " + e.getMessage());
            throw new RuntimeException("数据同步失败", e);
        }
    }
    public List<Book> searchBooksByKeyword(String keyword) {
        keyword = keyword.replaceAll("[^\\p{L}\\p{N}\\s]", " ")
               .replaceAll("\\s+", " ")
               .trim();
               
        if (bookSearchRepository != null) {
            try {
                SearchHits<Book> searchHits = bookSearchRepository.searchByKeyword(keyword);
                return searchHits.getSearchHits()
                    .stream()
                    .map(hit -> hit.getContent())
                    .collect(Collectors.toList());
            } catch (Exception e) {
                System.err.println("Elasticsearch 搜索失败，回退到数据库搜索: " + e.getMessage());
            }
        }
        // ES 未启用或失败时使用 MySQL 兜底
        return bookRepository.findByKeyword(keyword);
    }
    
    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }
    
    public Page<Book> findAllBooks(Pageable pageable) {
        return bookRepository.findAll(pageable);
    }
    
    public List<Book> findBooksBySeller(User seller) {
        return bookRepository.findBySeller(seller);
    }
    
    public List<Book> findPopularBooksByViews(int limit) {
        Pageable pageable = org.springframework.data.domain.PageRequest.of(0, limit);
        return bookRepository.findTopByViewCount(pageable);
    }
    
    public List<Book> findPopularBooksByPurchases(int limit) {
        Pageable pageable = org.springframework.data.domain.PageRequest.of(0, limit);
        return bookRepository.findTopByPurchaseCount(pageable);
    }
    
    public List<Book> findBooksByIsbn(String isbn) {
        return bookRepository.findByIsbn(isbn);
    }
}
