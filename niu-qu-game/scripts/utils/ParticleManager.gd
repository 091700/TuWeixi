# ParticleManager.gd - 粒子特效管理器
# 用于程序化生成游戏中的各种粒子特效（受击火花、死亡爆散、升级金光等）
# 使用GPUParticles2D节点 + 程序化材质，避免使用图片资源
extends Node

# ========== 静态全局粒子实例 ==========
static var _instance: Node = null

# ========== 粒子颜色预设 ==========
const COLOR_HIT_SPARK  = Color(1, 0.9, 0.2)
const COLOR_DEATH_BURST = Color(0.7, 0.1, 0.1)
const COLOR_LEVEL_UP   = Color(1, 0.85, 0.1)
const COLOR_MUCUS       = Color(0.2, 0.8, 0.3)
const COLOR_DUNG_BROWN  = Color(0.4, 0.25, 0.12)
const COLOR_DISINFECT   = Color(0.3, 0.9, 0.4)
const COLOR_FEATHER     = Color(0.95, 0.95, 1)
const COLOR_DIRT        = Color(0.5, 0.35, 0.2)
const COLOR_BUBBLE      = Color(0.7, 0.85, 1, 0.6)
const COLOR_DUST        = Color(0.5, 0.45, 0.4, 0.4)
const COLOR_HEAL        = Color(0.2, 0.9, 0.4)
const COLOR_BOSS_INTRO  = Color(1, 0.2, 0.1)
const COLOR_IMPACT_RING = Color(1, 0.8, 0.3)


func _ready() -> void:
	_instance = self
	process_mode = Node.PROCESS_MODE_ALWAYS
	add_to_group("particle_manager")
	print("ParticleManager: 粒子特效管理器已就绪")


## 获取全局实例
static func get_instance() -> Node:
	return _instance


# ========== 简单粒子（使用ColorRect + Tween，兼容性最好） ==========

## 创建突发粒子爆散（使用ColorRect碎片代替GPUParticles2D，避免Vector2/Vector3版本问题）
## @param parent: 父节点
## @param pos: 世界坐标位置
## @param col: 粒子颜色
## @param count: 粒子数量
## @param lifetime: 粒子生命周期（秒）
## @param spread: 扩散速度范围（px）
func _create_simple_burst(
	parent: Node,
	pos: Vector2,
	col: Color,
	count: int = 12,
	lifetime: float = 0.5,
	spread: float = 150.0
) -> void:
	for i in range(count):
		var particle = ColorRect.new()
		var psize: float = randf_range(2.0, 6.0)
		particle.size = Vector2(psize, psize)
		particle.color = col
		particle.modulate.a = 0.8
		particle.name = "BurstParticle"
		
		particle.global_position = pos + Vector2(randf_range(-5, 5), randf_range(-5, 5))
		parent.add_child(particle)
		
		var angle: float = randf_range(0, TAU)
		var dist: float = randf_range(spread * 0.3, spread)
		var target: Vector2 = particle.position + Vector2(cos(angle) * dist, sin(angle) * dist)
		
		var tween: Tween = parent.create_tween()
		tween.set_parallel(true)
		tween.tween_property(particle, "position", target, lifetime)
		tween.tween_property(particle, "modulate:a", 0.0, lifetime)
		tween.tween_property(particle, "rotation", randf_range(-PI, PI), lifetime)
		tween.tween_property(particle, "scale", Vector2(randf_range(0.3, 1.5), randf_range(0.3, 1.5)), lifetime)
		tween.finished.connect(particle.queue_free)


# ========== 特效快捷方法 ==========

## 受击火花特效
func play_hit_spark(parent: Node, position: Vector2, count: int = 8) -> void:
	_create_simple_burst(parent, position, COLOR_HIT_SPARK, count, 0.3, 100.0)


## 死亡爆散特效
func play_death_burst(parent: Node, position: Vector2, color_override: Color = COLOR_DEATH_BURST) -> void:
	_create_simple_burst(parent, position, color_override, 18, 0.6, 180.0)


