# PseudoAnimation.gd - 伪动画系统
# 挂载到Sprite2D节点上，通过代码控制rotation、scale和position模拟动画效果
# 基于单张图片，使用程序化变换实现呼吸/行走/跳跃/攻击/受击动画
extends Sprite2D

# 基础缩放值（用于所有动画计算的基准）
var base_scale: Vector2 = Vector2(1.0, 1.0)

func _ready() -> void:
	base_scale = scale

# 当前动画类型
var anim_type: String = "idle"

# 动画时间累计器
var _time: float = 0.0

# 行走弹跳的累计偏移（防止无限位移）
var _walk_bounce_offset: float = 0.0


func _process(delta: float) -> void:
	_time += delta
	match anim_type:
		"idle":
			_anim_idle(delta)
		"walk":
			_anim_walk(delta)
		"jump":
			_anim_jump()
		"attack":
			_anim_attack()
		"hurt":
			pass  # 受击动画通过外部调用 play_hurt() 触发，不在此循环
		"death":
			pass  # 死亡动画通过外部调用 play_death() 触发
		"dash":
			_anim_dash()
		_:
			pass  # 未知动画类型，保持静止


## 待机呼吸动画：scale在0.95~1.05间正弦变化，周期约2秒
func _anim_idle(_delta: float) -> void:
	var breath: float = 1.0 + sin(_time * PI) * 0.05
	scale = base_scale * breath


## 行走摇摆动画：rotation在-0.1~0.1弧度间正弦摆动，周期约0.5秒
## 同时叠加微弱的上下弹跳效果
func _anim_walk(delta: float) -> void:
	# 左右摇摆
	var wobble: float = sin(_time * 4.0 * PI) * 0.1
	rotation = wobble
	
	# 上下弹跳（使用累积偏移避免无限位移）
	var bounce: float = sin(_time * 8.0 * PI) * 1.5
	position.y += (bounce - _walk_bounce_offset)
	_walk_bounce_offset = bounce


## 跳跃倾斜动画：上升时rotation向前倾-0.2，下落时向后倾+0.2
func _anim_jump() -> void:
	# 此动画依赖velocity，由Player.gd在状态中设置
	# 默认先设为上升姿态
	rotation = -0.2


## 攻击缩放动画：瞬间放大到1.2倍
## 恢复由调用方通过Tween控制
func _anim_attack() -> void:
	scale = base_scale * 1.2


## 冲刺动画：身体拉长+速度线效果（通过scale模拟）
func _anim_dash() -> void:
	var stretch: float = sin(_time * 20.0 * PI) * 0.15
	scale = Vector2(base_scale.x + stretch, base_scale.y - stretch * 0.5)


## 受击闪烁动画：红色闪烁0.2秒
func play_hurt() -> void:
	var tween: Tween = create_tween()
	tween.tween_property(self, "modulate", Color.RED, 0.1)
	tween.tween_property(self, "modulate", Color.WHITE, 0.1)
	
	# 抖动效果
	var orig_pos: Vector2 = position
	var shake_tween: Tween = create_tween()
	shake_tween.tween_property(self, "position:x", orig_pos.x + 5.0, 0.05)
	shake_tween.tween_property(self, "position:x", orig_pos.x - 5.0, 0.05)
	shake_tween.tween_property(self, "position:x", orig_pos.x + 3.0, 0.05)
	shake_tween.tween_property(self, "position:x", orig_pos.x, 0.05)


## 死亡缩小消失动画：scale缩小到0 + 淡出，持续1秒
func play_death() -> void:
	var tween: Tween = create_tween()
	tween.set_parallel(true)
	tween.tween_property(self, "scale", Vector2.ZERO, 1.0)
	tween.tween_property(self, "modulate:a", 0.0, 1.0)


## 重置所有变换（切换到新动画类型时调用）
func reset_transform() -> void:
	rotation = 0.0
	scale = base_scale
	modulate = Color(1, 1, 1, 1)
	position.y -= _walk_bounce_offset
	_walk_bounce_offset = 0.0


## 切换到指定动画类型
## @param new_type: 动画类型字符串（idle/walk/jump/attack/hurt/death/dash）
func switch_anim(new_type: String) -> void:
	if anim_type != new_type:
		reset_transform()
		_time = 0.0
		anim_type = new_type