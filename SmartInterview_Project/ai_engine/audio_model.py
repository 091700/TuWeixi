import librosa
import numpy as np
import logging

# 配置日志基础参数
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def score_audio(audio_path, recognized_text=""):
    """
    音频评分函数：计算紧张度、自信度、清晰度三个声学指标
    """
    try:
        # 加载音频文件，固定采样率16000
        y, sr = librosa.load(audio_path, sr=16000)
        
        # 语音活动检测，切除静音片段，保留有效语音
        intervals = librosa.effects.split(y, top_db=25)
        if len(intervals) == 0:
            return {"nervousness": 95.0, "confidence": 30.0, "clarity": 20.0}
            
        # 拼接有效语音片段
        y_speech = np.concatenate([y[start:end] for start, end in intervals])
        # 计算总时长和有效语音时长
        total_duration = librosa.get_duration(y=y, sr=sr)
        speech_duration = librosa.get_duration(y=y_speech, sr=sr)
        
        # 有效语音过短，直接返回默认评分
        if speech_duration < 0.8:
            return {"nervousness": 85.0, "confidence": 30.0, "clarity": 20.0}

        # 计算核心声学特征
        pause_ratio = (total_duration - speech_duration) / total_duration  # 停顿比例
        rms = librosa.feature.rms(y=y_speech)[0]
        mean_rms = np.mean(rms)  # 平均音量
        
        # 基频（音高）计算，排除无效值
        f0, _, _ = librosa.pyin(y_speech, fmin=50, fmax=300)
        valid_f0 = f0[~np.isnan(f0)]
        f0_std = np.std(valid_f0) if len(valid_f0) > 5 else 0  # 音高波动
        
        rolloff = np.mean(librosa.feature.spectral_rolloff(y=y_speech, sr=sr, roll_percent=0.85))  # 频谱滚降
        
        # 计算语速（剔除标点后的字符数/有效语音时长）
        char_count = len(recognized_text.strip().replace("，", "").replace("。", "").replace("？", ""))
        speaking_rate = char_count / speech_duration if speech_duration > 0 else 0

        # 计算清晰度评分
        clarity_base = 30 + (rolloff / 5000) * 35 
        if 2.0 <= speaking_rate <= 5.5:
            clarity_base += 30  
        elif 1.0 <= speaking_rate < 2.0:
            clarity_base += 10  
        else:
            clarity_base -= 20  
        clarity = np.clip(clarity_base, 20, 95)

        # 计算紧张度评分
        nervousness_base = 30 + (pause_ratio * 120) 
        if speaking_rate > 6.0:  
            nervousness_base += 20  
        if f0_std > 25:
            nervousness_base += 15  
        nervousness = np.clip(nervousness_base, 30, 95)

        # 计算自信度评分
        confidence_base = np.interp(mean_rms, [0.01, 0.15], [40, 80])
        if 8 < f0_std < 25:
            confidence_base += 15  
        elif f0_std <= 5:
            confidence_base -= 20  
        confidence = np.clip(confidence_base, 20, 95)

        # 打印声学特征日志
        logger.info(f"[声学引擎] 滚降频:{rolloff:.0f}Hz, 停顿比:{pause_ratio:.2f}, F0波动:{f0_std:.1f}, 吐字率:{speaking_rate:.1f}字/秒, 能量均值:{mean_rms:.3f}")

        # 返回保留两位小数的评分结果
        return {
            "nervousness": round(float(nervousness), 2),
            "confidence": round(float(confidence), 2),
            "clarity": round(float(clarity), 2)
        }
    except Exception as e:
        # 异常捕获，返回默认评分并打印错误日志
        logger.error(f"物理特征提取失败: {e}")
        return {"nervousness": 80.0, "confidence": 40.0, "clarity": 40.0}