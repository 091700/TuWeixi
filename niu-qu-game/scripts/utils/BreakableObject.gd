# BreakableObject.gd - 可破坏物体节点
# 挂载到StaticBody2D上，接受玩家/队友攻击后可被破坏
# 类型：木箱(wooden_box)、岩石(rock)、粪堆(dung_pile)、藤蔓(vine)
extends StaticBody2D

@export var breakable_type: String = "wooden_box"  # 物体类型（对应DataManager数据）
@export var current_hp: int = 20                     # 当前耐久值
@export var drop_on_destroy: bool = true             # 是否掉落道具

# 运行时状态
var _is_destroyed: bool = false
var _max_hp: int = 20
var _data: Dictionary = {}
var _visual_nodes: Array = []
var _hit_flash_timer: float = 0.0

func _ready() -> void:
	# 添加到breakable组
	add_to_group("breakable")
	
	# 获取数据
	_data = DataManager.get_breakable_data(breakable_type)
	if not _data.is_empty():
		_max_hp = _data.get("hp", 20)
		if current_hp <= 0:
			current_hp = _max_hp
	else:
		_max_hp = 20
	
	# 设置碰撞层（地形层3）
	collision_layer = 4  # Layer 3
	collision_mask = 0
	
	# 创建程序化外观
	_create_appearance()
	
	# 检查是否已从存档中标记为已破坏
	_check_already_destroyed()
	
	print("BreakableObject: 可破坏物体 '%s' 初始化, HP=%d/%d" % [breakable_type, current_hp, _max_hp])


## 创建程序化外观
func _create_appearance() -> void:
	var color: Color = _data.get("visual_color", Color(0.5, 0.35, 0.2))
	
	# 创建视觉层（放在碰撞体上方）
	var visual_container = Node2D.new()
	visual_container.name = "Visuals"
	visual_container.position = Vector2.ZERO
	add_child(visual_container)
	
	match breakable_type:
		"wooden_box":
			_create_wooden_box(visual_container, color)
		"rock":
			_create_rock(visual_container, color)
		"dung_pile":
			_create_dung_pile(visual_container, color)
		"vine":
			_create_vine(visual_container, color)
		_:
			_create_generic(visual_container, color)


## 创建木箱外观 → 改为💩粪堆螺旋形状
func _create_wooden_box(parent: Node2D, _color: Color) -> void:
	# 💩主体：棕色底色+螺旋堆叠
	var body = ColorRect.new()
	body.size = Vector2(32, 28)
	body.position = Vector2(-16, -36)
	body.color = Color(0.4, 0.25, 0.12, 1)
	body.name = "PoopBody"
	parent.add_child(body)
	_visual_nodes.append(body)
	
	# 顶部螺旋小节
	var top_spiral = ColorRect.new()
	top_spiral.size = Vector2(16, 10)
	top_spiral.position = Vector2(-8, -44)
	top_spiral.color = Color(0.35, 0.2, 0.1, 0.6)
	top_spiral.name = "PoopTop"
	parent.add_child(top_spiral)
	_visual_nodes.append(top_spiral)
	
	# 螺旋纹理线
	var spiral_line = ColorRect.new()
	spiral_line.size = Vector2(28, 3)
	spiral_line.position = Vector2(-14, -26)
	spiral_line.color = Color(0.25, 0.15, 0.08, 0.7)
	spiral_line.name = "SpiralLine"
	parent.add_child(spiral_line)
	_visual_nodes.append(spiral_line)
	
	# 💩表情标签
	var emoji = Label.new()
	emoji.text = "💩"
	emoji.position = Vector2(-12, -48)
	emoji.size = Vector2(24, 24)
	emoji.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	emoji.add_theme_font_size_override("font_size", 16)
	emoji.name = "PoopEmoji"
	parent.add_child(emoji)
	_visual_nodes.append(emoji)


## 创建岩石外观
func _create_rock(parent: Node2D, color: Color) -> void:
	# 不规则石头外观（用多个矩形模拟）
	for i in range(3):
		var rock_part = ColorRect.new()
		rock_part.size = Vector2(24 + i * 4, 16 + i * 2)
		rock_part.position = Vector2(-(12 + i * 2), -(28 + i * 3))
		rock_part.color = color
		rock_part.name = "RockPart%d" % i
		parent.add_child(rock_part)
		_visual_nodes.append(rock_part)


