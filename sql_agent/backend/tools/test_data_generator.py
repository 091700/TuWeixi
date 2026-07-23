"""工具5: generate_test_data —— 业务语义测试数据一键生成（工业增强版）
支持基于已有数据样本的列语义推断 + 中文语义映射 + 数据类型推断三层回退"""
import re
import random
import string
import pymysql
from typing import Optional, Callable
from faker import Faker

from config import settings
from security.connection_pool import pool_manager
from tools.metadata_tool import get_table_metadata

fake = Faker("zh_CN")

# ── 语义→Faker 生成器映射（增强版，含中文+英文+复合词）─
SEMANTIC_MAP: dict = {}

def _build_semantic_map():
    """构建完整语义映射表"""
    base = {
        # ─ 人名 ─
        "name": "name", "姓名": "name", "名字": "name", "用户名": "user_name",
        "username": "user_name", "user_name": "user_name", "realname": "name",
        "nickname": "name", "nick_name": "name",
        # ─ 联系方式 ─
        "phone": "phone_number", "电话": "phone_number", "手机": "phone_number",
        "mobile": "phone_number", "tel": "phone_number", "telephone": "phone_number",
        "手机号": "phone_number", "contact": "phone_number",
        "email": "email", "邮箱": "email", "mail": "email",
        # ─ 地址 ─
        "address": "address", "住址": "address", "地址": "address",
        "province": "province", "省份": "province",
        "city": "city", "城市": "city", "市": "city",
        "district": "district", "区": "district", "县": "district",
        # ─ 公司 ─
        "company": "company", "公司": "company", "单位": "company",
        # ─ 身份证 ─
        "id_card": "ssn", "身份证": "ssn", "身份证号": "ssn",
        "idcard": "ssn", "card_id": "ssn",
        # ─ 其他 ─
        "ip": "ipv4", "ipv4": "ipv4",
        "url": "url", "网址": "url", "link": "url",
        "birthday": "date_of_birth", "生日": "date_of_birth", "birth": "date_of_birth",
        "age": "age_int", "年龄": "age_int",
        "amount": "amount", "金额": "amount", "price": "amount",
        "价格": "amount", "money": "amount", "费用": "amount",
        "quantity": "qty", "数量": "qty", "count": "qty", "qty": "qty", "num": "qty",
        "description": "sentence", "描述": "sentence", "说明": "sentence",
        "remark": "sentence", "备注": "sentence", "content": "paragraph",
        # ─ 时间 ─
        "created_at": "datetime", "updated_at": "datetime",
        "create_time": "datetime", "update_time": "datetime",
        "deleted_at": "datetime", "delete_time": "datetime",
        "date": "date", "日期": "date", "time": "datetime",
        # ─ 能力/技能（关键修复）─
        "capability": "capability_type", "能力": "capability_type",
        "skill": "capability_type", "技能": "capability_type",
        "ability": "capability_type",
        "profession": "job", "职业": "job", "job": "job", "工作": "job",
        # ─ 状态枚举 ─
        "status": "status_enum", "state": "status_enum", "type": "type_enum",
        "level": "level_enum", "等级": "level_enum",
        "grade": "level_enum", "评分": "level_enum",
        "gender": "gender", "性別": "gender", "sex": "gender", "性别": "gender",
        # ─ UUID ─
        "uuid": "uuid4", "guid": "uuid4",
        # ─ 认证相关 ─
        "password_hash": "bcrypt_hash", "password": "bcrypt_hash", "pwd": "bcrypt_hash",
        "role": "role_enum", "角色": "role_enum", "roles": "role_enum",
        "display_name": "display_name", "昵称": "display_name",
        # ─ 用户名相关（确保优先于其他匹配）─
        "user_name": "user_name", "login_name": "user_name",
    }
    result = {}
    for keyword, gen_type in base.items():
        result[keyword.lower()] = gen_type
    return result

SEMANTIC_MAP = _build_semantic_map()

# ── 已有数据样本采样与推断 ───────────────────────
def _sample_existing_data(database: str, table: str, column: str, limit: int = 5) -> list:
    """从已有表中采样某列的数据值，用于推断语义"""
    try:
        conn = pool_manager.get_connection(database)
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL AND `{column}` != '' LIMIT {limit}")
            rows = cursor.fetchall()
        conn.close()
        return [list(row.values())[0] for row in rows] if rows else []
    except Exception:
        return []


