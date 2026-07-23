import os
import sys
venv_path = os.path.join(os.getcwd(), "venv", "Lib", "site-packages")
nvidia_paths = [
    os.path.join(venv_path, "nvidia", "cublas", "bin"),
    os.path.join(venv_path, "nvidia", "cudnn", "bin"),
]

for path in nvidia_paths:
    if os.path.exists(path):
        os.add_dll_directory(path)
        # 为了保险，同时加入环境变量
        os.environ["PATH"] = path + os.pathsep + os.environ["PATH"]
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import shutil

os.environ["CHROMA_TELEMETRY_DISABLED"] = "1"
import logging
from audio_model import score_audio
from rag_engine import rag_system
from pydub import AudioSegment
from pydantic import BaseModel
from tts_engine import tts_system
from fastapi.middleware.cors import CORSMiddleware
import uuid
from fastapi.staticfiles import StaticFiles
from faster_whisper import WhisperModel
os.environ["CHROMA_TELEMETRY_DISABLED"] = "1"

# 全局日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("正在加载 Faster-Whisper 引擎 (GPU 加速版)...")
model = WhisperModel("small", device="cuda", compute_type="float16")

# 初始化FastAPI应用
app = FastAPI(title="AI Interview Core Engine")

# 配置跨域中间件，允许所有请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建临时音频存储目录
os.makedirs("temp_audio", exist_ok=True)

# TTS请求参数模型
class TTSRequest(BaseModel):
    text: str
    voice: str = "BV007_streaming" 

# TTS语音合成接口
@app.post("/api/tts/generate")
async def generate_tts(req: TTSRequest):
    try:
        # 调用TTS引擎生成音频base64
        audio_base64 = tts_system.generate_audio_base64(req.text, req.voice)
        if audio_base64:
            return {"status": "success", "data": {"audio_base64": audio_base64}}
        else:
            raise HTTPException(status_code=500, detail="语音合成失败，请检查控制台日志")
    except Exception as e:
        logger.error(f"TTS 接口报错: {str(e)}")
        raise HTTPException(status_code=500, detail="TTS 服务异常")

# 重复创建临时目录（保留原代码，不做修改）
os.makedirs("temp_audio", exist_ok=True)
# 创建永久音频存储目录
os.makedirs("static/audio", exist_ok=True)
# 挂载静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 音频分析接口：语音识别+声学评分+文件归档
@app.post("/api/analyze/audio")
async def analyze_audio(audio_file: UploadFile = File(...)):
    file_uuid = str(uuid.uuid4())
    file_path = f"temp_audio/{file_uuid}.webm"
    wav_path = f"temp_audio/{file_uuid}.wav"
    
    try:
        # 保存上传的音频文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
        
        # 转换webm格式为wav
        audio = AudioSegment.from_file(file_path, format="webm")
        audio.export(wav_path, format="wav")
        
        # 语音识别
        segments, info = model.transcribe(wav_path, beam_size=5, language="zh")
        text = "".join([segment.text for segment in segments])

        if not text.strip():
            text = "（未能识别出有效语音）"
        
        # 声学特征评分
        scores = score_audio(wav_path, text)
        
        # 生成唯一标识，归档音频文件
        file_uuid = str(uuid.uuid4())
        save_path = f"static/audio/{file_uuid}.wav"
        shutil.copy(wav_path, save_path)
        audio_url = f"http://localhost:8000/static/audio/{file_uuid}.wav"
        
        logger.info(f"录音分析完成，得分: {scores}，识别文字: {text}，已归档至: {save_path}")

        return {
            "status": "success", 
            "data": {
                "scores": scores, 
                "text": text,
                "audio_url": audio_url
            }
        }
        
    finally:
        # 清理临时文件
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

# 内容分析接口：基于RAG获取参考答案
@app.post("/api/analyze/content")
async def analyze_content(question: str = Form(...), user_answer: str = Form(...), job_role: str = Form(...)):
    try:
        # 通过RAG系统检索标准参考答案
        standard_reference = rag_system.retrieve_standard_answer(question, job_role)
        return {
            "status": "success",
            "data": {
                "user_answer": user_answer,
                "rag_reference": standard_reference,
                "instruction": f"请依据上述参考知识，评判该名【{job_role}】面试者的回答。"
            }
        }
    except Exception as e:
        logger.error(f"内容处理流报错: {str(e)}")
        raise HTTPException(status_code=500, detail="内容生成接口异常")

# 随机面试题获取接口
@app.get("/api/question/random")
async def get_random_question(job_role: str, difficulty: str = "medium"):
    question = rag_system.get_random_question(job_role, difficulty)
    return {"status": "success", "data": question}

# 启动服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)