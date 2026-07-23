# CollisionZoneManager.gd - 碰撞区域管理器
# 挂载到关卡场景的Node2D上，在_ready时根据collider_data数组动态创建所有碰撞体
# 支持类型:
#   wall: 实心墙壁（StaticBody2D）
#   floor: 地面（StaticBody2D，与wall相同实现）
#   death: 即死深渊（Area2D，进入后调用玩家instant_death）
#   damage: 伤害区域（Area2D，持续扣血）
#   oneway: 单向平台（StaticBody2D + one_way_collision=true）
#   water: 水域减速区（Area2D，进入后移动减速）
#   checkpoint: 存档点/传送点（Area2D，触发信号）
#   pipe_entrance: 管道秘密入口（Area2D，传送到指定出口）
#   breakable: 可破坏障碍（留接口给模块四/七实现）
extends Node2D

# ========== 配置（在编辑器或代码中设置） ==========
@export var collider_data: Array = []

# ========== 引用缓存 ==========
var _player_ref: CharacterBody2D = null
var _built_colliders: Array = []  # 记录已创建的区域节点
var _is_built: bool = false       # 防止重复构建

# 碰撞层配置（Godot位掩码值，非层号）
# Layer 1(玩家) = 1, Layer 2(敌人) = 2, Layer 3(地形) = 4
const LAYER_PLAYER: int = 1   # 位0 = 层1
const LAYER_TERRAIN: int = 4  # 位2 = 层3


func _ready() -> void:
	# 不在此自动构建——由关卡脚本在 collider_data 填充后通过 call_deferred 触发
	pass


## 构建所有碰撞区域
func _build_colliders() -> void:
	if _is_built:
		push_warning("CollisionZoneManager: 碰撞区域已经构建过，跳过重复构建")
		return
	
	if collider_data.is_empty():
		push_warning("CollisionZoneManager: collider_data 为空，关卡没有碰撞区域")
		return
	
	_is_built = true
	
	# 查找玩家引用
	_player_ref = _find_player()
	
	for entry in collider_data:
		if entry.size() < 5:
			push_error("CollisionZoneManager: 碰撞数据格式错误，需要至少5个元素: %s" % str(entry))
			continue
		
		var type: String = entry[0]
		var x: float = entry[1]
		var y: float = entry[2]
		var w: float = entry[3]
		var h: float = entry[4]
		
		match type:
			"wall":
				_create_static_body(x, y, w, h, "wall")
			"floor":
				_create_static_body(x, y, w, h, "floor")
			"death":
				_create_death_zone(x, y, w, h)
			"damage":
				var dmg: int = entry[5] if entry.size() > 5 else 5
				_create_damage_zone(x, y, w, h, dmg)
			"oneway":
				_create_oneway_platform(x, y, w, h)
			"water":
				var slow: float = entry[5] if entry.size() > 5 else 0.5
				_create_water_zone(x, y, w, h, slow)
			"checkpoint":
				var cp_id: String = entry[5] if entry.size() > 5 else ""
				var is_save: bool = entry[6] if entry.size() > 6 else false
				_create_checkpoint(x, y, w, h, cp_id, is_save)
			"pipe_entrance":
				var pipe_target: String = entry[5] if entry.size() > 5 else ""
				_create_pipe_entrance(x, y, w, h, pipe_target)
			"breakable":
				var break_req: String = entry[5] if entry.size() > 5 else "attack"
				var breakable_hp: int = entry[6] if entry.size() > 6 else 30
				_create_breakable(x, y, w, h, break_req, breakable_hp)
			_:
				push_warning("CollisionZoneManager: 未知碰撞类型 '%s'，跳过" % type)
	
	print("CollisionZoneManager: 构建完成，共 %d 个碰撞区域" % _built_colliders.size())


## 查找场景中的玩家节点
func _find_player() -> CharacterBody2D:
	# 优先通过player组查找
	var players: Array = get_tree().get_nodes_in_group("player")
	if not players.is_empty():
		return players[0]
	
	# 递归搜索
	return _find_player_recursive(get_tree().root)