def _infer_from_samples(samples: list) -> Optional[str]:
    """从数据样本推断列语义类型"""
    if not samples:
        return None
    str_samples = [str(s) for s in samples]

    # 身份证号（18位数字或17位+X）
    if any(re.match(r'^\d{17}[\dXx]$', s) for s in str_samples):
        return "ssn"

    # 手机号（1开头11位数字）
    if any(re.match(r'^1[3-9]\d{9}$', s) for s in str_samples):
        return "phone_number"

    # 邮箱
    if any('@' in s for s in str_samples):
        return "email"

    # 纯中文（可能是人名、地址等）
    all_chinese = [re.sub(r'[^\u4e00-\u9fff]', '', s) for s in str_samples]
    if all(s and len(s) >= 2 and len(s) <= 4 for s in all_chinese):
        return "name"  # 短中文大概率是人名
    if all(s and len(s) >= 5 for s in all_chinese):
        return "address"  # 长中文大概率是地址

    # 布尔（必须在纯数字ID之前，否则 0/1 会被误判为 id_number）
    if all(s in ('0', '1', 'true', 'false', '是', '否', 'YES', 'NO') for s in str_samples):
        return "bool"

    # 纯数字ID
    if all(re.match(r'^\d{1,10}$', s) for s in str_samples):
        return "id_number"

    # 男女枚举
    if all(s in ('男', '女', 'M', 'F', 'Male', 'Female') for s in str_samples):
        return "gender"

    return None


# ── 生成器工厂 ──────────────────────────────────
def _make_generator(gen_type: str, col_type: str = "", col_name: str = "") -> Callable:
    """根据语义类型创建数据生成器"""

    # ─ 特定语义类型 ─
    if gen_type == "name":
        return lambda: fake.name()
    elif gen_type == "user_name":
        return lambda: fake.user_name()
    elif gen_type == "phone_number":
        return lambda: fake.phone_number()
    elif gen_type == "email":
        return lambda: fake.email()
    elif gen_type == "address":
        return lambda: fake.address()
    elif gen_type == "province":
        return lambda: fake.province()
    elif gen_type == "city":
        return lambda: fake.city()
    elif gen_type == "district":
        return lambda: fake.district()
    elif gen_type == "company":
        return lambda: fake.company()
    elif gen_type == "ssn":
        return lambda: fake.ssn()
    elif gen_type == "ipv4":
        return lambda: fake.ipv4()
    elif gen_type == "url":
        return lambda: fake.url()
    elif gen_type == "date_of_birth":
        return lambda: fake.date_of_birth().isoformat()
    elif gen_type == "age_int":
        return lambda: random.randint(18, 65)
    elif gen_type == "amount":
        return lambda: round(random.uniform(0.01, 99999.99), 2)
    elif gen_type == "qty":
        return lambda: random.randint(1, 100)
    elif gen_type == "sentence":
        return lambda: fake.sentence()
    elif gen_type == "paragraph":
        return lambda: fake.paragraph()
    elif gen_type == "date":
        return lambda: fake.date_this_year().isoformat()
    elif gen_type == "datetime":
        return lambda: fake.date_time_this_year().isoformat()
    elif gen_type == "uuid4":
        return lambda: fake.uuid4()
    elif gen_type == "gender":
        return lambda: random.choice(["男", "女"])
    elif gen_type == "bool":
        return lambda: random.choice([0, 1])
    elif gen_type == "id_number":
        return lambda: random.randint(1, 100000)
    elif gen_type == "capability_type":
        return lambda: random.choice([
            "完全劳动能力", "部分劳动能力", "丧失劳动能力",
            "有劳动能力", "弱劳动力", "无劳动能力"
        ])
    elif gen_type == "job":
        return lambda: random.choice([
            "务农", "务工", "个体经营", "无业", "退休",
            "学生", "公务员", "企业职员", "自由职业"
        ])
    elif gen_type == "status_enum":
        return lambda: random.randint(0, 1)
    elif gen_type == "level_enum":
        return lambda: random.randint(1, 5)
    elif gen_type == "type_enum":
        return lambda: random.choice(["admin", "reader", "writer"])
    elif gen_type == "bcrypt_hash":
        import bcrypt
        return lambda: bcrypt.hashpw(fake.password(length=12).encode(), bcrypt.gensalt()).decode()
    elif gen_type == "role_enum":
        return lambda: random.choice(["admin", "reader"])
    elif gen_type == "display_name":
        return lambda: "用户_" + fake.user_name()

    # ─ 数据类型推断 ─
    type_upper = col_type.upper() if col_type else ""

    if "INT" in type_upper or "TINYINT" in type_upper or "SMALLINT" in type_upper:
        if "bool" in col_name.lower() or "is_" in col_name.lower() or "active" in col_name.lower():
            return lambda: random.choice([0, 1])
        if "status" in col_name.lower() or "state" in col_name.lower():
            return lambda: random.randint(1, 5)
        return lambda: random.randint(1, 10000)

    if "BIGINT" in type_upper:
        return lambda: random.randint(1, 100000)

    if "DECIMAL" in type_upper or "FLOAT" in type_upper or "DOUBLE" in type_upper:
        return lambda: round(random.uniform(0.01, 9999.99), 2)

    if "VARCHAR" in type_upper or "CHAR" in type_upper:
        max_len = 32
        match = re.search(r'\((\d+)\)', col_type)
        if match:
            max_len = min(int(match.group(1)), 64)
        return lambda: fake.word()[:max_len]

    if "TEXT" in type_upper:
        return lambda: fake.sentence()

    if "DATE" in type_upper:
        return lambda: fake.date_this_year().isoformat()

    if "DATETIME" in type_upper or "TIMESTAMP" in type_upper:
        return lambda: fake.date_time_this_year().isoformat()

    if "JSON" in type_upper:
        return lambda: '{"value":' + str(random.randint(1, 100)) + '}'

    # ─ 默认兜底 ─
    return lambda: fake.word()


