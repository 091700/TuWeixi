package com.example.intelligentbookplatform.service;

import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

import javax.imageio.ImageIO;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

import com.example.intelligentbookplatform.config.YOLOConfig;

import ai.djl.Model;
import ai.djl.inference.Predictor;
import ai.djl.modality.Classifications;
import ai.djl.modality.cv.Image;
import ai.djl.modality.cv.ImageFactory;
import ai.djl.modality.cv.output.BoundingBox;
import ai.djl.modality.cv.output.DetectedObjects;
import ai.djl.modality.cv.output.Rectangle;
import ai.djl.ndarray.NDArray;
import ai.djl.ndarray.NDList;
import ai.djl.ndarray.NDManager;
import ai.djl.ndarray.types.DataType;
import ai.djl.ndarray.types.Shape;
import ai.djl.translate.Batchifier;
import ai.djl.translate.Translator;
import ai.djl.translate.TranslatorContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import jakarta.annotation.PostConstruct;

@Component
public class YOLODetector {

    private static final Logger logger = LoggerFactory.getLogger(YOLODetector.class);

    private Predictor<Image, DetectedObjects> predictor;
    private final YOLOConfig config;

    @Autowired
    public YOLODetector(YOLOConfig config) {
        this.config = config;
    }

    @PostConstruct
    public void init() {
        try (InputStream modelStream = new ClassPathResource(config.getModelPath()).getInputStream()) {
            Model model = Model.newInstance("OnnxRuntime");
            model.load(modelStream);
            this.predictor = model.newPredictor(buildTranslator());
            logger.info("YOLO 模型加载成功：" + config.getModelPath());
        } catch (Exception e) {
            logger.error("YOLO 模型加载失败（视觉搜索功能不可用，应用继续启动）: " + e.getMessage());
            this.predictor = null;
        }
    }

