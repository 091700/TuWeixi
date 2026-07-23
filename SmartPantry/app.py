from fastapi import FastAPI
from pydantic import BaseModel
import torch
import torch.nn as nn
from typing import List
import json
import logging
import os
from transformers import AutoModelForCausalLM, AutoTokenizer

# ===================== 前置：彻底禁用嵌套张量，从环境层面避坑 =====================
import warnings
warnings.filterwarnings("ignore")
os.environ["PYTORCH_ENABLE_NUMPY_COMPATIBILITY"] = "1"


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 锁死CPU，避免设备不一致
device = torch.device("cpu")
torch.set_num_threads(4)
torch.set_default_dtype(torch.float32)
logger.info("🚀 核心引擎启动！当前设备: CPU 稳定模式，已禁用嵌套张量优化")

# ===================== 1. LLM与动态知识库加载 =====================
logger.info("⏳ 加载本地 LLM...")
tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-1.5B-Instruct")
llm_model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-1.5B-Instruct", 
    torch_dtype=torch.float32, 
    device_map="cpu",
    low_cpu_mem_usage=True
)
logger.info("✅ LLM 加载完成")

# 风味缓存管理
CACHE_FILE = "flavor_cache.json"
def load_flavor_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_flavor_cache(cache):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
def get_all_ingredients_from_db():
    try:
        # ========== 替换成你的数据库配置 ==========
        import pymysql
        DB_CONFIG = {
            "host": "localhost",       # 你的数据库IP（本地填localhost）
            "user": "root",            # 你的数据库用户名
            "password": "091700xixi", # 替换成实际密码
            "db": "smart_pantry",       # 你的数据库名
            "charset": "utf8mb4"       # 字符集（避免中文乱码）
        }
        # =========================================
        
        # 建立数据库连接
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM ingredient_dict")
        
        # 提取所有食材名称
        ingredients = [row[0].strip() for row in cursor.fetchall() if row[0]]
        cursor.close()
        conn.close()
        logger.info(f"✅ 从数据库获取到 {len(ingredients)} 种食材")
        return ingredients
    except ImportError:
        logger.error("❌ 缺少pymysql库，请执行：pip install pymysql")
        return []
    except Exception as e:
        logger.error(f"❌ 查询数据库失败：{str(e)}", exc_info=True)
        return []