func _find_player_recursive(node: Node) -> CharacterBody2D:
	for child in node.get_children():
		if child is CharacterBody2D and child.is_in_group("player"):
			return child
		var found: CharacterBody2D = _find_player_recursive(child)
		if found:
			return found
	return null


# ========== 静态碰撞体（wall / floor） ==========

## 创建实心碰撞体（墙壁或地面）
func _create_static_body(x: float, y: float, w: float, h: float, label: String = "") -> void:
	var body = StaticBody2D.new()
	body.name = "StaticBody_%s" % label
	body.position = Vector2(x + w / 2.0, y + h / 2.0)
	body.collision_layer = LAYER_TERRAIN
	body.collision_mask = 0  # 地形不检测其他物体
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	body.add_child(shape)
	
	add_child(body)
	_built_colliders.append(body)


# ========== 即死区域（death） ==========

## 创建即死深渊区域
func _create_death_zone(x: float, y: float, w: float, h: float) -> void:
	var area = Area2D.new()
	area.name = "DeathZone"
	area.position = Vector2(x + w / 2.0, y + h / 2.0)
	area.collision_layer = 0     # 不产生碰撞
	area.collision_mask = LAYER_PLAYER  # 只检测玩家
	area.set_meta("zone_type", "death")
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	area.add_child(shape)
	
	# 连接信号——玩家进入即死
	area.body_entered.connect(_on_death_zone_body_entered)
	
	add_child(area)
	_built_colliders.append(area)


func _on_death_zone_body_entered(body: Node2D) -> void:
	if body.is_in_group("player") and body.has_method("instant_death"):
		print("CollisionZoneManager: 玩家进入即死区域")
		body.instant_death()


# ========== 伤害区域（damage） ==========

## 创建持续伤害区域（尖刺、酸液等），使用bind方式传递dps参数
func _create_damage_zone(x: float, y: float, w: float, h: float, damage_per_sec: int) -> void:
	var area = Area2D.new()
	area.name = "DamageZone"
	area.position = Vector2(x + w / 2.0, y + h / 2.0)
	area.collision_layer = 0
	area.collision_mask = LAYER_PLAYER
	area.set_meta("zone_type", "damage")
	area.set_meta("damage_per_sec", damage_per_sec)
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	area.add_child(shape)
	
	# 使用bind传递dps值
	area.body_entered.connect(_on_damage_zone_entered.bind(damage_per_sec))
	area.body_exited.connect(_on_damage_zone_exited.bind(damage_per_sec))
	
	add_child(area)
	_built_colliders.append(area)


func _on_damage_zone_entered(body: Node2D, dmg_per_sec: int) -> void:
	if body.is_in_group("player") and body.has_method("enter_damage_zone"):
		body.enter_damage_zone(dmg_per_sec)


func _on_damage_zone_exited(body: Node2D, dmg_per_sec: int) -> void:
	if body.is_in_group("player") and body.has_method("exit_damage_zone"):
		body.exit_damage_zone(dmg_per_sec)


# ========== 水域减速区（water） ==========

## 创建水域减速区
func _create_water_zone(x: float, y: float, w: float, h: float, slow_factor: float) -> void:
	var area = Area2D.new()
	area.name = "WaterZone"
	area.position = Vector2(x + w / 2.0, y + h / 2.0)
	area.collision_layer = 0
	area.collision_mask = LAYER_PLAYER
	area.set_meta("zone_type", "water")
	area.set_meta("slow_factor", slow_factor)
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	area.add_child(shape)
	
	# 连接信号——使用bind传递区域参数
	area.body_entered.connect(_on_water_zone_entered.bind(area))
	area.body_exited.connect(_on_water_zone_exited.bind(area))
	
	add_child(area)
	_built_colliders.append(area)


