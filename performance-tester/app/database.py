"""
Database module for storing test results - OPTIMIZED for SSD
Features:
- WAL mode for better concurrent access and SSD performance
- Bulk inserts for faster writes
- Optimized indexes for queries
- Connection pooling
- Memory-mapped I/O for large datasets
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
import threading


class Database:
    """Database manager for performance test results - SSD optimized"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._lock = threading.Lock()  # Thread safety for concurrent access
        self._bulk_buffer = []  # Buffer for bulk inserts
        self._bulk_buffer_size = 1000  # Flush after 1000 records
        self.init_database()
        self._optimize_for_ssd()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections - optimized"""
        conn = sqlite3.connect(
            self.db_path,
            timeout=30.0,  # 30 second timeout for locks
            check_same_thread=False  # Allow multi-threading
        )
        conn.row_factory = sqlite3.Row

        # Enable SSD optimizations
        conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging for SSDs
        conn.execute("PRAGMA synchronous=NORMAL")  # Balance between safety and speed
        conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
        conn.execute("PRAGMA temp_store=MEMORY")  # Use RAM for temp tables
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O

        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _optimize_for_ssd(self):
        """Apply SSD-specific optimizations"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Set optimal pragmas for SSD
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.execute("PRAGMA mmap_size=268435456")

            # Auto-vacuum for SSD wear leveling
            cursor.execute("PRAGMA auto_vacuum=INCREMENTAL")

            # Larger page size for SSDs (4KB aligned)
            try:
                cursor.execute("PRAGMA page_size=4096")
            except sqlite3.OperationalError:
                pass  # Can't change page size after DB is created

            print("✓ Database optimized for SSD (WAL mode, 64MB cache, 256MB mmap)")

    def init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Test runs table - ENHANCED with more metrics
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
                    p75_response_time REAL,
                    p90_response_time REAL,
                    p95_response_time REAL,
                    p99_response_time REAL,
                    p999_response_time REAL,
                    requests_per_second REAL,
                    errors_per_second REAL,
                    throughput_mbps REAL,
                    total_bytes_sent INTEGER,
                    total_bytes_received INTEGER,
                    std_dev_response_time REAL,
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

            # System metrics table - ENHANCED
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_run_id INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    cpu_percent REAL,
                    cpu_per_core TEXT,
                    load_1min REAL,
                    load_5min REAL,
                    load_15min REAL,
                    memory_percent REAL,
                    memory_used_mb REAL,
                    memory_cached_mb REAL,
                    disk_usage_percent REAL,
                    disk_io_read_mb REAL,
                    disk_io_write_mb REAL,
                    disk_read_iops REAL,
                    disk_write_iops REAL,
                    disk_read_rate_mbs REAL,
                    disk_write_rate_mbs REAL,
                    network_sent_mb REAL,
                    network_recv_mb REAL,
                    network_upload_mbps REAL,
                    network_download_mbps REAL,
                    network_total_mbps REAL,
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
        """Add system metrics record - ENHANCED with new fields"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Convert cpu_per_core list to JSON string
            cpu_per_core_json = json.dumps(metrics.get('cpu_per_core', [])) if metrics.get('cpu_per_core') else None

            cursor.execute("""
                INSERT INTO system_metrics
                (test_run_id, timestamp, cpu_percent, cpu_per_core, load_1min, load_5min, load_15min,
                 memory_percent, memory_used_mb, memory_cached_mb, disk_usage_percent,
                 disk_io_read_mb, disk_io_write_mb, disk_read_iops, disk_write_iops,
                 disk_read_rate_mbs, disk_write_rate_mbs,
                 network_sent_mb, network_recv_mb, network_upload_mbps, network_download_mbps,
                 network_total_mbps, active_connections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                test_run_id,
                metrics.get('timestamp', datetime.now()),
                metrics.get('cpu_percent'),
                cpu_per_core_json,
                metrics.get('load_1min'),
                metrics.get('load_5min'),
                metrics.get('load_15min'),
                metrics.get('memory_percent'),
                metrics.get('memory_used_mb'),
                metrics.get('memory_cached_mb'),
                metrics.get('disk_usage_percent'),
                metrics.get('disk_io_read_mb'),
                metrics.get('disk_io_write_mb'),
                metrics.get('disk_read_iops'),
                metrics.get('disk_write_iops'),
                metrics.get('disk_read_rate_mbs'),
                metrics.get('disk_write_rate_mbs'),
                metrics.get('network_sent_mb'),
                metrics.get('network_recv_mb'),
                metrics.get('network_upload_mbps'),
                metrics.get('network_download_mbps'),
                metrics.get('network_total_mbps'),
                metrics.get('active_connections')
            ))

    def bulk_add_requests(self, test_run_id: int, requests_data: List[Dict[str, Any]]):
        """Bulk insert requests - MUCH faster for large datasets"""
        if not requests_data:
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Prepare bulk data
            bulk_data = [
                (
                    test_run_id,
                    req.get('timestamp', datetime.now()),
                    req['endpoint'],
                    req.get('method', 'POST'),
                    req.get('status_code'),
                    req['response_time'],
                    req['success'],
                    req.get('error_message'),
                    req.get('request_size'),
                    req.get('response_size')
                )
                for req in requests_data
            ]

            # Bulk insert (much faster than individual inserts)
            cursor.executemany("""
                INSERT INTO requests
                (test_run_id, timestamp, endpoint, method, status_code,
                 response_time, success, error_message, request_size, response_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, bulk_data)

            print(f"✓ Bulk inserted {len(requests_data)} requests")

    def bulk_add_system_metrics(self, test_run_id: int, metrics_data: List[Dict[str, Any]]):
        """Bulk insert system metrics - MUCH faster for large datasets"""
        if not metrics_data:
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Prepare bulk data
            bulk_data = []
            for m in metrics_data:
                cpu_per_core_json = json.dumps(m.get('cpu_per_core', [])) if m.get('cpu_per_core') else None
                bulk_data.append((
                    test_run_id,
                    m.get('timestamp', datetime.now()),
                    m.get('cpu_percent'),
                    cpu_per_core_json,
                    m.get('load_1min'),
                    m.get('load_5min'),
                    m.get('load_15min'),
                    m.get('memory_percent'),
                    m.get('memory_used_mb'),
                    m.get('memory_cached_mb'),
                    m.get('disk_usage_percent'),
                    m.get('disk_io_read_mb'),
                    m.get('disk_io_write_mb'),
                    m.get('disk_read_iops'),
                    m.get('disk_write_iops'),
                    m.get('disk_read_rate_mbs'),
                    m.get('disk_write_rate_mbs'),
                    m.get('network_sent_mb'),
                    m.get('network_recv_mb'),
                    m.get('network_upload_mbps'),
                    m.get('network_download_mbps'),
                    m.get('network_total_mbps'),
                    m.get('active_connections')
                ))

            # Bulk insert
            cursor.executemany("""
                INSERT INTO system_metrics
                (test_run_id, timestamp, cpu_percent, cpu_per_core, load_1min, load_5min, load_15min,
                 memory_percent, memory_used_mb, memory_cached_mb, disk_usage_percent,
                 disk_io_read_mb, disk_io_write_mb, disk_read_iops, disk_write_iops,
                 disk_read_rate_mbs, disk_write_rate_mbs,
                 network_sent_mb, network_recv_mb, network_upload_mbps, network_download_mbps,
                 network_total_mbps, active_connections)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, bulk_data)

            print(f"✓ Bulk inserted {len(metrics_data)} metrics")

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
