# CollectibleItem.gd - 收集品节点
# 挂载到Area2D上，玩家进入范围后自动触发收集逻辑
# 支持：童年照片、古老粪球、班级合照碎片
extends Area2D

@export var collectible_id: String = ""       # 收集品ID（对应DataManager中的数据）
@export var auto_collect: bool = true         # 是否自动收集（true=进入即收集）
@export var show_prompt: bool = true          # 是否显示收集提示
@export var play_effect: bool = true          # 是否播放收集特效

# 节点引用
var _sprite: Sprite2D = null
var _label: Label = null
var _is_collected: bool = false
var _float_timer: float = 0.0

func _ready() -> void:
	# 添加到collectible组
	add_to_group("collectible")
	
	# 设置碰撞层
	collision_layer = 0  # 不产生碰撞
	collision_mask = 1   # 只检测玩家（Layer 1）
	
	# 创建视觉外观（程序化生成）
	_create_appearance()
	
	# 连接信号
	body_entered.connect(_on_body_entered)
	
	# 如果已收集过（从存档恢复），隐藏
	_check_already_collected()
	
	print("CollectibleItem: 收集品 '%s' 已初始化" % collectible_id)


## 创建程序化外观
func _create_appearance() -> void:
	var data: Dictionary = DataManager.get_collectible_data(collectible_id)
	if data.is_empty():
		return
	
	# 创建视觉Sprite
	_sprite = Sprite2D.new()
	_sprite.name = "CollectibleSprite"
	
	var col_type: String = data.get("type", "")
	
	# 根据类型生成不同的视觉
	match col_type:
		"photo":
			_create_photo_appearance()
		"artifact":
			_create_artifact_appearance()
		"class_photo":
			_create_class_photo_appearance()
		_:
			_create_generic_appearance()
	
	# 添加发光效果
	var glow = ColorRect.new()
	glow.size = Vector2(24, 24)
	glow.position = Vector2(-12, -30)
	glow.color = Color(1, 0.9, 0.3, 0.3)
	glow.name = "Glow"
	add_child(glow)


## 创建照片外观
func _create_photo_appearance() -> void:
	# 小照片卡片外观
	var bg = ColorRect.new()
	bg.size = Vector2(20, 24)
	bg.position = Vector2(-10, -28)
	bg.color = Color(0.95, 0.95, 0.9)
	bg.name = "PhotoCard"
	add_child(bg)
	
	# 照片上的"图像"区域
	var img = ColorRect.new()
	img.size = Vector2(16, 14)
	img.position = Vector2(-8, -26)
	img.color = Color(0.7, 0.8, 0.9)
	img.name = "PhotoImage"
	bg.add_child(img)
	
	_sprite = null  # 不使用Sprite2D


## 创建古老粪球外观
func _create_artifact_appearance() -> void:
	var circle = ColorRect.new()
	circle.size = Vector2(24, 24)
	circle.position = Vector2(-12, -30)
	circle.color = Color(0.35, 0.2, 0.1)
	circle.name = "ArtifactCircle"
	add_child(circle)
	
	_sprite = null


## 创建班级合照碎片外观
func _create_class_photo_appearance() -> void:
	var bg = ColorRect.new()
	bg.size = Vector2(18, 16)
	bg.position = Vector2(-9, -26)
	bg.color = Color(0.85, 0.85, 0.8)
	bg.name = "ClassPhotoFrag"
	add_child(bg)
	_sprite = null


## 创建通用外观
func _create_generic_appearance() -> void:
	var bg = ColorRect.new()
	bg.size = Vector2(20, 20)
	bg.position = Vector2(-10, -28)
	bg.color = Color(0.5, 0.7, 0.5)
	bg.name = "GenericItem"
	add_child(bg)


## 检查该收集品是否已被收集（使用Global.collected_items防止重复生成）
func _check_already_collected() -> void:
	# 用Global全局数组做去重
	if collectible_id in Global.collected_items:
		_is_collected = true
		_set_collected_visual()
		monitoring = false
		print("CollectibleItem: '%s' 已收集过，隐藏" % collectible_id)


## 设置已收集的视觉状态（半透明、缩小）
func _set_collected_visual() -> void:
	modulate.a = 0.2
	scale = Vector2(0.5, 0.5)
	if _sprite:
		_sprite.modulate.a = 0.2


## 玩家进入收集范围
func _on_body_entered(body: Node2D) -> void:
	if _is_collected:
		return
	
	if not body.is_in_group("player"):
		return
	
	_collect(body)


