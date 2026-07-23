package com.example.intelligentbookplatform.dto;

import com.example.intelligentbookplatform.model.Book;

public class SearchResult {
    private Book book;
    private String highlightedTitle;
    private String highlightedAuthor;
    private String highlightedDescription;

    public SearchResult() {}

    public SearchResult(Book book, String highlightedTitle, String highlightedAuthor, String highlightedDescription) {
        this.book = book;
        this.highlightedTitle = highlightedTitle;
        this.highlightedAuthor = highlightedAuthor;
        this.highlightedDescription = highlightedDescription;
    }

    public Book getBook() { 
        return book; 
    }
    
    public void setBook(Book book) { 
        this.book = book; 
    }

    public String getHighlightedTitle() { 
        return highlightedTitle != null ? highlightedTitle : (book != null ? book.getTitle() : ""); 
    }
    
    public void setHighlightedTitle(String highlightedTitle) { 
        this.highlightedTitle = highlightedTitle; 
    }

    public String getHighlightedAuthor() { 
        return highlightedAuthor != null ? highlightedAuthor : (book != null ? book.getAuthor() : ""); 
    }
    
    public void setHighlightedAuthor(String highlightedAuthor) { 
        this.highlightedAuthor = highlightedAuthor; 
    }

    public String getHighlightedDescription() { 
        return highlightedDescription != null ? highlightedDescription :
               (book != null && book.getDescription() != null ? book.getDescription() : ""); 
    }
    
    public void setHighlightedDescription(String highlightedDescription) {
        this.highlightedDescription = highlightedDescription;
    }
}