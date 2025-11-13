"""
System monitoring module - ENHANCED for 8 vCPU / 24GB RAM / 400GB SSD
Monitors CPU (per-core), RAM, Disk I/O, Network throughput during performance tests

Features:
- Per-core CPU monitoring (optimized for 8 vCPU)
- Detailed I/O metrics (IOPS, throughput rates)
- Network throughput in Mbps (for 600 Mbit/s connection)
- SSD-optimized metrics
- Real-time rate calculations
"""
import psutil
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from collections import deque
import statistics


class SystemMonitor:
    """Monitor system resources during tests"""

    def __init__(self, interval: float = 1.0, history_size: int = 300):
        """
        Initialize system monitor

        Args:
            interval: Monitoring interval in seconds
            history_size: Number of samples to keep in memory
        """
        self.interval = interval
        self.history_size = history_size
        self.monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

        # Circular buffers for real-time data
        self.cpu_history = deque(maxlen=history_size)
        self.cpu_per_core_history = deque(maxlen=history_size)  # NEW: per-core CPU
        self.memory_history = deque(maxlen=history_size)
        self.disk_io_history = deque(maxlen=history_size)
        self.disk_iops_history = deque(maxlen=history_size)  # NEW: IOPS
        self.network_io_history = deque(maxlen=history_size)
        self.network_throughput_history = deque(maxlen=history_size)  # NEW: Mbps
        self.timestamps = deque(maxlen=history_size)

        # Baseline measurements for rate calculations
        self._disk_io_baseline = psutil.disk_io_counters()
        self._network_io_baseline = psutil.net_io_counters()
        self._baseline_time = time.time()

        # Previous values for rate calculations
        self._prev_disk_io = None
        self._prev_network_io = None
        self._prev_time = time.time()

        # Callback for storing metrics
        self.metric_callback: Optional[Callable] = None

    def start(self, callback: Optional[Callable] = None):
        """
        Start monitoring

        Args:
            callback: Optional function to call with each metric sample
        """
        if self.monitoring:
            return

        self.metric_callback = callback
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                metrics = self.get_current_metrics()
                self._update_history(metrics)

                if self.metric_callback:
                    self.metric_callback(metrics)

                time.sleep(self.interval)
            except Exception as e:
                print(f"Monitoring error: {e}")

    def _update_history(self, metrics: Dict[str, Any]):
        """Update history buffers with new metrics - Enhanced"""
        self.timestamps.append(metrics['timestamp'])
        self.cpu_history.append(metrics['cpu_percent'])
        self.cpu_per_core_history.append(metrics['cpu_per_core'])
        self.memory_history.append(metrics['memory_percent'])
        self.disk_io_history.append({
            'read': metrics['disk_io_read_mb'],
            'write': metrics['disk_io_write_mb']
        })
        self.disk_iops_history.append({
            'read_iops': metrics.get('disk_read_iops', 0),
            'write_iops': metrics.get('disk_write_iops', 0)
        })
        self.network_io_history.append({
            'sent': metrics['network_sent_mb'],
            'recv': metrics['network_recv_mb']
        })
        self.network_throughput_history.append({
            'upload_mbps': metrics.get('network_upload_mbps', 0),
            'download_mbps': metrics.get('network_download_mbps', 0)
        })

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics - ENHANCED with per-core CPU, IOPS, and Mbps"""
        current_time = time.time()

        # CPU metrics - ENHANCED with per-core monitoring
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_per_core = psutil.cpu_percent(interval=0.1, percpu=True)  # NEW: Per-core CPU
        cpu_count = psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)
        cpu_freq = psutil.cpu_freq()

        # Memory metrics
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        # Disk metrics
        disk = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()

        # Network metrics
        network_io = psutil.net_io_counters()

        # Calculate cumulative IO since baseline
        time_delta = current_time - self._baseline_time

        if time_delta > 0:
            disk_read_mb = (disk_io.read_bytes - self._disk_io_baseline.read_bytes) / (1024 * 1024)
            disk_write_mb = (disk_io.write_bytes - self._disk_io_baseline.write_bytes) / (1024 * 1024)
            network_sent_mb = (network_io.bytes_sent - self._network_io_baseline.bytes_sent) / (1024 * 1024)
            network_recv_mb = (network_io.bytes_recv - self._network_io_baseline.bytes_recv) / (1024 * 1024)
        else:
            disk_read_mb = disk_write_mb = network_sent_mb = network_recv_mb = 0

        # Calculate RATES (IOPS and Mbps) - NEW
        interval = current_time - self._prev_time

        if interval > 0 and self._prev_disk_io and self._prev_network_io:
            # Disk IOPS (operations per second)
            disk_read_iops = (disk_io.read_count - self._prev_disk_io.read_count) / interval
            disk_write_iops = (disk_io.write_count - self._prev_disk_io.write_count) / interval

            # Disk throughput (MB/s)
            disk_read_rate = (disk_io.read_bytes - self._prev_disk_io.read_bytes) / (1024 * 1024 * interval)
            disk_write_rate = (disk_io.write_bytes - self._prev_disk_io.write_bytes) / (1024 * 1024 * interval)

            # Network throughput in Mbps (for 600 Mbit/s connection)
            bytes_sent_diff = network_io.bytes_sent - self._prev_network_io.bytes_sent
            bytes_recv_diff = network_io.bytes_recv - self._prev_network_io.bytes_recv

            network_upload_mbps = (bytes_sent_diff * 8) / (1_000_000 * interval)  # Convert to Mbps
            network_download_mbps = (bytes_recv_diff * 8) / (1_000_000 * interval)
        else:
            disk_read_iops = disk_write_iops = 0
            disk_read_rate = disk_write_rate = 0
            network_upload_mbps = network_download_mbps = 0

        # Update previous values
        self._prev_disk_io = disk_io
        self._prev_network_io = network_io
        self._prev_time = current_time

        # Get active network connections
        try:
            connections = len(psutil.net_connections(kind='inet'))
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            connections = 0

        # CPU load average (Linux/Unix)
        try:
            load_avg = psutil.getloadavg()
            load_1min, load_5min, load_15min = load_avg
        except (AttributeError, OSError):
            load_1min = load_5min = load_15min = 0

        return {
            'timestamp': datetime.now().isoformat(),  # Convert to ISO string for JSON serialization
            # CPU metrics - ENHANCED
            'cpu_percent': cpu_percent,
            'cpu_per_core': cpu_per_core,  # NEW: List of per-core usage
            'cpu_count': cpu_count,
            'cpu_count_logical': cpu_count_logical,
            'cpu_freq_mhz': cpu_freq.current if cpu_freq else 0,
            'cpu_freq_max_mhz': cpu_freq.max if cpu_freq else 0,
            'cpu_freq_min_mhz': cpu_freq.min if cpu_freq else 0,
            'load_1min': load_1min,  # NEW
            'load_5min': load_5min,  # NEW
            'load_15min': load_15min,  # NEW

            # Memory metrics
            'memory_percent': memory.percent,
            'memory_used_mb': memory.used / (1024 * 1024),
            'memory_available_mb': memory.available / (1024 * 1024),
            'memory_total_mb': memory.total / (1024 * 1024),
            'memory_cached_mb': memory.cached / (1024 * 1024) if hasattr(memory, 'cached') else 0,
            'swap_percent': swap.percent,
            'swap_used_mb': swap.used / (1024 * 1024),

            # Disk metrics - ENHANCED
            'disk_usage_percent': disk.percent,
            'disk_used_gb': disk.used / (1024 * 1024 * 1024),
            'disk_free_gb': disk.free / (1024 * 1024 * 1024),
            'disk_total_gb': disk.total / (1024 * 1024 * 1024),
            'disk_io_read_mb': disk_read_mb,
            'disk_io_write_mb': disk_write_mb,
            'disk_read_iops': disk_read_iops,  # NEW
            'disk_write_iops': disk_write_iops,  # NEW
            'disk_read_rate_mbs': disk_read_rate,  # NEW: MB/s
            'disk_write_rate_mbs': disk_write_rate,  # NEW: MB/s

            # Network metrics - ENHANCED
            'network_sent_mb': network_sent_mb,
            'network_recv_mb': network_recv_mb,
            'network_upload_mbps': network_upload_mbps,  # NEW: Real-time Mbps
            'network_download_mbps': network_download_mbps,  # NEW: Real-time Mbps
            'network_total_mbps': network_upload_mbps + network_download_mbps,  # NEW
            'active_connections': connections
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Get static system information"""
        import platform
        import socket

        cpu_info = {}
        try:
            import cpuinfo
            cpu_info = cpuinfo.get_cpu_info()
        except:
            pass

        return {
            'hostname': socket.gethostname(),
            'platform': platform.platform(),
            'processor': platform.processor() or cpu_info.get('brand_raw', 'Unknown'),
            'cpu_cores': psutil.cpu_count(logical=False),
            'cpu_threads': psutil.cpu_count(logical=True),
            'total_memory_gb': psutil.virtual_memory().total / (1024 ** 3),
            'total_disk_gb': psutil.disk_usage('/').total / (1024 ** 3),
            'python_version': platform.python_version()
        }

    def get_realtime_data(self) -> Dict[str, Any]:
        """Get real-time data for live charts"""
        if not self.timestamps:
            return {
                'timestamps': [],
                'cpu': [],
                'memory': [],
                'disk_read': [],
                'disk_write': [],
                'network_sent': [],
                'network_recv': []
            }

        return {
            'timestamps': [ts.isoformat() for ts in self.timestamps],
            'cpu': list(self.cpu_history),
            'memory': list(self.memory_history),
            'disk_read': [d['read'] for d in self.disk_io_history],
            'disk_write': [d['write'] for d in self.disk_io_history],
            'network_sent': [n['sent'] for n in self.network_io_history],
            'network_recv': [n['recv'] for n in self.network_io_history]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Calculate statistics from history"""
        if not self.timestamps:
            return {}

        import statistics

        return {
            'cpu': {
                'avg': statistics.mean(self.cpu_history),
                'min': min(self.cpu_history),
                'max': max(self.cpu_history),
                'median': statistics.median(self.cpu_history)
            },
            'memory': {
                'avg': statistics.mean(self.memory_history),
                'min': min(self.memory_history),
                'max': max(self.memory_history),
                'median': statistics.median(self.memory_history)
            },
            'disk_io': {
                'total_read_mb': sum(d['read'] for d in self.disk_io_history),
                'total_write_mb': sum(d['write'] for d in self.disk_io_history)
            },
            'network_io': {
                'total_sent_mb': sum(n['sent'] for n in self.network_io_history),
                'total_recv_mb': sum(n['recv'] for n in self.network_io_history)
            }
        }

    def reset(self):
        """Reset monitoring history and baselines"""
        self.cpu_history.clear()
        self.cpu_per_core_history.clear()
        self.memory_history.clear()
        self.disk_io_history.clear()
        self.disk_iops_history.clear()
        self.network_io_history.clear()
        self.network_throughput_history.clear()
        self.timestamps.clear()

        self._disk_io_baseline = psutil.disk_io_counters()
        self._network_io_baseline = psutil.net_io_counters()
        self._baseline_time = time.time()

        self._prev_disk_io = None
        self._prev_network_io = None
        self._prev_time = time.time()

    def check_thresholds(self, cpu_threshold: float = 80.0,
                        memory_threshold: float = 85.0,
                        disk_threshold: float = 90.0) -> Dict[str, Any]:
        """
        Check if current metrics exceed thresholds

        Returns dict with warnings
        """
        metrics = self.get_current_metrics()
        warnings = []

        if metrics['cpu_percent'] > cpu_threshold:
            warnings.append(f"High CPU usage: {metrics['cpu_percent']:.1f}%")

        if metrics['memory_percent'] > memory_threshold:
            warnings.append(f"High memory usage: {metrics['memory_percent']:.1f}%")

        if metrics['disk_usage_percent'] > disk_threshold:
            warnings.append(f"High disk usage: {metrics['disk_usage_percent']:.1f}%")

        return {
            'has_warnings': len(warnings) > 0,
            'warnings': warnings,
            'metrics': metrics
        }