func _on_water_zone_entered(body: Node2D, zone: Area2D) -> void:
	if body.is_in_group("player") and body.has_method("enter_water_zone"):
		var slow: float = zone.get_meta("slow_factor", 0.5)
		body.enter_water_zone(slow)


func _on_water_zone_exited(body: Node2D, zone: Area2D) -> void:
	if body.is_in_group("player") and body.has_method("exit_water_zone"):
		var slow: float = zone.get_meta("slow_factor", 0.5)
		body.exit_water_zone(slow)


# ========== 单向平台（oneway） ==========

## 创建单向平台（可从下方穿过，上方可站立）
func _create_oneway_platform(x: float, y: float, w: float, h: float) -> void:
	var body = StaticBody2D.new()
	body.name = "OneWayPlatform"
	body.position = Vector2(x + w / 2.0, y + h / 2.0)
	body.collision_layer = LAYER_TERRAIN
	body.collision_mask = 0
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	shape.one_way_collision = true  # 关键：设置为单向碰撞
	body.add_child(shape)
	
	add_child(body)
	_built_colliders.append(body)


# ========== 存档点/传送点（checkpoint） ==========

## 创建存档点或传送点
## @param cp_id: 存档点/传送点ID
## @param is_save: 是否为存档点（true=存档，false=传送）
func _create_checkpoint(x: float, y: float, w: float, h: float, cp_id: String, is_save: bool) -> void:
	var area = Area2D.new()
	area.name = "Checkpoint_%s" % cp_id
	area.position = Vector2(x + w / 2.0, y + h / 2.0)
	area.collision_layer = 0
	area.collision_mask = LAYER_PLAYER
	area.set_meta("zone_type", "checkpoint")
	area.set_meta("checkpoint_id", cp_id)
	area.set_meta("is_save", is_save)
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	area.add_child(shape)
	
	# 连接信号
	area.body_entered.connect(_on_checkpoint_entered.bind(cp_id, is_save))
	
	add_child(area)
	_built_colliders.append(area)


func _on_checkpoint_entered(body: Node2D, cp_id: String, is_save: bool) -> void:
	if not body.is_in_group("player"):
		return
	
	print("CollisionZoneManager: 玩家到达%s: %s" % ["存档点" if is_save else "传送点", cp_id])
	Global.checkpoint_reached.emit(cp_id)
	
	# 6个关卡传送系统：击败当前BOSS才能进入下一关
	if cp_id.begins_with("cave_exit"):
		var current = Global.current_map
		if current == "cave_1":
			if not Global.story_flags.get("defeated_spider_queen", false):
				_show_blocked_message(body, "击败蜘蛛女王后才能通过！")
				return
			call_deferred("_deferred_switch_map", "cave_2")
		elif current == "cave_2":
			if not Global.story_flags.get("defeated_rooster_lord", false):
				_show_blocked_message(body, "击败大公鸡领主后才能通过！")
				return
			call_deferred("_deferred_switch_map", "sewer_1")
	elif cp_id.begins_with("sewer_to_farm"):
		var current = Global.current_map
		if current == "sewer_1":
			if not Global.story_flags.get("defeated_sewer_crocodile", false):
				_show_blocked_message(body, "击败下水道鳄鱼后才能通过！")
				return
			call_deferred("_deferred_switch_map", "sewer_2")
		elif current == "sewer_2":
			if not Global.story_flags.get("defeated_excavator_giant", false):
				_show_blocked_message(body, "击败挖掘机巨人后才能通过！")
				return
			call_deferred("_deferred_switch_map", "farm_1")
	elif cp_id.begins_with("farm_boss_entrance"):
		var current = Global.current_map
		if current == "farm_1":
			if not Global.story_flags.get("defeated_farmers_dog", false):
				_show_blocked_message(body, "击败农夫的狗后才能通过！")
				return
			call_deferred("_deferred_switch_map", "farm_2")
		elif current == "farm_2":
			if not Global.story_flags.get("defeated_cleaning_lady", false):
				_show_blocked_message(body, "击败保洁阿姨后才能获胜！")
				return
			# 游戏通关！
			_show_blocked_message(body, "恭喜通关！返回标题画面...")
			var t = get_tree().create_timer(2.0)
			t.timeout.connect(func(): SceneManager.go_to_title())
	elif cp_id.begins_with("sewer_secret"):
		call_deferred("_deferred_switch_map", "farm_1")
	elif is_save:
		if body.has_method("set_checkpoint"):
			body.set_checkpoint(cp_id)
	else:
		if body.has_method("set_checkpoint"):
			body.set_checkpoint(cp_id)


