package com.example.intelligentbookplatform.service;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;

import javax.imageio.ImageIO;

import org.springframework.stereotype.Service;

import ai.djl.modality.cv.Image;
import net.sourceforge.tess4j.ITesseract;
import net.sourceforge.tess4j.Tesseract;
import net.sourceforge.tess4j.TesseractException;

@Service
public class OCRService {
    private final ITesseract tesseract;

    // 初始化Tesseract（中英文识别）
    public OCRService() {
        tesseract = new Tesseract();
        // Mac Homebrew安装的tessdata路径，若路径不对可改为自己的实际路径
        tesseract.setDatapath("/opt/homebrew/share/tessdata/");
        tesseract.setLanguage("chi_sim+eng");
    }

    // 接收DJL Image和检测框（暂不裁剪，直接识别完整图片，避免DJL版本问题）
    public String extractText(Image fullImage, ai.djl.modality.cv.output.Rectangle bookRect) throws TesseractException {
        try {
            // DJL Image转BufferedImage（Tesseract需要的格式）
            BufferedImage bufferedImage = convertDjlImageToBufferedImage(fullImage);
            // 直接识别完整图片（后续可优化裁剪，当前先保证编译）
            return tesseract.doOCR(bufferedImage).trim();
        } catch (Exception e) {
            throw new TesseractException("OCR识别失败：" + e.getMessage(), e);
        }
    }

    // DJL Image转BufferedImage（兼容DJL 0.23.0版本）
    private BufferedImage convertDjlImageToBufferedImage(Image djlImage) throws IOException {
        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        // 用DJL自带方法保存为PNG字节流
        djlImage.save(baos, "png");
        // 字节流转BufferedImage
        return ImageIO.read(new ByteArrayInputStream(baos.toByteArray()));
    }
}