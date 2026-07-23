# 🎮 NiuQu Game — Godot 4 2D 游戏工具框架

基于 Godot 4 的 2D 平台跳跃游戏引擎工具集，8 个 GDScript 核心模块，约 68KB 源码，覆盖碰撞系统、对象池、粒子动画、相机运镜、关卡交互等完整游戏开发管线。

---

## 核心脚本

### CollisionZoneManager（428 行）

碰撞区域工厂。根据数据数组动态生成 8 种碰撞体，用代码驱动而非手动搭建 TileMap：

- wall / floor：StaticBody2D 实心地形
- oneway：单向平台（`one_way_collision = true`）
- death / damage：即死深渊 / 持续扣血区域（Area2D 信号驱动）
- water：水域减速区（`slow_factor` 可配置）
- checkpoint：存档点 + 6 关卡传送系统（蜘蛛女王 → 大公鸡领主 → 下水道鳄鱼 → 挖掘机巨人 → 农夫的狗 → 保洁阿姨），每个 Boss 击败后解锁下一关
- pipe_entrance：管道秘密入口（跨地图传送）
- breakable：可破坏障碍（指定破坏方式和耐久值，留接口给后续模块）

### BreakableObject（348 行）

可破坏物体系统：

- 耐久值 + 伤害阈值双重判定
- 碎裂动画触发（Tween 驱动缩放 + 透明度 → queue_free）
- 掉落物生成（CollectibleItem 实例化）
- 碰撞体实时禁用/启用（`collision_layer = 0` 切换）

### CollectibleItem（240 行）

可收集物品系统：

- 磁吸拾取（`move_toward` 插值吸附到玩家）
- 脉冲动画（`sin` 函数驱动大小变化）
- 瞬间拾取 / 缓动拾取两种模式
- 拾取后触发信号 + 粒子效果

### ParticleManager（328 行）

粒子系统管理器：

- 多粒子模板池（碰撞火花 / 收集闪光 / 跳跃灰尘 / 碎裂碎片 / 魔法光环）
- 每个模板独立配置颜色、数量、生命周期、速度、扩散角
- 预设函数：`spawn_collision_sparks(pos)` / `spawn_collect_glow(pos)` / `spawn_jump_dust(pos)` 等
- 防泄漏机制：粒子数量上限 + 定时自动清理

### CameraShake（47 行）

相机抖动引擎：

- 位移 / 旋转 / 缩放三通道独立噪声
- 强度衰减（`max(linear_decay, 0)`）
- `shake_intensity(amount)` 和 `shake_continuous(intensity, duration)` 两种模式

### ObjectPool（130 行）

泛型对象池：

- `prefab` 模板预加载
- `acquire()` / `release()` 接口
- 自动扩容（`max_size` 硬上限防止内存泄漏）
- 通过组标签标记池中活跃对象

### PseudoAnimation（108 行）

纯代码补间动画：

- 位置 / 旋转 / 缩放三通道支持
- `ease` 和 `elastic` 两种缓动曲线
- 全局帧同步（`_process(delta)` 驱动，Tween 不可用时回退）
- 链式调用：`start()` → 自动完成 → `queue_free_or_reset()`

### SceneInteractable（410 行）

交互系统：

- 圆形检测区域探测玩家
- 交互提示 UI 自动跟随
- 可配置交互类型（对话 / 拾取 / 开关 / 传送）
- 交互状态机（`idle → highlighted → interacting → cooldown`）

---

## 关卡传送系统

基于 `Global.story_flags` 的渐进式关卡解锁：

```
cave_1 → (击败蜘蛛女王) → cave_2 → (击败大公鸡领主)
  → sewer_1 → (击败鳄鱼) → sewer_2 → (击败挖掘机巨人)
  → farm_1 → (击败农夫的狗) → farm_2 → (击败保洁阿姨) → 通关
```

每个传送点自动检查对应 Boss 的 `story_flag`，未击败时显示阻挡消息 + 2 秒渐隐消失动画。

## 技术栈

Godot 4 · GDScript · 纯节点体系（无第三方插件依赖）