# ========== 管道入口（pipe_entrance） ==========

## 创建管道秘密入口
func _create_pipe_entrance(x: float, y: float, w: float, h: float, target_id: String) -> void:
	var area = Area2D.new()
	area.name = "PipeEntrance_%s" % target_id
	area.position = Vector2(x + w / 2.0, y + h / 2.0)
	area.collision_layer = 0
	area.collision_mask = LAYER_PLAYER
	area.set_meta("zone_type", "pipe_entrance")
	area.set_meta("target_id", target_id)
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	area.add_child(shape)
	
	area.body_entered.connect(_on_pipe_entered.bind(target_id))
	
	add_child(area)
	_built_colliders.append(area)


func _deferred_switch_map(map_name: String) -> void:
	# 使用全局Timer避免CollisionZoneManager被释放后调用失败
	var t = get_tree().create_timer(0.01)
	t.timeout.connect(func(): SceneManager.switch_map(map_name))


func _show_blocked_message(body: Node2D, msg: String) -> void:
	var label = Label.new()
	label.text = msg
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_color_override("font_color", Color(1, 0.3, 0.3, 1))
	label.add_theme_font_size_override("font_size", 20)
	label.global_position = body.global_position + Vector2(-150, -80)
	label.size = Vector2(300, 40)
	get_parent().add_child(label)
	var tween = create_tween()
	tween.tween_property(label, "modulate:a", 0.0, 2.0)
	tween.tween_property(label, "position:y", label.position.y - 30, 2.0)
	tween.finished.connect(label.queue_free)


func _on_pipe_entered(body: Node2D, target_id: String) -> void:
	if body.is_in_group("player"):
		print("CollisionZoneManager: 玩家进入管道: %s" % target_id)
		# 管道传送逻辑——后续模块完善（同一地图内传送）
		# 暂定：如果是sewer_secret_01，切换到农田
	if target_id == "sewer_secret_01":
			call_deferred("_deferred_switch_map", "farm_1")


# ========== 可破坏障碍物（breakable） ==========

## 创建可破坏障碍物
## @param break_req: 破坏要求（"attack"=普通攻击, "earthworm_only"=需蚯蚓工兵）
## @param hp: 障碍物耐久值
func _create_breakable(x: float, y: float, w: float, h: float, break_req: String, hp: int) -> void:
	# 使用StaticBody2D作为障碍物
	var body = StaticBody2D.new()
	body.name = "Breakable_%s" % break_req
	body.position = Vector2(x + w / 2.0, y + h / 2.0)
	body.collision_layer = LAYER_TERRAIN
	body.collision_mask = 0
	body.set_meta("zone_type", "breakable")
	body.set_meta("break_requirement", break_req)
	body.set_meta("breakable_hp", hp)
	
	var shape = CollisionShape2D.new()
	var rect = RectangleShape2D.new()
	rect.size = Vector2(w, h)
	shape.shape = rect
	body.add_child(shape)
	
	# 添加视觉效果（棕色矩形表示可破坏）
	var visual = ColorRect.new()
	visual.size = Vector2(w, h)
	visual.position = Vector2(-w / 2.0, -h / 2.0)
	visual.color = Color(0.5, 0.3, 0.1, 0.8)
	visual.name = "Visual"
	body.add_child(visual)
	
	add_child(body)
	_built_colliders.append(body)