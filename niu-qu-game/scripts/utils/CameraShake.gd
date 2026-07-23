# CameraShake.gd - 摄像机震动效果
# 挂载到Camera2D节点上，提供屏幕震动功能
# 用于受击反馈、BOSS登场、爆炸等场景
extends Camera2D

## 震动强度（像素偏移量）
var _shake_intensity: float = 0.0

## 震动剩余持续时间
var _shake_duration: float = 0.0

## 摄像机的原始偏移量（用于恢复）
var _original_offset: Vector2


func _ready() -> void:
	_original_offset = offset


## 触发屏幕震动
## @param intensity: 震动强度（像素偏移量），推荐值：受击3，BOSS登场8，爆炸10
## @param duration: 持续时间（秒），推荐值：受击0.2，BOSS登场0.5，爆炸0.3
func shake(intensity: float, duration: float) -> void:
	# 取最大值，避免小震动覆盖大震动
	if intensity > _shake_intensity or _shake_duration <= 0:
		_shake_intensity = intensity
		_shake_duration = duration


## 每帧更新震动效果
func _process(delta: float) -> void:
	if _shake_duration > 0:
		_shake_duration -= delta
		# 使用指数衰减让震动逐渐减弱
		var current_intensity: float = _shake_intensity * (_shake_duration / maxf(0.01, _shake_duration + 0.5))
		offset = _original_offset + Vector2(
			randf_range(-current_intensity, current_intensity),
			randf_range(-current_intensity, current_intensity)
		)
		if _shake_duration <= 0:
			# 震动结束，恢复原位
			offset = _original_offset
			_shake_intensity = 0.0


## 立即停止震动并恢复摄像机位置
func stop_shake() -> void:
	_shake_duration = 0.0
	_shake_intensity = 0.0
	offset = _original_offset