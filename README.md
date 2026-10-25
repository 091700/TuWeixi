<div align="center">
  <img src="assets/profile/hero.svg" width="100%" alt="TuWeixi — 12 projects">
  <br><br>
  <img src="https://img.shields.io/badge/PROJECTS-12-5B8CFF?style=flat-square" alt="Projects">
  <img src="https://img.shields.io/badge/LANGUAGES-7-9B6BFF?style=flat-square" alt="Languages">
  <img src="https://img.shields.io/badge/AI-4%20PROJECTS-FF6BD6?style=flat-square" alt="AI Projects">
  <img src="https://img.shields.io/github/stars/091700/TuWeixi?style=flat-square&color=FFC53D" alt="Stars">
  <br><br>
  <sub>12 个自研项目，覆盖 AI Agent、全栈 Web、桌面工具与游戏。<br>每个仓库都有独立 README，记录实现思路与关键取舍。</sub>
</div>

<br>

---

## 🤖 AI 与全栈

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🗄️ sql_agent</b><br>
      <sub>LLM Agent 全栈</sub>
    </td>
    <td valign="top">
      <sub>从零实现，1460 行自研代码，不套框架黑盒。</sub>
      <ul>
        <li>Agent Loop：五维终止 · LLM 自评 · Self-Healing 重试</li>
        <li>多 Agent 编排：DAG → Kahn 拓扑 → asyncio 并行</li>
        <li>PER 经验回放：按 TD-error 采样并注入 Prompt</li>
        <li>SQL 三层沙箱 · RBAC · 高危操作审批</li>
      </ul>
      <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white">
      <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white">
      <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white">
      <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square">
      <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🎙️ SmartInterview</b><br>
      <sub>AI 模拟面试</sub>
    </td>
    <td valign="top">
      <sub>语音面试 + 声学评分 + 内容追问的一体化平台。</sub>
      <ul>
        <li>WebSocket 实时对话，服务端 353 行</li>
        <li>Faster-Whisper GPU 转写，librosa 三项声学指标</li>
        <li>紧张度 / 自信度 / 清晰度三维评分</li>
        <li>ChromaDB + bge-small-zh 知识库检索</li>
        <li>DeepSeek 内容评分与追问生成</li>
      </ul>
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white">
      <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white">
      <img src="https://img.shields.io/badge/Whisper-7C3AED?style=flat-square">
      <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🧊 SmartPantry</b><br>
      <sub>智能冰箱管理</sub>
    </td>
    <td valign="top">
      <sub>预测保鲜期，顺便给黑暗料理打分。</sub>
      <ul>
        <li>PyTorch 全连接网络预测食材保鲜期</li>
        <li>5 维风味向量余弦相似度评分</li>
        <li>Qwen 2.5-1.5B 零样本提取食材特征</li>
        <li>19 种人工整理的风味特征基础库</li>
      </ul>
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white">
      <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white">
      <img src="https://img.shields.io/badge/Qwen-615CED?style=flat-square">
      <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>📚 Book Platform</b><br>
      <sub>智能图书交易</sub>
    </td>
    <td valign="top">
      <sub>搜索、识图、OCR，三路找到同一本书。</sub>
      <ul>
        <li>Elasticsearch 多字段模糊搜索，按 _score 排序</li>
        <li>YOLOv5 以图搜书：ONNX 导出 + Java 子进程调用</li>
        <li>Tesseract OCR 识别封面文字</li>
        <li>Spring Security + BCrypt 账号体系</li>
      </ul>
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white">
      <img src="https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white">
      <img src="https://img.shields.io/badge/YOLOv5-00BFFF?style=flat-square">
      <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white">
    </td>
  </tr>
</table>

<div align="center">
  <img src="assets/profile/divider.svg" width="72%" alt="divider">
</div>

