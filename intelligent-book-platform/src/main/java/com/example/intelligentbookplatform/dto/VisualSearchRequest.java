package com.example.intelligentbookplatform.dto;

import org.springframework.web.multipart.MultipartFile;

public class VisualSearchRequest {
    private MultipartFile image;
    private String searchType;
    public VisualSearchRequest() {}
    
    public VisualSearchRequest(MultipartFile image, String searchType) {
        this.image = image;
        this.searchType = searchType;
    }
    
    public MultipartFile getImage() {
        return image;
    }
    
    public void setImage(MultipartFile image) {
        this.image = image;
    }
    
    public String getSearchType() {
        return searchType;
    }
    
    public void setSearchType(String searchType) {
        this.searchType = searchType;
    }
}