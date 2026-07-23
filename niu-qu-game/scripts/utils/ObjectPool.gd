# ObjectPool.gd - 对象池管理器
# 用于频繁创建/销毁的对象（子弹、粒子、伤害数字等），减少GC压力
# 使用 acquire() / release() 接口管理对象复用
extends Node

# ========== 对象池数据结构 ==========
# _pools: Dictionary<String, Dictionary> = { pool_key: { "scene": PackedScene, "available": Array, "active": Array } }
var _pools: Dictionary = {}

# ========== 全局对象池单例引用 ==========
static var _instance: Node = null

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_instance = self

## 获取全局对象池实例
static func get_instance() -> Node:
	return _instance


## 注册一个对象类型到池中
## @param pool_key: 池的唯一标识符
## @param packed_scene: 对象的PackedScene资源
## @param preload_count: 预加载数量（可选，默认0）
func register_pool(pool_key: String, packed_scene: PackedScene, preload_count: int = 0) -> void:
	if _pools.has(pool_key):
		push_warning("ObjectPool: 池 '%s' 已注册" % pool_key)
		return
	
	_pools[pool_key] = {
		"scene": packed_scene,
		"available": [],
		"active": [],
	}
	
	# 预加载对象
	for i in range(preload_count):
		var obj: Node = packed_scene.instantiate()
		obj.set_meta("_pool_key", pool_key)
		obj.visible = false
		obj.process_mode = Node.PROCESS_MODE_DISABLED
		_pools[pool_key]["available"].append(obj)
	
	print("ObjectPool: 注册池 '%s'，预加载 %d 个对象" % [pool_key, preload_count])


## 从池中获取一个对象
## @param pool_key: 池的标识符
## @return: 节点实例，如果池未注册或没有可用对象则返回null
func acquire(pool_key: String) -> Node:
	if not _pools.has(pool_key):
		push_error("ObjectPool: 未注册的池 '%s'" % pool_key)
		return null
	
	var pool: Dictionary = _pools[pool_key]
	var obj: Node = null
	
	if pool["available"].is_empty():
		# 池已空，创建新实例
		obj = pool["scene"].instantiate()
		obj.set_meta("_pool_key", pool_key)
	else:
		# 从可用列表中取出
		obj = pool["available"].pop_back()
	
	# 激活对象
	obj.visible = true
	obj.process_mode = Node.PROCESS_MODE_INHERIT
	pool["active"].append(obj)
	
	return obj


## 将对象归还到池中
## @param obj: 要归还的节点
func release(obj: Node) -> void:
	if obj == null:
		return
	
	var pool_key: String = obj.get_meta("_pool_key", "")
	if pool_key.is_empty() or not _pools.has(pool_key):
		# 未在池中注册的对象直接删除
		obj.queue_free()
		return
	
	# 从活跃列表移除
	var pool: Dictionary = _pools[pool_key]
	var idx: int = pool["active"].find(obj)
	if idx != -1:
		pool["active"].remove_at(idx)
	
	# 重置对象状态
	obj.visible = false
	obj.process_mode = Node.PROCESS_MODE_DISABLED
	
	# 如果对象有父节点，移除
	if obj.get_parent():
		obj.get_parent().remove_child(obj)
	
	# 加入可用列表
	pool["available"].append(obj)


## 从池中获取对象并添加到父节点
## @param pool_key: 池的标识符
## @param parent: 父节点
## @param position: 世界坐标位置
## @return: 节点实例
func acquire_and_add(pool_key: String, parent: Node, position: Vector2 = Vector2.ZERO) -> Node:
	var obj: Node = acquire(pool_key)
	if obj and parent:
		parent.add_child(obj)
		if obj is Node2D:
			obj.global_position = position
	return obj


## 获取池的统计信息
## @return: Dictionary { "available": int, "active": int }
func get_pool_stats(pool_key: String) -> Dictionary:
	if not _pools.has(pool_key):
		return { "available": 0, "active": 0 }
	
	var pool: Dictionary = _pools[pool_key]
	return {
		"available": pool["available"].size(),
		"active": pool["active"].size(),
	}


## 清空指定池（删除所有对象）
## @param pool_key: 池的标识符
func clear_pool(pool_key: String) -> void:
	if not _pools.has(pool_key):
		return
	
	var pool: Dictionary = _pools[pool_key]
	for obj in pool["available"]:
		obj.queue_free()
	for obj in pool["active"]:
		obj.queue_free()
	
	pool["available"].clear()
	pool["active"].clear()


## 清空所有对象池
func clear_all_pools() -> void:
	for pool_key in _pools.keys():
		clear_pool(pool_key)
	_pools.clear()
	print("ObjectPool: 所有池已清空")