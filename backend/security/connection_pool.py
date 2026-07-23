"""数据库连接池模块 —— 用 DBUtils.PooledDB 替代每次新建连接"""
import pymysql
from dbutils.pooled_db import PooledDB
from config import settings
from typing import Optional


class ConnectionPool:
    """MySQL 连接池管理器"""

    _pools: dict = {}  # key: database_name or "__no_db__"

    @classmethod
    def get_pool(cls, database: Optional[str] = None) -> PooledDB:
        """获取或创建连接池"""
        pool_key = database or "__no_db__"
        if pool_key not in cls._pools:
            cls._pools[pool_key] = PooledDB(
                creator=pymysql,
                maxconnections=8,
                mincached=2,
                maxcached=5,
                blocking=True,
                maxusage=1000,
                setsession=["SET NAMES utf8mb4"],
                ping=1,  # 自动 ping 检查连接是否存活
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=database,
                read_timeout=settings.query_timeout,
                connect_timeout=5,
                cursorclass=pymysql.cursors.DictCursor,
                charset="utf8mb4",
            )
        return cls._pools[pool_key]

    @classmethod
    def get_connection(cls, database: Optional[str] = None) -> pymysql.Connection:
        """从连接池获取连接"""
        return cls.get_pool(database).connection()


# 全局连接池实例
pool_manager = ConnectionPool()