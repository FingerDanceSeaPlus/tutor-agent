import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class TraceService:
    """Trace服务"""
    def __init__(self, storage_type: str = "jsonl"):
        """初始化Trace服务"""
        self.storage_type = storage_type
        self.base_dir = "traces"
        os.makedirs(self.base_dir, exist_ok=True)

        if storage_type == "sqlite":
            self._init_sqlite()

    def _init_sqlite(self):
        """初始化SQLite数据库"""
        self.db_path = os.path.join(self.base_dir, "traces.db")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # 创建会话表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP,
                    hint_level TEXT,
                    current_stage TEXT
                )
            ''')
            # 创建事件表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trace_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    ts TIMESTAMP,
                    stage TEXT,
                    kind TEXT,
                    payload_json TEXT,
                    FOREIGN KEY (session_id) REFERENCES sessions (id)
                )
            ''')
            conn.commit()

    def store_trace(self, session_id: str, trace: Dict[str, Any]):
        """存储trace"""
        if self.storage_type == "jsonl":
            self._store_jsonl(session_id, trace)
        elif self.storage_type == "sqlite":
            self._store_sqlite(session_id, trace)
        else:
            logger.error(f"不支持的存储类型: {self.storage_type}")

    def _store_jsonl(self, session_id: str, trace: Dict[str, Any]):
        """以JSONL格式存储trace"""
        file_path = os.path.join(self.base_dir, f"{session_id}.jsonl")
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                # 存储每个事件
                for event in trace.get("events", []):
                    json.dump(event, f, ensure_ascii=False, default=str)
                    f.write("\n")
            logger.info(f"Trace stored to {file_path}")
        except Exception as e:
            logger.error(f"存储trace失败: {e}")

    def _store_sqlite(self, session_id: str, trace: Dict[str, Any]):
        """以SQLite格式存储trace"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 插入或更新会话信息
                cursor.execute(
                    "INSERT OR REPLACE INTO sessions (id, created_at, hint_level, current_stage) VALUES (?, ?, ?, ?)",
                    (session_id, datetime.now(), trace.get("hint_level"), trace.get("current_stage"))
                )
                # 插入事件
                for event in trace.get("events", []):
                    cursor.execute(
                        "INSERT INTO trace_events (session_id, ts, stage, kind, payload_json) VALUES (?, ?, ?, ?, ?)",
                        (
                            session_id,
                            event.get("ts"),
                            event.get("stage"),
                            event.get("kind"),
                            json.dumps(event.get("payload"), ensure_ascii=False)
                        )
                    )
                conn.commit()
            logger.info(f"Trace stored to SQLite for session {session_id}")
        except Exception as e:
            logger.error(f"存储trace失败: {e}")

    def get_trace(self, session_id: str) -> Dict[str, Any]:
        """获取trace"""
        if self.storage_type == "jsonl":
            return self._get_jsonl(session_id)
        elif self.storage_type == "sqlite":
            return self._get_sqlite(session_id)
        else:
            logger.error(f"不支持的存储类型: {self.storage_type}")
            return {}

    def _get_jsonl(self, session_id: str) -> Dict[str, Any]:
        """从JSONL文件获取trace"""
        file_path = os.path.join(self.base_dir, f"{session_id}.jsonl")
        if not os.path.exists(file_path):
            return {"events": []}

        events = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        events.append(json.loads(line))
            return {"events": events}
        except Exception as e:
            logger.error(f"读取trace失败: {e}")
            return {"events": []}

    def _get_sqlite(self, session_id: str) -> Dict[str, Any]:
        """从SQLite获取trace"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                # 获取会话信息
                cursor.execute("SELECT hint_level, current_stage FROM sessions WHERE id = ?", (session_id,))
                session_info = cursor.fetchone()

                # 获取事件
                cursor.execute(
                    "SELECT ts, stage, kind, payload_json FROM trace_events WHERE session_id = ? ORDER BY ts",
                    (session_id,)
                )
                events = []
                for row in cursor.fetchall():
                    ts, stage, kind, payload_json = row
                    events.append({
                        "ts": ts,
                        "stage": stage,
                        "kind": kind,
                        "payload": json.loads(payload_json)
                    })

                result = {"events": events}
                if session_info:
                    result["hint_level"] = session_info[0]
                    result["current_stage"] = session_info[1]
                return result
        except Exception as e:
            logger.error(f"读取trace失败: {e}")
            return {"events": []}

    def list_sessions(self) -> List[Dict[str, Any]]:
        """列出所有会话"""
        if self.storage_type == "jsonl":
            return self._list_jsonl_sessions()
        elif self.storage_type == "sqlite":
            return self._list_sqlite_sessions()
        else:
            logger.error(f"不支持的存储类型: {self.storage_type}")
            return []

    def _list_jsonl_sessions(self) -> List[Dict[str, Any]]:
        """列出JSONL格式的会话"""
        sessions = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith(".jsonl"):
                session_id = filename[:-6]  # 移除.jsonl后缀
                file_path = os.path.join(self.base_dir, filename)
                created_at = os.path.getctime(file_path)
                sessions.append({
                    "session_id": session_id,
                    "created_at": datetime.fromtimestamp(created_at).isoformat()
                })
        return sessions

    def _list_sqlite_sessions(self) -> List[Dict[str, Any]]:
        """列出SQLite中的会话"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, created_at, hint_level, current_stage FROM sessions")
                sessions = []
                for row in cursor.fetchall():
                    session_id, created_at, hint_level, current_stage = row
                    sessions.append({
                        "session_id": session_id,
                        "created_at": created_at,
                        "hint_level": hint_level,
                        "current_stage": current_stage
                    })
                return sessions
        except Exception as e:
            logger.error(f"列出会话失败: {e}")
            return []