# ── 主函数 ──────────────────────────────────────
def generate_test_data(
    database: str,
    table: str,
    scenario: str = "",
    row_count: int = 50,
) -> dict:
    """
    根据业务场景描述和表结构约束，生成符合真实业务逻辑的批量 INSERT 语句

    语义推断优先级：
    1. 已有数据样本反向推断（最准确）
    2. 列名/注释匹配语义映射
    3. 数据类型默认推断
    """
    row_count = min(int(row_count), 500)

    # 获取表结构
    meta = get_table_metadata(database, table)
    if not meta.get("success"):
        return {"success": False, "error": f"获取表结构失败: {meta.get('error', '未知错误')}"}

    tables = meta.get("tables", [])
    if not tables:
        return {"success": False, "error": f"表 '{table}' 不存在于数据库 '{database}'"}

    columns = tables[0].get("columns", [])
    if not columns:
        return {"success": False, "error": f"表 '{table}' 无列定义"}

    # 构建字段→生成器映射（三层推断）
    col_generators = {}
    col_names = []
    semantic_log = []  # 记录每个列的推断来源

    for col in columns:
        col_name = col["name"]
        col_type = col["type"]
        col_comment = col.get("comment", "")
        is_auto = "auto_increment" in col.get("extra", "").lower()

        # 跳过自增主键
        if is_auto and col["key"] == "PRI":
            semantic_log.append(f"{col_name}: 跳过(自增主键)")
            continue

        col_names.append(col_name)
        col_lower = col_name.lower()
        comment_lower = col_comment.lower() if col_comment else ""

        # 第1层：从已有数据样本推断
        gen_type = None
        samples = _sample_existing_data(database, table, col_name, 5)
        if samples:
            gen_type = _infer_from_samples(samples)
            if gen_type:
                semantic_log.append(f"{col_name}: 样本推断 → {gen_type} (样本: {samples[:3]})")
                col_generators[col_name] = _make_generator(gen_type, col_type, col_name)
                continue

        # 第2层：列名/注释匹配（先强制整数列的布尔检测，避免子串命中如 is_active 命中了 ip）
        col_type_upper = (col.get("data_type") or "").upper()
        if col_type_upper in ("INT", "TINYINT", "SMALLINT", "BIGINT") and ("is_" in col_lower or "has_" in col_lower):
            gen_type = "bool"
        else:
            for keyword, gt in SEMANTIC_MAP.items():
                if keyword in col_lower or keyword in comment_lower:
                    gen_type = gt
                    break

        if gen_type:
            semantic_log.append(f"{col_name}: 语义匹配 → {gen_type} (匹配关键词)")
        else:
            gen_type = "type_default"
            semantic_log.append(f"{col_name}: 类型默认 → {col_type}")

        col_generators[col_name] = _make_generator(gen_type, col_type, col_name)

    if not col_names:
        return {"success": False, "error": "表无可用生成列"}

    # 学习跨列关系：从已有数据中提取 role→display_name 的映射规律
    role_display_map = {}
    if "role" in col_names and "display_name" in col_names:
        try:
            conn = pool_manager.get_connection(database)
            with conn.cursor() as cur:
                cur.execute(f"SELECT DISTINCT `role`, `display_name` FROM `{table}` WHERE `display_name` IS NOT NULL AND `display_name` != '' LIMIT 10")
                for row in cur.fetchall():
                    r = row.get("role", "") or list(row.values())[0]
                    d = row.get("display_name", "") or (list(row.values())[1] if len(row) > 1 else "")
                    if r and d:
                        role_display_map[str(r).strip().lower()] = str(d)
            conn.close()
        except Exception:
            pass

    # 生成数据
    insert_statements = []
    sample_data = []

    for batch_start in range(0, row_count, min(row_count, 50)):
        batch_end = min(batch_start + 50, row_count)
        batch_rows = []

        for _ in range(batch_end - batch_start):
            row_values = {}
            for col_name in col_names:
                try:
                    val = col_generators[col_name]()
                except Exception:
                    val = ""
                if isinstance(val, str):
                    val = val.replace("'", "\\'")
                    val = f"'{val}'"
                row_values[col_name] = val

            # 跨列关系推断：从已有数据中学习 role→display_name 映射，如果已有记录就用它，否则用默认模式
            if "role" in col_names and "display_name" in col_names:
                raw_role = str(row_values.get("role", "")).strip("'").lower()
                if role_display_map and raw_role in role_display_map:
                    row_values["display_name"] = f"'{role_display_map[raw_role]}'"
                elif "admin" in raw_role:
                    row_values["display_name"] = "'系统管理员'"
                elif "reader" in raw_role:
                    row_values["display_name"] = "'只读用户'"

            batch_rows.append(row_values)

        cols_str = ", ".join(f"`{c}`" for c in col_names)
        values_list = []
        for row in batch_rows:
            vals = []
            for c in col_names:
                v = row[c]
                vals.append(str(v) if isinstance(v, (int, float)) else v)
            values_list.append(f"({', '.join(vals)})")

        insert_sql = f"INSERT INTO `{table}` ({cols_str}) VALUES\n  " + ",\n  ".join(values_list) + ";"
        insert_statements.append(insert_sql)

        if len(sample_data) < 3:
            sample_data.extend(batch_rows[:3 - len(sample_data)])

    return {
        "success": True,
        "table": table,
        "database": database,
        "row_count": row_count,
        "generated_columns": col_names,
        "insert_statements": insert_statements,
        "sample_data": sample_data[:3],
        "scenario": scenario or "通用业务数据",
        "semantic_log": semantic_log,
    }


# ── Tool Definition Schema ──────────────────────────
TOOL_GENERATE_DATA_DEFINITION = {
    "type": "function",
    "function": {
        "name": "generate_test_data",
        "description": (
            "根据业务场景描述和表结构约束，自动识别字段语义（从已有数据样本推断 + 列名匹配 + 类型推断），"
            "生成符合真实业务逻辑的批量 INSERT 语句。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "database": {"type": "string", "description": "目标数据库名"},
                "table": {"type": "string", "description": "目标表名"},
                "scenario": {"type": "string", "description": "业务场景描述，如：生成100条电商用户订单数据"},
                "row_count": {"type": "integer", "description": "生成数据行数，默认50，最大500"},
            },
            "required": ["database", "table", "scenario"],
        },
    },
}