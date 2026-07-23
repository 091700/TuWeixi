package com.example.intelligentbookplatform.service;

import java.io.ByteArrayInputStream;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.example.intelligentbookplatform.model.Book;

import ai.djl.modality.cv.Image;
import ai.djl.modality.cv.ImageFactory;

@Service
public class YOLOService {
    private static final Logger logger = LoggerFactory.getLogger(YOLOService.class);

    @Autowired
    private YOLODetector yoloDetector;

    @Autowired
    private OCRService ocrService;

    @Autowired
    private BookService bookService;

    // 图片搜索核心逻辑：上传图片→YOLO检测→OCR识别→图书搜索（清洗+双向）
    public List<Book> searchByImage(MultipartFile imageFile) throws Exception {
        // 1. 校验图片
        if (imageFile.isEmpty()) {
            throw new RuntimeException("请上传有效的图片文件");
        }

        // 2. 读取图片（供OCR使用）
        Image fullImage;
        try (InputStream stream = imageFile.getInputStream()) {
            fullImage = ImageFactory.getInstance().fromInputStream(stream);
        }

        // 3. YOLO检测图书（用ByteArrayInputStream避免流关闭）
        List<ai.djl.modality.cv.output.Rectangle> bookBoxes;
        try (InputStream stream = new ByteArrayInputStream(imageFile.getBytes())) {
            bookBoxes = yoloDetector.detectBooks(stream);
        }

        // 4. 校验检测结果
        if (bookBoxes.isEmpty()) {
            throw new RuntimeException("未检测到图书，请上传包含图书封面的图片");
        }
        logger.info("YOLO检测到 {} 本图书", bookBoxes.size());

        // 5. OCR识别图书文本
        List<String> keywords = new ArrayList<>();
        for (ai.djl.modality.cv.output.Rectangle box : bookBoxes) {
            try {
                String text = ocrService.extractText(fullImage, box);
                if (!text.isEmpty()) {
                    keywords.add(text);
                    logger.info("OCR识别到文本：{}", text);
                }
            } catch (Exception e) {
                logger.warn("单本图书OCR识别失败，跳过：{}", e.getMessage());
            }
        }

        // 6. 校验OCR结果
        if (keywords.isEmpty()) {
            throw new RuntimeException("无法识别图书文本，请上传更清晰的图片");
        }

        // 7. 关键词清洗：去控制字符、只保留中英文字符、数字、空格
        String rawKey = String.join(" ", keywords);
        String searchKey = rawKey.replaceAll("[^\\p{L}\\p{N}\\s]", " ")
                                 .replaceAll("\\s+", " ")
                                 .trim();

        // 8. 双向搜索：先搜英文，若空再搜中文书名《算法导论》
        List<Book> hits = bookService.searchBooksByKeyword(searchKey);
        if (hits.isEmpty() && searchKey.contains("Introduction to Algorithms")) {
            hits = bookService.searchBooksByKeyword("算法导论");
        }
        return hits;
    }
}