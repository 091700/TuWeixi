# SceneInteractable.gd - 场景交互元素
# 挂载到Area2D或StaticBody2D上，实现各类场景交互
# 类型：
#   switch: 踩踏开关，触发对应门/机关
#   push_box: 可推动的箱子（压力板谜题）
#   mushroom_spring: 弹簧蘑菇，弹飞玩家
#   pipe_teleport: 管道入口，传送到出口
#   glowing_moss: 发光苔藓，恢复MP（一次性）
#   checkpoint_altar: 存档祭坛（可视化的存档点）
#   hidden_door: 隐藏门（满足条件后显现）
extends Area2D

@export var interact_type: String = "switch"       # 交互类型
@export var interact_id: String = ""                # 交互物ID
@export var target_id: String = ""                  # 目标ID（开关→门、管道入口→出口等）
@export var param_float: float = 0.0                # 通用浮点参数（弹力、恢复量等）
@export var one_shot: bool = true                   # 是否一次性（用后消失）
@export var required_skill: String = ""             # 需要的技能（double_jump/dash/wall_jump等）

# 运行时状态
var _is_triggered: bool = false
var _is_active: bool = true
var _linked_target: Node = null                     # 关联的目标节点
var _visual_nodes: Array = []
var _player_ref: CharacterBody2D = null

func _ready() -> void:
	add_to_group("interactable")
	
	# 设置碰撞层
	collision_layer = 0
	collision_mask = 1  # 检测玩家
	
	# 创建程序化外观
	_create_appearance()
	
	# 查找关联目标
	if target_id != "":
		_find_linked_target()
	
	# 连接信号
	match interact_type:
		"switch", "mushroom_spring", "pipe_teleport", "checkpoint_altar", "glowing_moss", "hidden_door":
			body_entered.connect(_on_body_entered)
		"push_box":
			# push_box 由玩家推动处理，不连接body_entered
			pass
	
	print("SceneInteractable: '%s' (类型=%s) 已初始化" % [interact_id, interact_type])


## 创建程序化外观
func _create_appearance() -> void:
	var visual_container = Node2D.new()
	visual_container.name = "Visuals"
	visual_container.position = Vector2.ZERO
	add_child(visual_container)
	
	match interact_type:
		"switch":
			_create_switch_appearance(visual_container)
		"push_box":
			_create_push_box_appearance(visual_container)
		"mushroom_spring":
			_create_mushroom_appearance(visual_container)
		"pipe_teleport":
			_create_pipe_appearance(visual_container)
		"glowing_moss":
			_create_moss_appearance(visual_container)
		"checkpoint_altar":
			_create_checkpoint_altar_appearance(visual_container)
		"hidden_door":
			_create_hidden_door_appearance(visual_container)
		_:
			_create_generic_appearance(visual_container)


## 开关外观（踩踏板）
func _create_switch_appearance(parent: Node2D) -> void:
	var base = ColorRect.new()
	base.size = Vector2(40, 10)
	base.position = Vector2(-20, -10)
	base.color = Color(0.3, 0.3, 0.35)
	base.name = "SwitchBase"
	parent.add_child(base)
	_visual_nodes.append(base)
	
	var button = ColorRect.new()
	button.size = Vector2(20, 6)
	button.position = Vector2(-10, -8)
	button.color = Color(0.9, 0.3, 0.1)
	button.name = "SwitchButton"
	parent.add_child(button)
	_visual_nodes.append(button)


## 推箱子外观
func _create_push_box_appearance(parent: Node2D) -> void:
	var body = ColorRect.new()
	body.size = Vector2(48, 48)
	body.position = Vector2(-24, -48)
	body.color = Color(0.55, 0.35, 0.2)
	body.name = "PushBoxBody"
	parent.add_child(body)
	_visual_nodes.append(body)
	
	# 边框
	var border = ReferenceRect.new()
	border.size = Vector2(46, 46)
	border.position = Vector2(-23, -47)
	border.border_color = Color(0.3, 0.2, 0.1, 0.8)
	border.border_width = 2
	border.editor_only = false
	border.name = "PushBoxBorder"
	parent.add_child(border)
	_visual_nodes.append(border)
	
	# 箭头指示
	var arrow = Label.new()
	arrow.text = "←→"
	arrow.position = Vector2(-15, -35)
	arrow.add_theme_color_override("font_color", Color(0.2, 0.2, 0.3))
	arrow.add_theme_font_size_override("font_size", 14)
	arrow.name = "PushBoxArrow"
	parent.add_child(arrow)


