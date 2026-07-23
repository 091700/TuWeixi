# 🎮 NiuQu Game — Godot 4 游戏工具库

基于 Godot 4 的 2D/3D 游戏通用工具集，提供 8 个核心脚本组件，覆盖物理碰撞、对象池、粒子系统、相机抖动、可破坏物体、伪动画等常见游戏需求。

## 组件

| 组件 | 说明 |
|------|------|
| `CollisionZoneManager.gd` | 碰撞区域管理器，自动处理 2D/3D 碰撞检测 |
| `BreakableObject.gd` | 可破坏物体逻辑，支持碎裂效果 |
| `CollectibleItem.gd` | 可收集物品实现，拾取反馈 |
| `ParticleManager.gd` | 粒子系统管理器，支持多粒子模板 |
| `CameraShake.gd` | 相机抖动，支持位移/旋转/缩放多维度抖动 |
| `ObjectPool.gd` | 对象池，复用高频创建/销毁对象 |
| `PseudoAnimation.gd` | 伪动画系统，纯代码驱动的补间动画 |
| `SceneInteractable.gd` | 场景交互组件，检测并响应玩家交互 |

## 技术栈

Godot 4 · GDScript