## 升级金光特效
func play_level_up_gold(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_LEVEL_UP, 25, 1.2, 90.0)
	var timer: SceneTreeTimer = parent.get_tree().create_timer(0.3)
	timer.timeout.connect(func():
		if is_instance_valid(parent):
			_create_simple_burst(parent, position + Vector2(0, -40), Color(1, 0.9, 0.3), 15, 0.8, 60.0)
	)


## 冲击波扩散特效
func play_impact_ring(parent: Node, position: Vector2, color: Color = COLOR_IMPACT_RING, radius: float = 80.0) -> void:
	var ring = ColorRect.new()
	ring.size = Vector2(4, 4)
	ring.position = parent.to_local(position) - Vector2(2, 2)
	ring.color = color
	ring.modulate.a = 0.8
	ring.name = "ImpactRing"
	parent.add_child(ring)
	
	var tween: Tween = parent.create_tween()
	tween.set_parallel(true)
	tween.tween_property(ring, "scale", Vector2(radius / 2.0, radius / 2.0), 0.4)
	tween.tween_property(ring, "modulate:a", 0.0, 0.4)
	tween.tween_property(ring, "position", ring.position - Vector2(radius / 2.0, radius / 2.0), 0.4)
	tween.finished.connect(ring.queue_free)
	
	_create_simple_burst(parent, position, color, 10, 0.35, radius)


## 黏液轨迹粒子
func play_mucus_trail(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_MUCUS, 5, 0.4, 30.0)


## 粪球爆炸特效
func play_dung_explosion(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_DUNG_BROWN, 20, 0.7, 160.0)
	play_impact_ring(parent, position, Color(0.5, 0.3, 0.15, 0.6), 60.0)


## 消毒液雾特效
func play_disinfect_mist(parent: Node, position: Vector2, direction: Vector2 = Vector2.RIGHT) -> void:
	# 雾状粒子沿指定方向扩散
	for i in range(12):
		var particle = ColorRect.new()
		var psize: float = randf_range(3.0, 8.0)
		particle.size = Vector2(psize, psize)
		particle.color = COLOR_DISINFECT
		particle.modulate.a = 0.7
		particle.global_position = position + Vector2(randf_range(-15, 15), randf_range(-10, 10))
		particle.name = "MistParticle"
		parent.add_child(particle)
		
		var dir_len: float = randf_range(60.0, 150.0)
		var angle_jitter: float = randf_range(-20.0, 20.0) * PI / 180.0
		var base_angle: float = direction.angle()
		var final_angle: float = base_angle + angle_jitter
		var target: Vector2 = particle.position + Vector2(cos(final_angle), sin(final_angle)) * dir_len
		
		var tween: Tween = parent.create_tween()
		tween.set_parallel(true)
		tween.tween_property(particle, "position", target, 0.5)
		tween.tween_property(particle, "modulate:a", 0.0, 0.5)
		tween.tween_property(particle, "scale", Vector2(randf_range(0.5, 2.0), randf_range(0.5, 2.0)), 0.5)
		tween.finished.connect(particle.queue_free)


## 羽毛飘落特效
func play_feather_fall(parent: Node, position: Vector2, count: int = 6) -> void:
	for i in range(count):
		var feather = ColorRect.new()
		feather.size = Vector2(6, 2)
		feather.color = COLOR_FEATHER
		feather.modulate.a = 0.8
		feather.global_position = position + Vector2(randf_range(-30, 30), randf_range(0, 10))
		feather.name = "Feather"
		parent.add_child(feather)
		
		var target: Vector2 = feather.position + Vector2(randf_range(-40, 40), randf_range(60, 150))
		var tween: Tween = parent.create_tween()
		tween.set_parallel(true)
		tween.tween_property(feather, "position", target, 2.0)
		tween.tween_property(feather, "modulate:a", 0.0, 2.0)
		tween.tween_property(feather, "rotation", randf_range(-PI, PI), 2.0)
		tween.finished.connect(feather.queue_free)


## 泥土飞溅特效
func play_dirt_splash(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_DIRT, 15, 0.5, 200.0)


