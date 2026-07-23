package com.example.intelligentbookplatform.config;

import org.springframework.context.annotation.Configuration;

@Configuration
public class YOLOConfig {
    // 模型路径：resources/models/yolov8n.onnx
    private final String modelPath = "models/yolov8n.onnx";
    
    // 置信度阈值（过滤低置信度结果）
    private final double confidenceThreshold = 0.5;
    
    // 非极大值抑制阈值（去除重复框）
    private final double iouThreshold = 0.4;
    
    // 输入图像尺寸（YOLOv8 标准尺寸）
    private final int inputSize = 640;

    // Getter 方法（必须提供，用于其他类获取配置）
    public String getModelPath() {
        return modelPath;
    }
    public double getConfidenceThreshold() {
        return confidenceThreshold;
    }
    public double getIouThreshold() {
        return iouThreshold;
    }
    public int getInputSize() {
        return inputSize;
    }
}