## 弹簧蘑菇外观
func _create_mushroom_appearance(parent: Node2D) -> void:
	# 菌柄
	var stem = ColorRect.new()
	stem.size = Vector2(14, 20)
	stem.position = Vector2(-7, -20)
	stem.color = Color(0.9, 0.85, 0.7)
	stem.name = "MushroomStem"
	parent.add_child(stem)
	
	# 菌盖
	var cap = ColorRect.new()
	cap.size = Vector2(36, 16)
	cap.position = Vector2(-18, -28)
	cap.color = Color(0.8, 0.2, 0.1)
	cap.name = "MushroomCap"
	parent.add_child(cap)


## 管道入口外观
func _create_pipe_appearance(parent: Node2D) -> void:
	# 管道主体
	var pipe = ColorRect.new()
	pipe.size = Vector2(40, 60)
	pipe.position = Vector2(-20, -60)
	pipe.color = Color(0.35, 0.35, 0.4)
	pipe.name = "PipeBody"
	parent.add_child(pipe)
	
	# 管道内
	var inner = ColorRect.new()
	inner.size = Vector2(30, 56)
	inner.position = Vector2(-15, -58)
	inner.color = Color(0.05, 0.05, 0.08)
	inner.name = "PipeInner"
	parent.add_child(inner)
	
	# 箭头标记
	var arrow = Label.new()
	arrow.text = "↓"
	arrow.position = Vector2(-10, -45)
	arrow.add_theme_color_override("font_color", Color(0.5, 0.8, 0.5))
	arrow.add_theme_font_size_override("font_size", 18)
	arrow.name = "PipeArrow"
	parent.add_child(arrow)


## 发光苔藓外观
func _create_moss_appearance(parent: Node2D) -> void:
	for i in range(5):
		var moss = ColorRect.new()
		moss.size = Vector2(8 + randi() % 8, 6 + randi() % 4)
		moss.position = Vector2(randf_range(-15, 15), randf_range(-20, -5))
		moss.color = Color(0.3, 0.9, 0.4, 0.7)
		moss.name = "Moss%d" % i
		parent.add_child(moss)
	
	# 发光效果
	var glow = ColorRect.new()
	glow.size = Vector2(30, 30)
	glow.position = Vector2(-15, -20)
	glow.color = Color(0.3, 1, 0.4, 0.15)
	glow.name = "MossGlow"
	parent.add_child(glow)
	_visual_nodes.append(glow)


## 存档祭坛外观
func _create_checkpoint_altar_appearance(parent: Node2D) -> void:
	var base = ColorRect.new()
	base.size = Vector2(50, 12)
	base.position = Vector2(-25, -12)
	base.color = Color(0.6, 0.5, 0.3)
	base.name = "AltarBase"
	parent.add_child(base)
	
	var pillar = ColorRect.new()
	pillar.size = Vector2(10, 30)
	pillar.position = Vector2(-5, -42)
	pillar.color = Color(0.7, 0.6, 0.4)
	pillar.name = "AltarPillar"
	parent.add_child(pillar)
	
	# 发光球
	var orb = ColorRect.new()
	orb.size = Vector2(16, 16)
	orb.position = Vector2(-8, -50)
	orb.color = Color(0.4, 0.7, 1, 0.8)
	orb.name = "AltarOrb"
	parent.add_child(orb)
	_visual_nodes.append(orb)