## 执行收集逻辑
func _collect(player: Node2D) -> void:
	_is_collected = true
	
	# 记录到Global防止重复生成
	if not collectible_id in Global.collected_items:
		Global.collected_items.append(collectible_id)
	
	var data: Dictionary = DataManager.get_collectible_data(collectible_id)
	var item_name: String = data.get("name", collectible_id)
	
	# 发射收集信号
	Global.collectible_found.emit(collectible_id)
	Global.item_collected.emit(collectible_id, 1)
	
	# 播放音效
	AudioManager.play_sfx("pickup")
	
	# 显示收集提示
	if show_prompt:
		_show_collect_notification(item_name, data.get("description", ""))
	
	# 播放收集特效
	if play_effect:
		_play_collect_effect()
	
	# 给予经验值奖励（每个收集品50EXP）
	if player.has_method("gain_exp"):
		player.gain_exp(50)
	
	# 特殊处理：检查是否集齐
	_check_completion()
	
	print("CollectibleItem: 收集品 '%s' 已收集" % item_name)
	
	# 隐藏节点
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.3)
	tween.tween_property(self, "scale", Vector2(1.5, 1.5), 0.2)
	tween.parallel().tween_property(self, "modulate:a", 0.0, 0.2)
	tween.finished.connect(queue_free)


## 显示收集通知弹窗
func _show_collect_notification(item_name: String, description: String) -> void:
	var hud: CanvasLayer = get_tree().get_first_node_in_group("hud")
	if hud and hud.has_method("show_collectible_notification"):
		hud.show_collectible_notification(item_name, description)
	else:
		# 兜底：创建一个简单的浮动Label
		_show_fallback_notification(item_name)


## 兜底通知显示
func _show_fallback_notification(text: String) -> void:
	var label = Label.new()
	label.text = "获得: %s" % text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_color_override("font_color", Color(1, 0.9, 0.2))
	label.add_theme_font_size_override("font_size", 16)
	label.position = Vector2(400, 200)
	label.size = Vector2(480, 40)
	label.name = "CollectNotice"
	add_child(label)
	
	var tween = create_tween()
	tween.tween_property(label, "position:y", 160, 1.5)
	tween.parallel().tween_property(label, "modulate:a", 0.0, 1.5)
	tween.finished.connect(label.queue_free)


## 播放收集特效
func _play_collect_effect() -> void:
	# 简单粒子效果
	var particles = GPUParticles2D.new()
	particles.emitting = true
	particles.one_shot = true
	particles.amount = 8
	particles.lifetime = 0.5
	particles.explosiveness = 1.0
	particles.position = Vector2.ZERO
	particles.name = "CollectParticles"
	
	var material = ParticleProcessMaterial.new()
	material.gravity = Vector2(0, -80)
	material.initial_velocity_min = 30
	material.initial_velocity_max = 80
	material.direction = 0
	material.spread = 180
	material.color = Color(1, 0.9, 0.2)
	particles.process_material = material
	
	add_child(particles)
	particles.emitting = true
	
	# 自动清理
	var timer = get_tree().create_timer(1.0)
	timer.timeout.connect(particles.queue_free)


## 检查集齐条件（更新Global标记）
func _check_completion() -> void:
	# 需要获取所有已收集的收集品状态
	# 通过遍历场景中所有已收集的collectible节点
	_update_collection_flags()


## 更新全局收集标记
func _update_collection_flags() -> void:
	# 收集所有已收集的收集品ID
	var collected_ids: Array = []
	var tree = get_tree()
	for node in tree.get_nodes_in_group("collectible"):
		if node.has_method("is_collected") and node.is_collected():
			collected_ids.append(node.collectible_id)
		elif node.get("_is_collected"):
			collected_ids.append(node.collectible_id)
	
	# 构建字典供DataManager检查
	var collected_dict: Dictionary = {}
	for id in collected_ids:
		collected_dict[id] = true
	# 加上刚收集的
	collected_dict[collectible_id] = true
	
	# 检查全部5张照片
	if DataManager.has_all_photos(collected_dict):
		Global.story_flags["found_all_photos"] = true
		print("CollectibleItem: 全部5张童年照片收集完毕！")
	
	# 检查古老粪球
	if collected_dict.get("ancient_dung_ball", false):
		Global.story_flags["found_ancient_dung_ball"] = true
	
	# 检查全部班级合照
	if DataManager.has_all_class_photos(collected_dict):
		print("CollectibleItem: 全部班级合照碎片拼齐！彩蛋房间开启")
		# 拼接合照的事件（通过story_flag触发）


## 是否已收集（供外部查询）
func is_collected() -> bool:
	return _is_collected