## 创建粪堆外观
func _create_dung_pile(parent: Node2D, color: Color) -> void:
	# 多个圆形/椭圆模拟粪堆
	for i in range(4):
		var pile_part = ColorRect.new()
		pile_part.size = Vector2(14 + i * 3, 12 + i * 2)
		pile_part.position = Vector2(-(14 + i * 1.5), -(8 + i * 4))
		pile_part.color = color
		pile_part.name = "DungPart%d" % i
		parent.add_child(pile_part)
		_visual_nodes.append(pile_part)
	
	# 小黑点装饰
	for i in range(3):
		var dot = ColorRect.new()
		dot.size = Vector2(4, 4)
		dot.position = Vector2(randf_range(-10, 10), randf_range(-30, -15))
		dot.color = Color(0.1, 0.05, 0.02)
		dot.name = "Dot%d" % i
		parent.add_child(dot)
		_visual_nodes.append(dot)


## 创建藤蔓外观
func _create_vine(parent: Node2D, color: Color) -> void:
	# 长条形藤蔓
	for i in range(3):
		var vine_part = ColorRect.new()
		vine_part.size = Vector2(6, 50)
		vine_part.position = Vector2(-3 + i * 8 - 8, -50)
		vine_part.color = color
		vine_part.name = "VinePart%d" % i
		parent.add_child(vine_part)
		_visual_nodes.append(vine_part)


## 创建通用外观
func _create_generic(parent: Node2D, color: Color) -> void:
	var rect = ColorRect.new()
	rect.size = Vector2(36, 36)
	rect.position = Vector2(-18, -36)
	rect.color = color
	rect.name = "GenericBreakable"
	parent.add_child(rect)
	_visual_nodes.append(rect)


## 检查是否已从存档中标记为已破坏
func _check_already_destroyed() -> void:
	# 从SaveManager的待恢复数据中检查
	var pending_data: Variant = get_tree().root.get_meta("_pending_save_data", null)
	if pending_data != null and typeof(pending_data) == TYPE_DICTIONARY:
		var destroyed_list: Array = pending_data.get("destroyed_breakables", [])
		if destroyed_list.has(_get_unique_id()):
			_destroy(false, false)
			return


## 生成唯一ID（基于位置）
func _get_unique_id() -> String:
	return "%s_%.0f_%.0f" % [breakable_type, global_position.x, global_position.y]


## 受到伤害（玩家攻击或队友攻击）
func take_damage(damage: int, _knockback_dir: Vector2 = Vector2.ZERO) -> void:
	if _is_destroyed:
		return
	
	current_hp -= damage
	_play_hit_flash()
	
	if current_hp <= 0:
		_destroy(true, true)
	
	print("BreakableObject: %s 受到伤害 %d, 剩余HP=%d" % [breakable_type, damage, current_hp])


## 由蚯蚓工兵专门破坏
func break_by_earthworm() -> void:
	if _is_destroyed:
		return
	
	# 蚯蚓可破坏所有岩石类
	_destroy(true, true)


## 破坏物体
func _destroy(play_effect: bool = true, drop_items: bool = true) -> void:
	if _is_destroyed:
		return
	_is_destroyed = true
	
	print("BreakableObject: %s 被破坏!" % breakable_type)
	
	# 掉落道具
	if drop_items and drop_on_destroy:
		_spawn_drops()
	
	# 播放破坏特效
	if play_effect:
		_play_destroy_effect()
	
	# 播放音效
	AudioManager.play_sfx("enemy_die")
	
	# 消除碰撞体
	collision_layer = 0
	
	# 视觉淡出并移除
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.3)
	tween.tween_property(self, "scale", Vector2(0.2, 0.2), 0.2)
	tween.finished.connect(queue_free)


## 生成掉落道具
func _spawn_drops() -> void:
	var drop_table: Array = _data.get("drop_items", [])
	var drops: Array = DataManager.roll_drops(drop_table)
	
	for item_id in drops:
		if item_id == "":
			continue
		_spawn_item(item_id)