    private Translator<Image, DetectedObjects> buildTranslator() {
        return new Translator<Image, DetectedObjects>() {
            
            @Override
public Batchifier getBatchifier() {
    return null;   // 禁用 DJL 的自动 stack，避免 Ort 不支持
}

            @Override
            public NDList processInput(TranslatorContext ctx, Image input) throws IOException {
                NDManager manager = ctx.getNDManager();

                // 1. Image -> BufferedImage
                BufferedImage bufferedImage = imageToBufferedImage(input);
                int dstSize = config.getInputSize();
                BufferedImage resized = resizeBufferedImage(bufferedImage, dstSize, dstSize);

                // 2. RGB -> CHW (byte)
                byte[] chw = new byte[3 * 640 * 640];
int[] rgb = resized.getRGB(0, 0, 640, 640, null, 0, 640);
for (int c = 0; c < 3; c++) {
    for (int h = 0; h < 640; h++) {
        for (int w = 0; w < 640; w++) {
            int pixel = rgb[h * 640 + w];
            chw[c * 640 * 640 + h * 640 + w] = (byte) ((pixel >> (16 - c * 8)) & 0xFF);
        }
    }
}

                // 3. NDArray (UINT8)
                ByteBuffer buf = ByteBuffer.wrap(chw);
                NDArray nd = manager.create(buf, new Shape(3, dstSize, dstSize), DataType.UINT8);

                int[] uint8 = new int[chw.length];
for (int i = 0; i < chw.length; i++) uint8[i] = chw[i] & 0xFF;

float[] floatData = new float[uint8.length];
for (int i = 0; i < uint8.length; i++) floatData[i] = uint8[i] / 255.0f;

NDArray floatArray = manager.create(floatData, new Shape(1, 3, 640, 640));
return new NDList(floatArray);
            }

            @Override
            public DetectedObjects processOutput(TranslatorContext ctx, NDList list) {
                NDArray output = list.singletonOrThrow();
                float[] data = output.toFloatArray();
                long[] shape = output.getShape().getShape();
                int numBoxes = (int) shape[1];
                int numParams = (int) shape[2];

                List<String> classNames = getYoloV8ClassNames();
                List<DetectedObjects.DetectedObject> detected = new ArrayList<>();

                final int bookClassIdx = 73;
                final float confTh = (float) config.getConfidenceThreshold();

                for (int i = 0; i < numBoxes; i++) {
                    int off = i * numParams;
                    float x = data[off];
                    float y = data[off + 1];
                    float w = data[off + 2];
                    float h = data[off + 3];
                    float conf = data[off + 4];
                    if (conf < confTh) continue;

                    float bookConf = data[off + 5 + bookClassIdx];
                    if (bookConf < confTh) continue;

                    Rectangle rect = new Rectangle(x - w / 2, y - h / 2, w, h);
                    detected.add(new DetectedObjects.DetectedObject("book", bookConf, rect));
                }

                return nms(detected, config.getIouThreshold());
            }

            /* ---------- 辅助 ---------- */

            private BufferedImage imageToBufferedImage(Image img) throws IOException {
                ByteArrayOutputStream bos = new ByteArrayOutputStream();
                img.save(bos, "png");
                return ImageIO.read(new ByteArrayInputStream(bos.toByteArray()));
            }

            private BufferedImage resizeBufferedImage(BufferedImage src, int w, int h) {
                BufferedImage dst = new BufferedImage(w, h, BufferedImage.TYPE_3BYTE_BGR);
                java.awt.Graphics2D g = dst.createGraphics();
                g.drawImage(src.getScaledInstance(w, h, java.awt.Image.SCALE_SMOOTH), 0, 0, null);
                g.dispose();
                return dst;
            }

            private List<String> getYoloV8ClassNames() {
                return Arrays.asList(
                        "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
                        "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
                        "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
                        "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
                        "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
                        "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
                        "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake",
                        "chair", "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop",
                        "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
                        "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush"
                );
            }

            private DetectedObjects nms(List<DetectedObjects.DetectedObject> src, double iouTh) {
                src.sort((a, b) -> Double.compare(b.getProbability(), a.getProbability()));
                List<DetectedObjects.DetectedObject> keep = new ArrayList<>();
                for (DetectedObjects.DetectedObject c : src) {
                    boolean k = true;
                    for (DetectedObjects.DetectedObject g : keep) {
                        if (iou(c.getBoundingBox().getBounds(), g.getBoundingBox().getBounds()) > iouTh) {
                            k = false;
                            break;
                        }
                    }
                    if (k) keep.add(c);
                }
                List<String> names = keep.stream().map(DetectedObjects.DetectedObject::getClassName).collect(Collectors.toList());
                List<Double> probs = keep.stream().map(DetectedObjects.DetectedObject::getProbability).collect(Collectors.toList());
                List<BoundingBox> boxes = keep.stream().map(DetectedObjects.DetectedObject::getBoundingBox).collect(Collectors.toList());
                return new DetectedObjects(names, probs, boxes);
            }

            private double iou(Rectangle a, Rectangle b) {
                double x1 = Math.max(a.getX(), b.getX());
                double y1 = Math.max(a.getY(), b.getY());
                double x2 = Math.min(a.getX() + a.getWidth(), b.getX() + b.getWidth());
                double y2 = Math.min(a.getY() + a.getHeight(), b.getY() + b.getHeight());
                double inter = Math.max(0, x2 - x1) * Math.max(0, y2 - y1);
                double union = a.getWidth() * a.getHeight() + b.getWidth() * b.getHeight() - inter;
                return union == 0 ? 0 : inter / union;
            }
        };
    }

    /* ===================== 对外接口 ===================== */

    public List<Rectangle> detectBooks(InputStream imageStream) throws IOException {
    if (predictor == null) {
        throw new RuntimeException("YOLO 模型未加载，视觉搜索功能不可用");
    }
    Image image = ImageFactory.getInstance().fromInputStream(imageStream);
    try {
        DetectedObjects detected = predictor.predict(image);
        List<Rectangle> bookBoxes = new ArrayList<>();

        for (Classifications.Classification cls : detected.items()) {
            if (!(cls instanceof DetectedObjects.DetectedObject)) {
                continue;                      // 安全跳过非检测对象
            }
            DetectedObjects.DetectedObject obj = (DetectedObjects.DetectedObject) cls;
            if ("book".equals(obj.getClassName()) && obj.getProbability() > config.getConfidenceThreshold()) {
                bookBoxes.add(obj.getBoundingBox().getBounds());
            }
        }
        return bookBoxes;
    } catch (Exception e) {
        e.printStackTrace();
        throw new RuntimeException("YOLO检测失败：" + e.getMessage(), e);
    }
}
}