# 2. 自动补全缺失食材的特征（调用LLM生成）
def auto_complete_ingredient_features():
    global flavor_cache
    # 获取数据库中的所有食材
    db_ingredients = get_all_ingredients_from_db()
    if not db_ingredients:
        logger.warning("⚠️ 未获取到数据库食材，跳过自动补全")
        return
    
    # 遍历数据库食材，补全缺失的特征
    for ing_name in db_ingredients:
        # 跳过已存在的食材（基础库/缓存中已有）
        if ing_name in BASE_FOOD_FALLBACK or ing_name in flavor_cache:
            continue
        
        logger.info(f"🔍 自动补全缺失食材：{ing_name}")
        try:
            # 调用LLM提取特征（复用现有接口逻辑）
            prompt = f"""分析食材【{ing_name}】。
1. 类别只能是(蔬菜,肉禽,水果,海鲜,豆制品,加工食品,调料,主食,其他)。
2. 保鲜天数(整数)。
3. 口味特征：甜度、咸度、酸度、辣度、异味或刺激度。这5个指标每个给出一个0-10的整数评估。如果不能吃或者极度恶心，异味度给10。
严格只输出JSON，无任何额外文字：{{"category": "类别", "base_shelf_life": 天数, "flavor": [甜, 咸, 酸, 辣, 异]}}"""
            
            messages = [
                {"role": "system", "content": "你是一个严谨的食品生化分析AI，仅输出符合格式的JSON。"}, 
                {"role": "user", "content": prompt}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            model_inputs = tokenizer([text], return_tensors="pt").to(device)
            
            with torch.no_grad():
                generated_ids = llm_model.generate(
                    model_inputs.input_ids, 
                    max_new_tokens=100,
                    temperature=0.01,
                    do_sample=False,
                    pad_token_id=tokenizer.eos_token_id
                )
                generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
            
            response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
            
            # 解析LLM返回的JSON
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError(f"LLM返回非JSON格式：{response_text}")
            data = json.loads(json_match.group())
            
            # 处理风味特征
            flavor_vec = data.get("flavor", [0,0,0,0,0])
            flavor_vec = [max(0, min(10, int(x))) for x in flavor_vec] if isinstance(flavor_vec, list) else [0,0,0,0,0]
            if len(flavor_vec) != 5:
                flavor_vec = [0,0,0,0,0]
            
            # 处理类别（映射到数字）
            cat_map = {
                "蔬菜":1, "肉禽":2, "水果":3, "海鲜":4, 
                "豆制品":5, "加工食品":6, "调料":7, "主食":8, "其他":9
            }
            cat_id = cat_map.get(data.get("category", "其他"), 9)
            
            # 生成唯一ID（避免和基础库冲突）
            new_id = len(flavor_cache) + 200  # 基础库ID到19，从200开始
            
            # 写入缓存
            flavor_cache[ing_name] = {
                "id": new_id,
                "cat": cat_id,
                "flavor": flavor_vec
            }
            logger.info(f"✅ 补全{ing_name}特征：{flavor_vec}")
        
        except Exception as e:
            logger.error(f"❌ 补全{ing_name}特征失败：{str(e)}")
            # 兜底：给默认特征
            flavor_cache[ing_name] = {
                "id": len(flavor_cache) + 200,
                "cat": 9,
                "flavor": [1,1,0,0,2]
            }
    
    # 保存更新后的缓存到JSON文件
    save_flavor_cache(flavor_cache)
    logger.info(f"✅ 自动补全完成，缓存总数：{len(flavor_cache)}")


flavor_cache = load_flavor_cache()
# 【强制对齐】和训练代码完全一致的基础食材库，ID、cat、flavor丝毫不差
BASE_FOOD_FALLBACK = {
    "西红柿": {"id": 1, "cat": 1, "flavor": [4, 1, 5, 0, 0]},
    "白菜": {"id": 2, "cat": 1, "flavor": [2, 0, 0, 0, 0]},
    "猪肉": {"id": 3, "cat": 2, "flavor": [1, 3, 0, 0, 1]},
    "鸡蛋": {"id": 4, "cat": 2, "flavor": [1, 2, 0, 0, 1]},
    "西瓜": {"id": 5, "cat": 3, "flavor": [8, 0, 0, 0, 0]},
    "榴莲": {"id": 6, "cat": 3, "flavor": [7, 0, 0, 0, 8]},
    "鱼肉": {"id": 7, "cat": 4, "flavor": [1, 3, 0, 0, 4]},
    "豆腐": {"id": 8, "cat": 5, "flavor": [1, 1, 0, 0, 0]},
    "皮蛋": {"id": 9, "cat": 6, "flavor": [0, 5, 0, 0, 7]},
    "鲱鱼罐头": {"id":10, "cat": 6, "flavor": [0, 9, 2, 0, 10]},
    "辣椒": {"id": 11, "cat": 7, "flavor": [0, 1, 0, 9, 2]},
    "大米": {"id": 12, "cat": 8, "flavor": [3, 0, 0, 0, 0]},
    "黑面包": {"id":13, "cat": 8, "flavor": [2, 2, 3, 0, 1]},
    "牛肉": {"id":14, "cat":2, "flavor": [1,4,0,0,2]},
    "黄瓜": {"id":15, "cat":1, "flavor": [3,0,2,0,0]},
    "青豆": {"id":16, "cat":1, "flavor": [2,1,0,0,0]},
    "鸡肉": {"id":17, "cat":2, "flavor": [1,2,0,0,1]},
    "哈密瓜": {"id":18, "cat":3, "flavor": [7,0,1,0,0]},
    "火龙果": {"id":19, "cat":3, "flavor": [8,0,2,0,0]}
}
# 合并兜底数据
for k, v in BASE_FOOD_FALLBACK.items():
    if k not in flavor_cache:
        flavor_cache[k] = v
save_flavor_cache(flavor_cache)
# ===================== 新增：启动自动补全 =====================
logger.info("🔄 开始自动同步数据库食材特征...")
auto_complete_ingredient_features()
logger.info(f"✅ 风味知识库加载完成，共 {len(flavor_cache)} 种食材")

# ===================== 2. 神经网络定义【和训练代码100%完全对齐，彻底避坑】 =====================
class ZeroShotFreshnessNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.cat_embedding = nn.Embedding(10, 8) 
        self.fc = nn.Sequential(
            nn.Linear(12, 64), nn.ReLU(), nn.Dropout(0.2),
            nn.Linear(64, 32), nn.ReLU(), nn.Linear(32, 1)
        )
    def forward(self, x):
        cat_ids = x[:, 0].long()
        num_features = x[:, 1:]
        embedded = self.cat_embedding(cat_ids)
        combined = torch.cat((embedded, num_features), dim=1)
        return self.fc(combined)

# 【核心修复】彻底移除src_key_padding_mask，从根源解决CPU维度报错，训练推理完全对齐
class TrueZeroShotNexus(nn.Module):
    def __init__(self, vocab_size=5000, num_cats=15, embed_dim=64):
        super().__init__()
        self.name_emb = nn.Embedding(vocab_size, embed_dim // 4, padding_idx=0)
        self.cat_emb = nn.Embedding(num_cats, embed_dim // 4, padding_idx=0)
        self.flavor_proj = nn.Linear(5, embed_dim // 2) 
        self.pos_enc = nn.Parameter(torch.randn(1, 5, embed_dim))
        
        # 和训练代码完全一致的Transformer配置
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, 
            nhead=4, 
            dim_feedforward=512, 
            dropout=0.1, 
            batch_first=True,
            activation="gelu"
        )
        # 训练代码是3层，这里必须也是3层！
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=3, enable_nested_tensor=False)
        
        # 和训练代码完全一致的MLP结构，层数、维度丝毫不差
        self.mlp = nn.Sequential(
            nn.Linear(embed_dim, 256), nn.GELU(), nn.Dropout(0.2),
            nn.Linear(256, 128), nn.GELU(), nn.Dropout(0.2),
            nn.Linear(128, 64), nn.GELU(),
            nn.Linear(64, 1), nn.Sigmoid()
        )

    def forward(self, n_x, c_x, f_x):
        batch_size, seq_len = n_x.shape
        # 1. 特征融合，padding_idx=0的位置embedding自动为0
        n_e = self.name_emb(n_x)
        c_e = self.cat_emb(c_x)
        f_e = self.flavor_proj(f_x)
        
        # 2. 拼接+位置编码，shape永远是 [batch, 5, 64]
        emb = torch.cat([n_e, c_e, f_e], dim=-1) + self.pos_enc
        
        # 3. 【核心避坑】彻底移除src_key_padding_mask，关闭嵌套张量，Transformer输出shape永远固定[batch,5,64]
        attended = self.transformer(emb)
        
        # 4. 池化逻辑：只对有效非padding的位置做平均，和训练完全一致
        mask = (n_x == 0)  # [batch, 5]，padding位置为True
        valid_mask = (~mask).float().unsqueeze(-1)  # [batch, 5, 1]，有效位置为1
        pooled = (attended * valid_mask).sum(dim=1) / valid_mask.sum(dim=1).clamp(min=1e-6)
        
        return self.mlp(pooled)

# ===================== 模型加载 =====================
model1 = ZeroShotFreshnessNet().to(device)
try:
    model1.load_state_dict(torch.load("ai1_zeroshot_freshness.pth", map_location=device, weights_only=True))
    model1.eval()
    logger.info("✅ AI-1 保鲜预测模型加载成功")
except Exception as e:
    logger.warning(f"⚠️ AI-1 权重加载失败: {e}")

# 【修复】严格加载权重，加载失败直接明确日志，不会用随机模型
model2 = TrueZeroShotNexus().to(device)
model_load_success = False
try:
    state_dict = torch.load("ai2_true_zeroshot.pth", map_location=device, weights_only=True)
    model2.load_state_dict(state_dict, strict=True)  # strict=True严格校验，不允许参数缺失
    model2.eval()
    model_load_success = True
    logger.info("✅ AI-2 味觉和谐度模型加载成功！")
except Exception as e:
    logger.error(f"❌ AI-2 权重加载失败，将使用纯规则打分: {e}", exc_info=True)
    model_load_success = False

app = FastAPI(title="SmartPantry NEXUS Engine")

# ===================== 3. API 路由定义 =====================
class ExtractRequest(BaseModel): 
    ingredient_name: str
class FreshnessRequest(BaseModel): 
    cat_id: int = 8
    base_shelf_life: float = 3.0
    storage_type: int
    temp: float
    initial_status: int
class IngredientItem(BaseModel): 
    name: str
    category: str
class HarmonyRequest(BaseModel): 
    ingredients: List[IngredientItem]

# 食材特征提取接口
@app.post("/api/ai/extract_features")
def extract_features(req: ExtractRequest):
    prompt = f"""分析食材【{req.ingredient_name}】。
1. 类别只能是(蔬菜,肉禽,水果,海鲜,豆制品,加工食品,调料,主食,其他)。
2. 保鲜天数(整数)。
3. 口味特征：甜度、咸度、酸度、辣度、异味或刺激度。这5个指标每个给出一个0-10的整数评估。如果不能吃或者极度恶心，异味度给10。
严格只输出JSON，无任何额外文字：{{"category": "类别", "base_shelf_life": 天数, "flavor": [甜, 咸, 酸, 辣, 异]}}"""
    
    messages = [
        {"role": "system", "content": "你是一个严谨的食品生化分析AI，仅输出符合格式的JSON。"}, 
        {"role": "user", "content": prompt}
    ]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    model_inputs = tokenizer([text], return_tensors="pt").to(device)
    
    with torch.no_grad():
        generated_ids = llm_model.generate(
            model_inputs.input_ids, 
            max_new_tokens=100,
            temperature=0.01,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)]
    
    response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    
    try:
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            raise ValueError("LLM未返回JSON格式内容")
        data = json.loads(json_match.group())
        
        flavor_vec = data.get("flavor", [0, 0, 0, 0, 0])
        if not isinstance(flavor_vec, list) or len(flavor_vec) !=5:
            flavor_vec = [0,0,0,0,0]
        flavor_vec = [max(0, min(10, int(x))) for x in flavor_vec]
        
        global flavor_cache
        if req.ingredient_name not in flavor_cache:
            new_id = len(flavor_cache) + 100 
            flavor_cache[req.ingredient_name] = {
                "id": new_id, 
                "cat": 9, 
                "flavor": flavor_vec
            }
            save_flavor_cache(flavor_cache)
        logger.info(f"👽 新食材特征入库: {req.ingredient_name} -> {flavor_vec}")
        
        return {"status": "success", "data": data}
    except Exception as e:
        logger.error(f"LLM 解析失败: {e}, 原始响应: {response_text}")
        return {"status": "success", "data": {"category": "其他", "base_shelf_life": 3, "flavor": [0,0,0,0,0]}}

# 保鲜天数预测接口
@app.post("/api/ai/predict_freshness")
def predict_freshness(req: FreshnessRequest):
    input_data = [[
        float(req.cat_id), 
        float(req.base_shelf_life), 
        float(req.storage_type), 
        float(req.temp), 
        float(req.initial_status)
    ]]
    with torch.no_grad():
        predicted_days = model1(torch.tensor(input_data, dtype=torch.float32).to(device)).item()
    return {"status": "success", "predicted_days": round(predicted_days, 1)}

@app.post("/api/ai/predict_harmony")
def predict_harmony(req: HarmonyRequest):
    logger.info(f"收到食材组合: {req.ingredients}")
    cat_map = {
        "蔬菜": 1, "肉类": 2, "肉禽": 2, "水果": 3, 
        "海鲜": 4, "豆制品": 5, "加工食品": 6, 
        "调料": 7, "主食": 8, "其他":9
    }
    n_ids, c_ids, f_vecs, valid_names, valid_cats = [], [], [], [], []
    
    # 违禁词直接判0分
    forbidden_words = ["屎", "粪", "毒", "垃圾", "塑料"]
    for item in req.ingredients:
        if any(bad_word in item.name for bad_word in forbidden_words):
            logger.warning(f"检测到违禁食材: {item.name}，直接返回0分")
            return {"status": "success", "harmony_score": 0.0}
    
    # 优先从基础库取，保证ID和训练对齐
    global flavor_cache
    for item in req.ingredients:
        if item.name in BASE_FOOD_FALLBACK:
            info = BASE_FOOD_FALLBACK[item.name]
            n_ids.append(info["id"])
            cat_id = cat_map.get(item.category, info.get("cat", 9))
            c_ids.append(cat_id)
            f_vecs.append(info["flavor"])
            valid_names.append(item.name)
            valid_cats.append(cat_id)
        elif item.name in flavor_cache:
            info = flavor_cache[item.name]
            cat_id = cat_map.get(item.category, info.get("cat", 9))
            n_ids.append(info["id"])
            c_ids.append(cat_id)
            f_vecs.append(info["flavor"])
            valid_names.append(item.name)
            valid_cats.append(cat_id)
        else:
            logger.warning(f"未知食材【{item.name}】，尝试自动补全特征...")
            try:
                prompt = f"""分析食材【{item.name}】。
1. 口味特征：甜度、咸度、酸度、辣度、异味或刺激度。这5个指标每个给出一个0-10的整数评估。
严格只输出JSON，无任何额外文字：{{"flavor": [甜, 咸, 酸, 辣, 异]}}"""
                messages = [
                    {"role": "system", "content": "仅输出JSON，无其他文字"},
                    {"role": "user", "content": prompt}
                ]
                text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                model_inputs = tokenizer([text], return_tensors="pt").to(device)
                with torch.no_grad():
                    generated_ids = llm_model.generate(
                        model_inputs.input_ids, max_new_tokens=50, temperature=0.01, do_sample=False
                    )
                response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                data = json.loads(json_match.group()) if json_match else {}
                flavor_vec = data.get("flavor", [1,1,0,0,2])
                flavor_vec = [max(0, min(10, int(x))) for x in flavor_vec] if isinstance(flavor_vec, list) else [1,1,0,0,2]
                if len(flavor_vec) != 5:
                    flavor_vec = [1,1,0,0,2]
            except:
                flavor_vec = [1,1,0,0,2]
            cat_id = cat_map.get(item.category, 9)
            n_ids.append(4999)
            c_ids.append(cat_id)
            f_vecs.append(flavor_vec)
            valid_names.append(item.name)
            valid_cats.append(cat_id)

    # 强制固定长度为5，和训练完全一致
    max_seq_len = 5
    n_ids = n_ids[:max_seq_len] + [0] * (max_seq_len - len(n_ids))
    c_ids = c_ids[:max_seq_len] + [0] * (max_seq_len - len(c_ids))
    f_vecs = f_vecs[:max_seq_len] + [[0,0,0,0,0]] * (max_seq_len - len(f_vecs))
    
    logger.info(f"输入张量: n_ids={n_ids}, c_ids={c_ids}, f_vecs={f_vecs}")
    
    # ========== 修复1：把规则打分函数移到前面，且改为内部函数（正确传参） ==========
    def rule_based_score(valid_names, f_vecs, valid_cats):
        if len(valid_names) <= 1:
            return 70.0
        flavors = [f[:5] for f in f_vecs if f != [0,0,0,0,0]]
        if not flavors:
            return 50.0
        max_sweet = max([f[0] for f in flavors])
        max_salty = max([f[1] for f in flavors])
        max_sour = max([f[2] for f in flavors])
        max_spicy = max([f[3] for f in flavors])
        max_pungent = max([f[4] for f in flavors])

        has_veg = any(c == 1 for c in valid_cats)
        has_meat = any(c == 2 for c in valid_cats)
        has_fruit = any(c == 3 for c in valid_cats)
        has_seafood = any(c == 4 for c in valid_cats)
        has_tofu = any(c == 5 for c in valid_cats)
        has_processed = any(c == 6 for c in valid_cats)
        has_spice = any(c == 7 for c in valid_cats)
        has_carb = any(c == 8 for c in valid_cats)

        # 动态初始分（根据食材类型）
        score = 60.0 if (has_veg and has_meat) else 40.0

        # 黄金搭配加分（扩大触发范围）
        if has_veg and has_meat:
            score += 20
        if has_veg and has_spice:
            score += 15
        if has_tofu and has_meat:
            score += 25
        if "西红柿" in valid_names and "鸡蛋" in valid_names:
            score += 30
        if "猪肉" in valid_names and "辣椒" in valid_names:
            score += 25
        if has_carb and (has_meat or has_veg):
            score += 10

        # 暗黑料理扣分（扩大触发范围）
        if has_fruit and (has_meat or has_seafood):
            # 甜咸冲突：甜度高+咸度高直接扣分
            if max_sweet >= 5 and max_salty >=3:
                score -= 50
        # 异味食材+水果/甜品
        if max_pungent >= 5 and has_fruit:
            score -= 40
        # 皮蛋+水果 强制扣分
        if "皮蛋" in valid_names and has_fruit:
            score -= 60
        # 鲱鱼罐头/榴莲+大部分食材扣分
        if "鲱鱼罐头" in valid_names or (has_fruit and "榴莲" in valid_names):
            score -= 80
        # 高辣+高甜 冲突
        if max_spicy >=7 and max_sweet >=7:
            score -= 30
        # 高异味（>7）无主食/高盐兜底
        if max_pungent >=7 and not (has_carb and max_salty >5):
            score -= 70

        # 限制0-100分
        return max(0.0, min(100.0, score))

    # ========== 修复2：核心打分逻辑（可达） ==========
    final_score = 0.0
    if model_load_success:
        try:
            # 构造张量，确保shape正确 [1,5]
            n_tensor = torch.tensor([n_ids], dtype=torch.long).to(device)
            c_tensor = torch.tensor([c_ids], dtype=torch.long).to(device)
            f_tensor = torch.tensor([f_vecs], dtype=torch.float32).to(device)
            
            # 打印shape，方便排查问题
            logger.info(f"张量shape: n={n_tensor.shape}, c={c_tensor.shape}, f={f_tensor.shape}")
            
            model2.eval()
            with torch.no_grad():
                score = model2(n_tensor, c_tensor, f_tensor).item()
            model_score = round(score * 100, 1)
            rule_score = rule_based_score(valid_names, f_vecs, valid_cats)  # 传参调用
            # 模型分权重70%，规则分30%兜底（你原来写的0.5+0.5，按需求调整）
            final_score = round(model_score * 0.5 + rule_score * 0.5, 1)
            logger.info(f"✅ AI-2 预测完成 | 模型分: {model_score} | 规则分: {rule_score} | 最终分: {final_score}")
        except Exception as e:
            logger.error(f"❌ AI-2 预测失败，使用规则分: {e}", exc_info=True)
            final_score = rule_based_score(valid_names, f_vecs, valid_cats)  # 传参调用
    else:
        final_score = rule_based_score(valid_names, f_vecs, valid_cats)  # 传参调用
        logger.info(f"⚠️ 使用纯规则打分 | 最终分: {final_score}")
    
    return {"status": "success", "harmony_score": final_score}
# ===================== 新增：启动FastAPI服务 =====================
if __name__ == "__main__":
    import uvicorn
    # 启动服务配置（开发环境）
    uvicorn.run(
        "app:app",          # 格式：文件名:FastAPI实例名（如果文件改名需对应修改）
        host="0.0.0.0",     # 允许本机/局域网/外网访问（仅本机测试可改 127.0.0.1）
        port=8000,          # 服务端口（可自定义，如 8080/9000）
        reload=True,        # 开发模式：代码修改后自动重启服务
        workers=1           # 进程数（生产环境可根据CPU核心数调整，如 4）
    )