## 气泡上升特效
func play_bubble_rise(parent: Node, position: Vector2) -> void:
	for i in range(4):
		var bubble = ColorRect.new()
		bubble.size = Vector2(5, 5)
		bubble.color = COLOR_BUBBLE
		bubble.global_position = position + Vector2(randf_range(-20, 20), 0)
		bubble.name = "Bubble"
		parent.add_child(bubble)
		
		var target: Vector2 = bubble.position + Vector2(randf_range(-10, 10), randf_range(-60, -100))
		var tween: Tween = parent.create_tween()
		tween.set_parallel(true)
		tween.tween_property(bubble, "position", target, 1.2)
		tween.tween_property(bubble, "modulate:a", 0.0, 1.2)
		tween.tween_property(bubble, "scale", Vector2(1.5, 1.5), 1.2)
		tween.finished.connect(bubble.queue_free)


## 尘埃粒子
func play_dust_float(parent: Node, position: Vector2) -> void:
	for i in range(3):
		var dust = ColorRect.new()
		dust.size = Vector2(2, 2)
		dust.color = COLOR_DUST
		dust.global_position = position + Vector2(randf_range(-15, 15), randf_range(-10, 5))
		dust.name = "Dust"
		parent.add_child(dust)
		
		var target: Vector2 = dust.position + Vector2(randf_range(-5, 5), randf_range(-20, -40))
		var tween: Tween = parent.create_tween()
		tween.set_parallel(true)
		tween.tween_property(dust, "position", target, 2.5)
		tween.tween_property(dust, "modulate:a", 0.0, 2.5)
		tween.finished.connect(dust.queue_free)


## 治疗绿光特效
func play_heal_glow(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_HEAL, 10, 0.7, 70.0)


## BOSS登场红色警告特效
func play_boss_intro(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, COLOR_BOSS_INTRO, 30, 1.0, 250.0)
	play_impact_ring(parent, position, Color(1, 0.2, 0.1, 0.7), 120.0)


## 道具拾取特效
func play_item_pickup(parent: Node, position: Vector2) -> void:
	_create_simple_burst(parent, position, Color(1, 0.9, 0.2, 0.8), 8, 0.4, 50.0)


## 经验值获取小提示
func play_exp_gain(parent: Node, position: Vector2, exp_amount: int) -> void:
	var label = Label.new()
	label.text = "+%d EXP" % exp_amount
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	label.add_theme_color_override("font_color", Color(0.6, 0.8, 1, 0.9))
	label.add_theme_font_size_override("font_size", 12)
	label.position = parent.to_local(position) - Vector2(30, 0)
	label.name = "ExpLabel"
	parent.add_child(label)
	
	var tween: Tween = parent.create_tween()
	tween.set_parallel(true)
	tween.tween_property(label, "position:y", label.position.y - 40, 0.8)
	tween.tween_property(label, "modulate:a", 0.0, 0.8)
	tween.finished.connect(label.queue_free)


# ========== 环境粒子系统 ==========

func create_ambient_particles(parent: Node, position: Vector2, effect_type: String, rate: float = 2.0) -> Node:
	var ambient = Node2D.new()
	ambient.name = "AmbientParticles_%s" % effect_type
	ambient.position = parent.to_local(position) if parent is Node2D else position
	parent.add_child(ambient)
	
	var timer = Timer.new()
	timer.wait_time = 1.0 / maxf(rate, 0.1)
	timer.one_shot = false
	timer.name = "AmbientTimer"
	ambient.add_child(timer)
	
	match effect_type:
		"dust":
			timer.timeout.connect(func():
				if is_instance_valid(parent):
					var offset = Vector2(randf_range(-30, 30), randf_range(-20, 10))
					play_dust_float(parent, ambient.global_position + offset)
			)
		"bubble":
			timer.timeout.connect(func():
				if is_instance_valid(parent):
					var offset = Vector2(randf_range(-40, 40), randf_range(0, 5))
					play_bubble_rise(parent, ambient.global_position + offset)
			)
		_:
			push_warning("ParticleManager: 未知环境效果类型 '%s'" % effect_type)
	
	timer.start()
	return ambient


func remove_ambient_particles(ambient_node: Node) -> void:
	if is_instance_valid(ambient_node):
		ambient_node.queue_free()