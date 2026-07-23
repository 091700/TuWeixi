#!/usr/bin/env python3
"""
YOLO 模型导出脚本
将 YOLOv8 模型导出为 ONNX 格式，供 Java 程序使用
"""

from ultralytics import YOLO
import os

def export_yolo_model():
    print("开始导出 YOLO 模型...")
    
    # 1. 加载预训练模型
    print("正在加载 YOLOv8n 模型...")
    model = YOLO('yolov8n.pt')  # 这会自动下载模型如果本地不存在
    
    # 2. 导出为 ONNX 格式
    print("正在导出为 ONNX 格式...")
    
    # 导出配置
    export_config = {
        'format': 'onnx',
        'dynamic': False,      # 静态批量大小，便于优化
        'simplify': True,     # 简化模型
        'opset': 12,          # ONNX 算子集版本
        'imgsz': 640          # 输入图像尺寸
    }
    
    # 执行导出
    success = model.export(**export_config)
    
    if success:
        # 找到导出的文件
        onnx_file = 'yolov8n.onnx'
        if os.path.exists(onnx_file):
            print(f"✅ 模型导出成功: {onnx_file}")
            print(f"文件大小: {os.path.getsize(onnx_file) / (1024*1024):.2f} MB")
            
            # 创建项目中的目标目录
            target_dir = '../src/main/resources/models/'
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制到项目目录
            import shutil
            shutil.copy(onnx_file, target_dir)
            print(f"✅ 模型已复制到: {target_dir}")
        else:
            print("❌ 导出文件未找到")
    else:
        print("❌ 模型导出失败")

def test_model_loading():
    """测试 ONNX 模型是否能正常加载"""
    try:
        import onnxruntime as ort
        print("\n测试 ONNX 模型加载...")
        
        # 创建推理会话
        session = ort.InferenceSession('yolov8n.onnx')
        
        # 获取输入输出信息
        inputs = session.get_inputs()
        outputs = session.get_outputs()
        
        print(f"✅ 模型加载成功")
        print(f"输入名称: {[input.name for input in inputs]}")
        print(f"输入形状: {[input.shape for input in inputs]}")
        print(f"输出名称: {[output.name for output in outputs]}")
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")

if __name__ == "__main__":
    print("YOLO 模型导出工具")
    print("=" * 50)
    
    export_yolo_model()
    test_model_loading()
    
    print("\n🎉 导出完成！")