## 在当前位置生成道具
func _spawn_item(item_id: String) -> void:
	# 创建一个道具拾取节点
	var item = Area2D.new()
	item.name = "DropItem_%s" % item_id
	item.global_position = global_position + Vector2(randf_range(-20, 20), -30)
	item.collision_layer = 0
	item.collision_mask = 1  # 检测玩家
	
	var shape = CollisionShape2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 16
	shape.shape = circle
	item.add_child(shape)
	
	# 道具视觉
	var visual = ColorRect.new()
	visual.size = Vector2(20, 20)
	visual.position = Vector2(-10, -10)
	var item_data: Dictionary = DataManager.get_item_data(item_id)
	visual.color = item_data.get("icon_color", Color.WHITE)
	visual.name = "ItemVisual"
	item.add_child(visual)
	
	# 物品名称标签
	var name_label = Label.new()
	name_label.text = item_data.get("name", item_id)
	name_label.position = Vector2(-40, 12)
	name_label.size = Vector2(100, 16)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_color_override("font_color", Color.WHITE)
	name_label.add_theme_font_size_override("font_size", 10)
	name_label.name = "ItemName"
	item.add_child(name_label)
	
	# 连接拾取信号
	item.body_entered.connect(_on_drop_item_picked_up.bind(item, item_id))
	
	# 添加到场景
	var parent: Node = get_parent()
	if parent:
		parent.add_child(item)
	
	# 5秒后自动消失
	var timer = get_tree().create_timer(5.0)
	timer.timeout.connect(func():
		if is_instance_valid(item):
			# 闪烁警告
			var blink = create_tween()
			blink.set_loops(6)
			blink.tween_property(item, "modulate:a", 0.2, 0.15)
			blink.tween_property(item, "modulate:a", 1.0, 0.15)
			blink.finished.connect(item.queue_free)
	)


## 道具被玩家拾取
func _on_drop_item_picked_up(body: Node2D, item: Area2D, item_id: String) -> void:
	if not body.is_in_group("player"):
		return
	
	# 添加到玩家背包
	if body.has_method("add_item"):
		body.add_item(item_id, 1)
	else:
		# 简单拾取：直接使用道具效果
		_apply_item_effect(body, item_id)
	
	# 播放入手音效
	AudioManager.play_sfx("pickup")
	
	# 发射信号
	Global.item_collected.emit(item_id, 1)
	
	# 移除道具节点
	item.queue_free()


## 直接应用道具效果
func _apply_item_effect(player: Node2D, item_id: String) -> void:
	var item_data: Dictionary = DataManager.get_item_data(item_id)
	if item_data.is_empty():
		return
	
	var params: Dictionary = item_data.get("params", {})
	
	# 恢复HP
	if params.has("heal_hp") and player.has_method("heal"):
		player.heal(params["heal_hp"])
	
	# 恢复MP
	if params.has("heal_mp"):
		var current_mp: int = player.get("current_mp")
		var max_mp: int = player.get("max_mp")
		player.set("current_mp", mini(current_mp + params["heal_mp"], max_mp))
	
	# 永久MP加成
	if params.has("permanent_mp_bonus"):
		player.max_mp += params["permanent_mp_bonus"]
		player.current_mp += params["permanent_mp_bonus"]


## 播放破坏特效
func _play_destroy_effect() -> void:
	# 粒子爆散效果
	var particles = GPUParticles2D.new()
	particles.emitting = true
	particles.one_shot = true
	particles.amount = 12
	particles.lifetime = 0.6
	particles.explosiveness = 1.0
	particles.position = Vector2.ZERO
	particles.name = "DestroyParticles"
	
	var material = ParticleProcessMaterial.new()
	material.gravity = Vector2(0, 200)
	material.initial_velocity_min = 40
	material.initial_velocity_max = 120
	material.direction = 0
	material.spread = 180
	material.color = _data.get("visual_color", Color(0.5, 0.35, 0.2))
	particles.process_material = material
	
	add_child(particles)
	particles.emitting = true
	
	var timer = get_tree().create_timer(1.5)
	timer.timeout.connect(particles.queue_free)


## 播放受击闪烁
func _play_hit_flash() -> void:
	var tween = create_tween()
	tween.tween_property(self, "modulate", Color(2, 2, 2), 0.05)
	tween.tween_property(self, "modulate", Color(1, 1, 1), 0.1)


## 检查破坏条件（供外部查询）
func can_break_by_player() -> bool:
	var req: String = _data.get("break_requirement", "attack")
	return req == "attack"  # 玩家可破坏attack类型

func can_break_by_earthworm() -> bool:
	var req: String = _data.get("break_requirement", "attack")
	if req == "earthworm_only":
		return true
	return req == "attack"

func is_destroyed() -> bool:
	return _is_destroyed