## 隐藏门外观
func _create_hidden_door_appearance(parent: Node2D) -> void:
	var door = ColorRect.new()
	door.size = Vector2(50, 80)
	door.position = Vector2(-25, -80)
	door.color = Color(0.15, 0.12, 0.1, 0.9)
	door.name = "HiddenDoor"
	parent.add_child(door)
	_visual_nodes.append(door)
	
	# 神秘符文
	var rune = Label.new()
	rune.text = "?"
	rune.position = Vector2(-10, -60)
	rune.add_theme_color_override("font_color", Color(0.5, 0.3, 0.8, 0.7))
	rune.add_theme_font_size_override("font_size", 24)
	rune.name = "DoorRune"
	parent.add_child(rune)


## 通用外观
func _create_generic_appearance(parent: Node2D) -> void:
	var rect = ColorRect.new()
	rect.size = Vector2(30, 30)
	rect.position = Vector2(-15, -30)
	rect.color = Color(0.5, 0.5, 0.5)
	rect.name = "GenericInteract"
	parent.add_child(rect)


## 查找关联的目标节点
func _find_linked_target() -> void:
	var tree = get_tree()
	for node in tree.get_nodes_in_group("interactable"):
		if node.get("interact_id") == target_id:
			_linked_target = node
			break


## 玩家进入交互范围
func _on_body_entered(body: Node2D) -> void:
	if _is_triggered and one_shot:
		return
	
	if not body.is_in_group("player"):
		return
	
	_player_ref = body
	
	# 检查技能要求
	if required_skill != "":
		if not _check_skill_requirement(body):
			return
	
	_trigger(body)


## 检查技能要求
func _check_skill_requirement(player: Node2D) -> bool:
	match required_skill:
		"double_jump":
			return player.get("can_double_jump") if player.get("can_double_jump") != null else false
		"triple_jump":
			return player.get("can_triple_jump") if player.get("can_triple_jump") != null else false
		"dash":
			return player.get("can_dash") if player.get("can_dash") != null else false
		"wall_jump":
			return player.get("can_wall_jump") if player.get("can_wall_jump") != null else false
		_:
			return true


## 触发交互
func _trigger(player: Node2D) -> void:
	match interact_type:
		"switch":
			_trigger_switch(player)
		"mushroom_spring":
			_trigger_mushroom(player)
		"pipe_teleport":
			_trigger_pipe(player)
		"glowing_moss":
			_trigger_moss(player)
		"checkpoint_altar":
			_trigger_checkpoint(player)
		"hidden_door":
			_trigger_hidden_door(player)
	
	if one_shot:
		_is_triggered = true


## 触发开关
func _trigger_switch(_player: Node2D) -> void:
	print("SceneInteractable: 开关 '%s' 被触发" % interact_id)
	AudioManager.play_sfx("click")
	
	# 视觉效果：按钮按下
	var tween = create_tween()
	tween.tween_property(_visual_nodes[1] if _visual_nodes.size() > 1 else self, "position:y", 0, 0.1)
	
	# 触发关联目标
	if _linked_target and _linked_target.has_method("activate"):
		_linked_target.activate()
	
	# 也可通过信号通知
	Global.story_flag_set.emit("switch_" + interact_id, true)


## 触发弹簧蘑菇
func _trigger_mushroom(player: Node2D) -> void:
	print("SceneInteractable: 弹簧蘑菇 '%s' 弹飞玩家" % interact_id)
	
	var bounce_power: float = param_float if param_float > 0 else 300.0
	
	if player is CharacterBody2D:
		player.velocity.y = -bounce_power
	
	# 蘑菇压缩回弹动画
	var tween = create_tween()
	tween.tween_property(self, "scale:y", 0.6, 0.05)
	tween.tween_property(self, "scale:y", 1.2, 0.1)
	tween.tween_property(self, "scale:y", 1.0, 0.1)
	
	AudioManager.play_sfx("jump")


