"""
Database module for storing test results
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager


class Database:
    """Database manager for performance test results"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Test runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_name TEXT NOT NULL,
                    test_type TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds REAL,
                    total_requests INTEGER DEFAULT 0,
                    successful_requests INTEGER DEFAULT 0,
                    failed_requests INTEGER DEFAULT 0,
                    avg_response_time REAL,
                    min_response_time REAL,
                    max_response_time REAL,
                    p50_response_time REAL,
                    p95_response_time REAL,
                    p99_response_time REAL,
                    requests_per_second REAL,
                    errors_per_second REAL,
                    status TEXT DEFAULT 'running',
                    config TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Individual requests table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_run_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    endpoint TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER,
                    response_time REAL NOT NULL,
                    success BOOLEAN NOT NULL,
                    error_message TEXT,
                    request_size INTEGER,
                    response_size INTEGER,
                    FOREIGN KEY (test_run_id) REFERENCES test_runs (id)
                )
            """)

            # System metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_run_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    disk_usage_percent REAL,
                    disk_io_read_mb REAL,
                    disk_io_write_mb REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    active_connections INTEGER,
                    FOREIGN KEY (test_run_id) REFERENCES test_runs (id)
                )
            """)

            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_test_runs_start_time
                ON test_runs(start_time)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_requests_test_run
                ON requests(test_run_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_metrics_test_run
                ON system_metrics(test_run_id)
            """)

    def create_test_run(self, test_name: str, test_type: str, config: Dict[str, Any]) -> int:
        """Create a new test run record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO test_runs
                (test_name, test_type, start_time, config, status)
                VALUES (?, ?, ?, ?, 'running')
            """, (test_name, test_type, datetime.now(), json.dumps(config)))
            return cursor.lastrowid

    def update_test_run(self, test_run_id: int, data: Dict[str, Any]):
        """Update test run with results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            fields = ", ".join([f"{key} = ?" for key in data.keys()])
            values = list(data.values()) + [test_run_id]
            cursor.execute(f"""
                UPDATE test_runs SET {fields}
                WHERE id = ?
            """, values)

    def complete_test_run(self, test_run_id: int):
        """Mark test run as completed"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE test_runs
                SET status = 'completed', end_time = ?
                WHERE id = ?
            """, (datetime.now(), test_run_id))

    def add_request(self, test_run_id: int, request_data: Dict[str, Any]):
        """Add a request record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO requests
                (test_run_id, timestamp, endpoint, method, status_code,
                 response_time, success, error_message, request_size, response_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_run_id,
                request_data.get('timestamp', datetime.now()),
                request_data['endpoint'],
                request_data.get('method', 'POST'),
                request_data.get('status_code'),
                request_data['response_time'],
                request_data['success'],
                request_data.get('error_message'),
                request_data.get('request_size'),
                request_data.get('response_size')
            ))

    def add_system_metric(self, test_run_id: int, metrics: Dict[str, Any]):
        """Add system metrics record"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_metrics
                (test_run_id, timestamp, cpu_percent, memory_percent, memory_used_mb,
                 disk_usage_percent, disk_io_read_mb, disk_io_write_mb,
                 network_sent_mb, network_recv_mb, active_connections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_run_id,
                metrics.get('timestamp', datetime.now()),
                metrics.get('cpu_percent'),
                metrics.get('memory_percent'),
                metrics.get('memory_used_mb'),
                metrics.get('disk_usage_percent'),
                metrics.get('disk_io_read_mb'),
                metrics.get('disk_io_write_mb'),
                metrics.get('network_sent_mb'),
                metrics.get('network_recv_mb'),
                metrics.get('active_connections')
            ))

    def get_test_run(self, test_run_id: int) -> Optional[Dict[str, Any]]:
        """Get test run by ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM test_runs WHERE id = ?", (test_run_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    def get_all_test_runs(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all test runs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM test_runs
                ORDER BY start_time DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def get_test_requests(self, test_run_id: int) -> List[Dict[str, Any]]:
        """Get all requests for a test run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM requests
                WHERE test_run_id = ?
                ORDER BY timestamp
            """, (test_run_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_system_metrics(self, test_run_id: int) -> List[Dict[str, Any]]:
        """Get system metrics for a test run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM system_metrics
                WHERE test_run_id = ?
                ORDER BY timestamp
            """, (test_run_id,))
            return [dict(row) for row in cursor.fetchall()]

    def get_statistics(self, test_run_id: int) -> Dict[str, Any]:
        """Calculate statistics for a test run"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Request statistics
            cursor.execute("""
                SELECT
                    COUNT(*) as total_requests,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed,
                    AVG(response_time) as avg_time,
                    MIN(response_time) as min_time,
                    MAX(response_time) as max_time
                FROM requests
                WHERE test_run_id = ?
            """, (test_run_id,))
            req_stats = dict(cursor.fetchone())

            # System metrics statistics
            cursor.execute("""
                SELECT
                    AVG(cpu_percent) as avg_cpu,
                    MAX(cpu_percent) as max_cpu,
                    AVG(memory_percent) as avg_memory,
                    MAX(memory_percent) as max_memory,
                    MAX(memory_used_mb) as max_memory_mb
                FROM system_metrics
                WHERE test_run_id = ?
            """, (test_run_id,))
            sys_stats = dict(cursor.fetchone())

            return {**req_stats, **sys_stats}

    def delete_test_run(self, test_run_id: int):
        """Delete a test run and all related data"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM requests WHERE test_run_id = ?", (test_run_id,))
            cursor.execute("DELETE FROM system_metrics WHERE test_run_id = ?", (test_run_id,))
            cursor.execute("DELETE FROM test_runs WHERE id = ?", (test_run_id,))