## 🎮 游戏

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🍬 BestGameForever2</b><br>
      <sub>三消游戏 · 完整版</sub>
    </td>
    <td valign="top">
      <sub>26 个脚本、约 4100 行，MVC 分层 + 事件总线，动画全部用 cc.tween 实现。</sub>
      <ul>
        <li>7×9 棋盘，8 个世界 × 99 关</li>
        <li>地图程序生成：LCG 伪随机，同一关每次一致</li>
        <li>四连生成炸弹，3×3 连锁引爆</li>
        <li>清空全部背景后触发 GoalGem 下落通关</li>
        <li>连击计分 + 时间奖励 + 三星结算</li>
        <li>空闲提示 · 无解洗牌 · 暂停 · 胜负结算 · BGM</li>
      </ul>
      <img src="https://img.shields.io/badge/Cocos_Creator_2.4.2-55C2E1?style=flat-square&logo=cocos&logoColor=white">
      <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black">
      <img src="https://img.shields.io/badge/Canvas_2D-2C2255?style=flat-square">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🎮 niu-qu-game</b><br>
      <sub>2D 游戏工具框架</sub>
    </td>
    <td valign="top">
      <sub>8 个可复用 GDScript 模块，拼装关卡逻辑。</sub>
      <ul>
        <li>碰撞区域工厂 428 行，覆盖 8 种碰撞体</li>
        <li>6 个关卡传送点 + 6 个 Boss 顺序解锁</li>
        <li>可破坏物体系统 + 对象池</li>
        <li>粒子管理器 · 相机抖动 · 伪动画补间</li>
      </ul>
      <img src="https://img.shields.io/badge/Godot_4-478CBF?style=flat-square&logo=godotengine&logoColor=white">
      <img src="https://img.shields.io/badge/GDScript-355570?style=flat-square">
    </td>
  </tr>
</table>

<div align="center">
  <img src="assets/profile/divider.svg" width="72%" alt="divider">
</div>

## ⚙️ 桌面与工程

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🖥️ Floating Helper</b><br>
      <sub>Electron 桌面助手</sub>
    </td>
    <td valign="top">
      <sub>透明浮窗「奶龙」，贴边、说话、听指令。</sub>
      <ul>
        <li>边缘吸附：20px 阈值 + 150ms 防抖 + 45px 脱离</li>
        <li>CPU / 内存 / 网络每秒轮询</li>
        <li>DeepSeek 聊天，electron-store 持久化</li>
        <li>语音子进程管理，退出时 taskkill /T /F 回收</li>
      </ul>
      <img src="https://img.shields.io/badge/Electron_30-47848F?style=flat-square&logo=electron&logoColor=white">
      <img src="https://img.shields.io/badge/Node.js-5FA04E?style=flat-square&logo=nodedotjs&logoColor=white">
      <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>📱 CampusTaskManager</b><br>
      <sub>Android 校园任务</sub>
    </td>
    <td valign="top">
      <sub>任务管理 + 地图导航的课程作业级 App。</sub>
      <ul>
        <li>高德地图路线规划与导航</li>
        <li>任务 CRUD + 分类 + 状态流转</li>
        <li>中英双语 · 亮暗双主题</li>
        <li>8 个 Java 源文件 + 6 个 XML 布局</li>
      </ul>
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white">
      <img src="https://img.shields.io/badge/Android-34A853?style=flat-square&logo=android&logoColor=white">
      <img src="https://img.shields.io/badge/AMap-0091FF?style=flat-square">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🏪 WarehouseSystem</b><br>
      <sub>仓库管理系统</sub>
    </td>
    <td valign="top">
      <sub>24 个 Java 源文件，覆盖仓储全流程。</sub>
      <ul>
        <li>10 Controller · 7 DAO · 5 Model 分层</li>
        <li>商品、订单、出入库管理</li>
        <li>客户 / 供应商 / 多仓库</li>
        <li>JDBC + Druid 连接池</li>
      </ul>
      <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white">
      <img src="https://img.shields.io/badge/Spring_MVC-6DB33F?style=flat-square&logo=spring&logoColor=white">
      <img src="https://img.shields.io/badge/JSP-FF6B00?style=flat-square">
      <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>📋 Student Manager</b><br>
      <sub>学生管理系统</sub>
    </td>
    <td valign="top">
      <sub>14 个 Java 源文件，分层清晰。</sub>
      <ul>
        <li>Controller / Service / DAO 分层</li>
        <li>Apache POI 批量导入导出 Excel</li>
        <li>LoginInterceptor 统一登录拦截</li>
        <li>Spring Boot + Thymeleaf 渲染</li>
      </ul>
      <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white">
      <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white">
      <img src="https://img.shields.io/badge/Apache_POI-D22128?style=flat-square&logo=apache&logoColor=white">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>🛒 e-commerce</b><br>
      <sub>PHP 电商系统</sub>
    </td>
    <td valign="top">
      <sub>15 个 PHP 文件，从注册到结算跑通一条线。</sub>
      <ul>
        <li>注册登录 · 商品管理</li>
        <li>购物车 · 下单结算</li>
        <li>后台商品 CRUD</li>
        <li>PDO 预处理 + Session</li>
      </ul>
      <img src="https://img.shields.io/badge/PHP_8-777BB4?style=flat-square&logo=php&logoColor=white">
      <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white">
    </td>
  </tr>