## 触发管道传送
func _trigger_pipe(player: Node2D) -> void:
	print("SceneInteractable: 管道 '%s' 传送玩家到 '%s'" % [interact_id, target_id])
	
	# 寻找目标管道出口
	var exit_node: Node = null
	if target_id != "":
		for node in get_tree().get_nodes_in_group("interactable"):
			if node.get("interact_id") == target_id and node.get("interact_type") == "pipe_teleport":
				exit_node = node
				break
	
	if exit_node and exit_node is Node2D:
		# 传送玩家到出口位置
		if player is CharacterBody2D:
			player.global_position = exit_node.global_position + Vector2(0, -40)
			player.velocity = Vector2.ZERO
	else:
		print("SceneInteractable: 管道出口 '%s' 未找到" % target_id)


## 触发发光苔藓
func _trigger_moss(player: Node2D) -> void:
	var restore_amount: float = param_float if param_float > 0 else 10.0
	
	# 恢复MP
	if player.has_method("heal"):
		player.heal(0)  # 不会用heal恢复MP
	if player.get("current_mp") != null:
		var max_mp: int = player.get("max_mp")
		var current_mp: int = player.get("current_mp")
		player.set("current_mp", mini(current_mp + int(restore_amount), max_mp))
	
	print("SceneInteractable: 发光苔藓 '%s' 恢复MP %.0f" % [interact_id, restore_amount])
	
	# 苔藓消失特效
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 1.0)
	tween.finished.connect(queue_free)
	
	AudioManager.play_sfx("pickup")


## 触发存档祭坛
func _trigger_checkpoint(player: Node2D) -> void:
	print("SceneInteractable: 存档祭坛 '%s' 被激活" % interact_id)
	
	# 保存进度
	if player.has_method("set_checkpoint"):
		player.set_checkpoint(interact_id)
	
	# 发射信号
	Global.checkpoint_reached.emit(interact_id)
	
	# 视觉反馈：祭坛发光
	if _visual_nodes.size() > 0:
		var orb: ColorRect = _visual_nodes[0]
		var glow_tween = create_tween()
		glow_tween.set_loops(3)
		glow_tween.tween_property(orb, "color:a", 1.0, 0.3)
		glow_tween.tween_property(orb, "color:a", 0.3, 0.3)
	
	# 自动存档
	SaveManager.trigger_auto_save("存档祭坛: " + interact_id)
	
	AudioManager.play_sfx("level_up")


## 触发隐藏门
func _trigger_hidden_door(_player: Node2D) -> void:
	print("SceneInteractable: 隐藏门 '%s' 打开" % interact_id)
	
	# 检查开启条件（如收集全部班级合照）
	var can_open: bool = true
	
	if required_skill == "class_photos":
		can_open = Global.story_flags.get("found_all_class_photos", false)
	
	if not can_open:
		print("SceneInteractable: 隐藏门 '%s' 条件不满足" % interact_id)
		return
	
	# 开门动画
	var tween = create_tween()
	tween.tween_property(self, "modulate:a", 0.0, 0.8)
	tween.parallel().tween_property(self, "scale:y", 0.0, 0.8)
	tween.finished.connect(func():
		collision_mask = 0  # 消除碰撞
		queue_free()
	)
	
	AudioManager.play_sfx("enemy_die")


## 激活（供开关等调用）
func activate() -> void:
	if _is_triggered:
		return
	_is_triggered = true
	print("SceneInteractable: '%s' 被远程激活" % interact_id)


## 处理推箱子推动（由玩家在physics中调用）
func push_box(push_dir: Vector2, push_speed: float) -> void:
	if interact_type != "push_box":
		return
	
	# 简单推动逻辑
	var move_amount = push_dir * push_speed * get_physics_process_delta_time()
	global_position += move_amount
	
	# 检查是否到达目标区域（PressurePlate）
	for node in get_tree().get_nodes_in_group("interactable"):
		if node.get("interact_id") == target_id and node.get("interact_type") == "switch":
			var dist = global_position.distance_to(node.global_position)
			if dist < 40:
				# 触发目标开关
				if node.has_method("activate"):
					node.activate()
				_is_triggered = true
				print("SceneInteractable: 推箱子到达压力板 '%s'" % target_id)


## 是否已触发（供外部查询）
func is_triggered() -> bool:
	return _is_triggered