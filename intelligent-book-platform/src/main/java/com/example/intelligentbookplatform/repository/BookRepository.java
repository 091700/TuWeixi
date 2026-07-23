package com.example.intelligentbookplatform.repository;

import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.example.intelligentbookplatform.model.Book;
import com.example.intelligentbookplatform.model.User;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {
    Page<Book> findAll(Pageable pageable);
    List<Book> findBySeller(User seller);
    
    @Query("SELECT b FROM Book b ORDER BY b.viewCount DESC")
    List<Book> findTopByViewCount(Pageable pageable);
    
    @Query("SELECT b FROM Book b ORDER BY b.purchaseCount DESC")
    List<Book> findTopByPurchaseCount(Pageable pageable);
    
    @Query("SELECT b FROM Book b WHERE b.title LIKE %:keyword% OR b.author LIKE %:keyword% OR b.description LIKE %:keyword%")
    List<Book> findByKeyword(@Param("keyword") String keyword);
    
    List<Book> findByIsbn(String isbn);
}