</table>

<table>
  <tr>
    <td width="24%" valign="top">
      <b>⚡ NetAcceleratorWin</b><br>
      <sub>WinForms 恶搞工具</sub>
    </td>
    <td valign="top">
      <sub>启动页 + 视频播放，双击即运行的整蛊小程序。</sub>
      <ul>
        <li>WinForms 两套窗体</li>
        <li>Fody / Costura 合并为单个 exe</li>
        <li>仅供娱乐</li>
      </ul>
      <img src="https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white">
      <img src="https://img.shields.io/badge/.NET_Framework-512BD4?style=flat-square&logo=dotnet&logoColor=white">
    </td>
  </tr>
</table>

<div align="center">
  <img src="assets/profile/divider.svg" width="72%" alt="divider">
</div>

## 🛠️ 技术栈

| 方向 | 用过的技术 |
|------|------------|
| **语言** | <img src="https://img.shields.io/badge/Java-ED8B00?style=flat-square&logo=openjdk&logoColor=white"> <img src="https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"> <img src="https://img.shields.io/badge/PHP-777BB4?style=flat-square&logo=php&logoColor=white"> <img src="https://img.shields.io/badge/C%23-512BD4?style=flat-square&logo=dotnet&logoColor=white"> <img src="https://img.shields.io/badge/GDScript-355570?style=flat-square"> |
| **后端** | <img src="https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white"> <img src="https://img.shields.io/badge/Spring_MVC-6DB33F?style=flat-square&logo=spring&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white"> <img src="https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white"> |
| **前端** | <img src="https://img.shields.io/badge/Vue_3-4FC08D?style=flat-square&logo=vuedotjs&logoColor=white"> <img src="https://img.shields.io/badge/Thymeleaf-005F0F?style=flat-square&logo=thymeleaf&logoColor=white"> <img src="https://img.shields.io/badge/JSP-FF6B00?style=flat-square"> <img src="https://img.shields.io/badge/Bootstrap-7952B3?style=flat-square&logo=bootstrap&logoColor=white"> |
| **AI / 数据** | <img src="https://img.shields.io/badge/DeepSeek-4B6BFB?style=flat-square"> <img src="https://img.shields.io/badge/Whisper-7C3AED?style=flat-square"> <img src="https://img.shields.io/badge/YOLOv5-00BFFF?style=flat-square"> <img src="https://img.shields.io/badge/Qwen-615CED?style=flat-square"> <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white"> <img src="https://img.shields.io/badge/ChromaDB-FF6B6B?style=flat-square"> |
| **存储** | <img src="https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white"> <img src="https://img.shields.io/badge/Elasticsearch-005571?style=flat-square&logo=elasticsearch&logoColor=white"> <img src="https://img.shields.io/badge/MyBatis--Plus-D77310?style=flat-square"> <img src="https://img.shields.io/badge/JPA-59666C?style=flat-square&logo=hibernate&logoColor=white"> <img src="https://img.shields.io/badge/Druid-1C9B5E?style=flat-square"> |
| **工程** | <img src="https://img.shields.io/badge/WebSocket-010101?style=flat-square&logo=socketdotio&logoColor=white"> <img src="https://img.shields.io/badge/Cocos_Creator-55C2E1?style=flat-square&logo=cocos&logoColor=white"> <img src="https://img.shields.io/badge/Godot_4-478CBF?style=flat-square&logo=godotengine&logoColor=white"> <img src="https://img.shields.io/badge/Android-34A853?style=flat-square&logo=android&logoColor=white"> <img src="https://img.shields.io/badge/Git-F05032?style=flat-square&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/Maven-C71A36?style=flat-square&logo=apachemaven&logoColor=white"> <img src="https://img.shields.io/badge/Gradle-02303A?style=flat-square&logo=gradle&logoColor=white"> |

---

<div align="center">
  <a href="https://github.com/091700/TuWeixi"><img src="https://img.shields.io/badge/GitHub-091700-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub"></a>
  <br><br>
  <sub>项目源码、目录结构与实现细节，见各仓库内的 README。</sub>
</div>

