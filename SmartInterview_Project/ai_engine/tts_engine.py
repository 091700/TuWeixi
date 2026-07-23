import requests
import uuid
import logging

logger = logging.getLogger(__name__)

class VolcengineTTS:
    def __init__(self, appid: str, access_token: str):
        # 初始化TTS配置参数
        self.appid = appid
        self.access_token = access_token
        self.cluster = "volcano_tts"
        self.api_url = "https://openspeech.bytedance.com/api/v1/tts"

    def generate_audio_base64(self, text: str, voice_type: str = "BV007_streaming") -> str:
        # 设置请求头
        headers = {
            "Authorization": f"Bearer;{self.access_token}",
            "Content-Type": "application/json"
        }
        
        # 构造TTS请求参数
        request_json = {
            "app": {
                "appid": self.appid,
                "token": self.access_token,
                "cluster": self.cluster
            },
            "user": {
                "uid": "interview_candidate"
            },
            "audio": {
                "voice_type": voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson"
            }
        }

        try:
            # 发送TTS合成请求
            response = requests.post(self.api_url, json=request_json, headers=headers, timeout=5)
            if response.status_code == 200:
                resp_data = response.json()
                if resp_data.get("code") == 3000:
                    # 返回音频base64数据
                    return resp_data.get("data")
                else:
                    logger.error(f"火山TTS业务报错: {resp_data.get('message')}")
            else:
                logger.error(f"火山TTS网络报错: HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"火山TTS请求异常: {str(e)}")
            
        return None

# 实例化TTS系统
tts_system = VolcengineTTS(
    appid="7862589233",
    access_token="gi2cg5ao72zJghimUbIxBr6Ujdo8MmTD"
)