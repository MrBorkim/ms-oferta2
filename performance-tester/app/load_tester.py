"""
Load testing module - OPTIMIZED for 8 vCPU / 24GB RAM / 400GB SSD / 600 Mbit/s
Performs various types of load tests on the MS-Oferta API with maximum performance

Features:
- HTTP/2 support for faster connections
- Connection pooling and reuse
- Batch request processing
- Memory-efficient streaming
- Optimized for 8 vCPU cores
- Burst testing capabilities
"""
import asyncio
import aiohttp
import httpx
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import dataclass, field
import multiprocessing as mp


@dataclass
class TestResult:
    """Single test request result"""
    endpoint: str
    method: str
    status_code: Optional[int]
    response_time: float
    success: bool
    error_message: Optional[str] = None
    request_size: int = 0
    response_size: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestSummary:
    """Test run summary statistics - Enhanced"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p75_response_time: float = 0.0
    p90_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    p999_response_time: float = 0.0
    requests_per_second: float = 0.0
    errors_per_second: float = 0.0
    status_codes: Dict[int, int] = field(default_factory=dict)
    # Enhanced metrics
    total_bytes_sent: int = 0
    total_bytes_received: int = 0
    throughput_mbps: float = 0.0
    avg_ttfb: float = 0.0  # Time to first byte
    connection_time: float = 0.0
    std_dev_response_time: float = 0.0


@dataclass
class BurstMetrics:
    """Metrics for burst testing"""
    burst_size: int = 0
    burst_duration: float = 0.0
    burst_rps: float = 0.0
    burst_success_rate: float = 0.0
    burst_errors: int = 0


class LoadTester:
    """Main load testing class - OPTIMIZED for maximum performance"""

    def __init__(self, base_url: str, timeout: int = 60, max_workers: int = None):
        """
        Initialize load tester with connection pooling and optimization

        Args:
            base_url: Base URL of the API to test
            timeout: Request timeout in seconds
            max_workers: Maximum workers (defaults to CPU count * 2)
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.results: List[TestResult] = []
        self.running = False
        self.progress_callback: Optional[Callable] = None

        # Optimize for 8 vCPU
        cpu_count = mp.cpu_count()
        self.max_workers = max_workers or min(cpu_count * 2, 32)  # Max 32 workers for 8 vCPU

        # Setup session with connection pooling
        self.session = self._create_optimized_session()

        # HTTP/2 client (httpx)
        self.http2_limits = httpx.Limits(
            max_keepalive_connections=100,
            max_connections=200,
            keepalive_expiry=30
        )

    def _create_optimized_session(self) -> requests.Session:
        """Create requests session with connection pooling and retry logic"""
        session = requests.Session()

        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )

        # HTTP adapter with connection pooling (optimized for 8 vCPU)
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=50,  # Connection pools
            pool_maxsize=100,     # Max connections per pool
            pool_block=False
        )

        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def set_progress_callback(self, callback: Callable):
        """Set callback for progress updates"""
        self.progress_callback = callback

    def _report_progress(self, message: str, progress: float):
        """Report progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message, progress)

    def generate_test_request(self, output_format: str = "docx") -> Dict[str, Any]:
        """Generate test request payload"""
        return {
            "KLIENT(NIP)": "1234567890",
            "Oferta z dnia": datetime.now().strftime("%Y-%m-%d"),
            "wazna_do": datetime.now().strftime("%Y-%m-%d"),
            "firmaM": "Performance Test Company",
            "temat": "Load Test Offer",
            "kategoria": "Testing",
            "opis": "Automated performance testing",
            "produkty": ["1.docx", "2.docx"],
            "cena": 10000.00,
            "RBG": 100,
            "uzasadnienie": "Testing purposes",
            "output_format": output_format
        }

    def test_health_check(self) -> TestResult:
        """Test health check endpoint with connection pooling"""
        start_time = time.time()
        endpoint = f"{self.base_url}/health"

        try:
            response = self.session.get(endpoint, timeout=self.timeout)
            response_time = time.time() - start_time

            return TestResult(
                endpoint="/health",
                method="GET",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                response_size=len(response.content)
            )
        except Exception as e:
            return TestResult(
                endpoint="/health",
                method="GET",
                status_code=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    def test_generate_offer(self, output_format: str = "docx") -> TestResult:
        """Test offer generation endpoint with connection pooling"""
        start_time = time.time()
        endpoint = f"{self.base_url}/api/generate-offer"
        payload = self.generate_test_request(output_format)

        try:
            response = self.session.post(
                endpoint,
                json=payload,
                timeout=self.timeout
            )
            response_time = time.time() - start_time

            return TestResult(
                endpoint="/api/generate-offer",
                method="POST",
                status_code=response.status_code,
                response_time=response_time,
                success=response.status_code == 200,
                request_size=len(str(payload).encode()),
                response_size=len(response.content)
            )
        except Exception as e:
            return TestResult(
                endpoint="/api/generate-offer",
                method="POST",
                status_code=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    def run_concurrent_test(self, num_requests: int, endpoint_type: str = "docx",
                          max_workers: int = 10) -> TestSummary:
        """
        Run concurrent load test

        Args:
            num_requests: Number of requests to send
            endpoint_type: Type of endpoint to test (health, docx, pdf, jpg)
            max_workers: Maximum number of concurrent workers

        Returns:
            TestSummary with results
        """
        self.results.clear()
        self.running = True
        start_time = time.time()

        self._report_progress(f"Starting concurrent test with {num_requests} requests", 0)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []

            for i in range(num_requests):
                if endpoint_type == "health":
                    future = executor.submit(self.test_health_check)
                else:
                    future = executor.submit(self.test_generate_offer, endpoint_type)
                futures.append(future)

            completed = 0
            for future in as_completed(futures):
                if not self.running:
                    break

                try:
                    result = future.result()
                    self.results.append(result)
                    completed += 1

                    if completed % 10 == 0:
                        progress = (completed / num_requests) * 100
                        self._report_progress(
                            f"Completed {completed}/{num_requests} requests",
                            progress
                        )
                except Exception as e:
                    print(f"Request failed: {e}")

        total_duration = time.time() - start_time
        self._report_progress("Test completed, calculating statistics", 100)

        return self._calculate_summary(total_duration)

    async def _async_request(self, session: aiohttp.ClientSession,
                            endpoint: str, method: str = "GET",
                            payload: Optional[Dict] = None) -> TestResult:
        """Make async HTTP request"""
        start_time = time.time()
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                async with session.get(url, timeout=self.timeout) as response:
                    await response.read()
                    response_time = time.time() - start_time
                    return TestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        success=response.status == 200,
                        response_size=response.content_length or 0
                    )
            else:  # POST
                async with session.post(url, json=payload, timeout=self.timeout) as response:
                    await response.read()
                    response_time = time.time() - start_time
                    return TestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        success=response.status == 200,
                        request_size=len(str(payload).encode()) if payload else 0,
                        response_size=response.content_length or 0
                    )
        except Exception as e:
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=None,
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )

    async def _run_async_test(self, num_requests: int, endpoint_type: str = "docx") -> List[TestResult]:
        """Run async load test"""
        results = []

        async with aiohttp.ClientSession() as session:
            tasks = []

            for i in range(num_requests):
                if endpoint_type == "health":
                    task = self._async_request(session, "/health", "GET")
                else:
                    payload = self.generate_test_request(endpoint_type)
                    task = self._async_request(session, "/api/generate-offer", "POST", payload)
                tasks.append(task)

                if (i + 1) % 10 == 0:
                    progress = ((i + 1) / num_requests) * 100
                    self._report_progress(f"Queued {i + 1}/{num_requests} requests", progress)

            results = await asyncio.gather(*tasks)

        return results

    def run_async_test(self, num_requests: int, endpoint_type: str = "docx") -> TestSummary:
        """
        Run async load test (faster than concurrent for high loads)

        Args:
            num_requests: Number of requests to send
            endpoint_type: Type of endpoint to test

        Returns:
            TestSummary with results
        """
        self.results.clear()
        self.running = True
        start_time = time.time()

        self._report_progress(f"Starting async test with {num_requests} requests", 0)

        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.results = loop.run_until_complete(
                self._run_async_test(num_requests, endpoint_type)
            )
        finally:
            loop.close()

        total_duration = time.time() - start_time
        self._report_progress("Test completed", 100)

        return self._calculate_summary(total_duration)

    def run_ramp_up_test(self, max_users: int, ramp_duration: int,
                        test_duration: int, endpoint_type: str = "docx") -> TestSummary:
        """
        Run ramp-up test (gradually increase load)

        Args:
            max_users: Maximum number of concurrent users
            ramp_duration: Time to reach max users (seconds)
            test_duration: Total test duration (seconds)
            endpoint_type: Type of endpoint to test

        Returns:
            TestSummary with results
        """
        self.results.clear()
        self.running = True
        start_time = time.time()

        self._report_progress(f"Starting ramp-up test to {max_users} users", 0)

        ramp_step = max_users / (ramp_duration * 2)  # Increase every 0.5 seconds
        current_users = 0

        with ThreadPoolExecutor(max_workers=max_users) as executor:
            futures = []

            while time.time() - start_time < test_duration and self.running:
                elapsed = time.time() - start_time

                # Calculate current user count
                if elapsed < ramp_duration:
                    current_users = int(elapsed * ramp_step)
                else:
                    current_users = max_users

                # Submit requests
                while len(futures) < current_users:
                    if endpoint_type == "health":
                        future = executor.submit(self.test_health_check)
                    else:
                        future = executor.submit(self.test_generate_offer, endpoint_type)
                    futures.append(future)

                # Collect completed requests
                done_futures = [f for f in futures if f.done()]
                for future in done_futures:
                    try:
                        result = future.result()
                        self.results.append(result)
                    except Exception as e:
                        print(f"Request failed: {e}")
                    futures.remove(future)

                # Report progress
                progress = (elapsed / test_duration) * 100
                self._report_progress(
                    f"Running with {current_users} users ({len(self.results)} requests completed)",
                    progress
                )

                time.sleep(0.5)

        total_duration = time.time() - start_time
        self._report_progress("Ramp-up test completed", 100)

        return self._calculate_summary(total_duration)

    def run_burst_test(self, burst_size: int, num_bursts: int = 1,
                      burst_delay: float = 1.0, endpoint_type: str = "docx") -> TestSummary:
        """
        Run BURST test - Maximum speed generation for 600 Mbit/s connection
        Optimized for 8 vCPU / 24GB RAM

        Args:
            burst_size: Number of requests per burst (recommended: 50-200)
            num_bursts: Number of bursts to execute
            burst_delay: Delay between bursts in seconds
            endpoint_type: Type of endpoint to test

        Returns:
            TestSummary with results including burst metrics
        """
        self.results.clear()
        self.running = True
        start_time = time.time()

        self._report_progress(f"Starting BURST test: {num_bursts} bursts of {burst_size} requests", 0)

        burst_metrics = []

        for burst_num in range(num_bursts):
            if not self.running:
                break

            burst_start = time.time()
            self._report_progress(
                f"Executing burst {burst_num + 1}/{num_bursts} ({burst_size} requests)",
                (burst_num / num_bursts) * 100
            )

            # Execute burst with maximum parallelism
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = []

                for i in range(burst_size):
                    if endpoint_type == "health":
                        future = executor.submit(self.test_health_check)
                    else:
                        future = executor.submit(self.test_generate_offer, endpoint_type)
                    futures.append(future)

                # Collect all results from burst
                burst_results = []
                burst_errors = 0
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        self.results.append(result)
                        burst_results.append(result)
                        if not result.success:
                            burst_errors += 1
                    except Exception as e:
                        burst_errors += 1
                        print(f"Burst request failed: {e}")

            burst_duration = time.time() - burst_start
            burst_success_rate = ((burst_size - burst_errors) / burst_size) * 100 if burst_size > 0 else 0
            burst_rps = burst_size / burst_duration if burst_duration > 0 else 0

            burst_metrics.append(BurstMetrics(
                burst_size=burst_size,
                burst_duration=burst_duration,
                burst_rps=burst_rps,
                burst_success_rate=burst_success_rate,
                burst_errors=burst_errors
            ))

            self._report_progress(
                f"Burst {burst_num + 1} completed: {burst_rps:.2f} RPS, {burst_success_rate:.1f}% success",
                ((burst_num + 1) / num_bursts) * 100
            )

            # Delay between bursts (except last one)
            if burst_num < num_bursts - 1 and burst_delay > 0:
                time.sleep(burst_delay)

        total_duration = time.time() - start_time
        self._report_progress("Burst test completed", 100)

        summary = self._calculate_summary(total_duration)

        # Add burst metrics info to summary
        if burst_metrics:
            avg_burst_rps = statistics.mean([b.burst_rps for b in burst_metrics])
            print(f"\n📊 Burst Test Results:")
            print(f"   Average Burst RPS: {avg_burst_rps:.2f}")
            print(f"   Peak RPS: {max(b.burst_rps for b in burst_metrics):.2f}")
            print(f"   Total Bursts: {num_bursts}")

        return summary

    async def _run_http2_test(self, num_requests: int, endpoint_type: str = "docx") -> List[TestResult]:
        """
        Run HTTP/2 test for maximum performance (experimental)
        Uses httpx with HTTP/2 support

        Args:
            num_requests: Number of requests
            endpoint_type: Type of endpoint to test

        Returns:
            List of TestResult objects
        """
        results = []

        async with httpx.AsyncClient(
            http2=True,
            limits=self.http2_limits,
            timeout=httpx.Timeout(self.timeout)
        ) as client:

            async def make_request(request_num: int) -> TestResult:
                start_time = time.time()

                try:
                    if endpoint_type == "health":
                        response = await client.get(f"{self.base_url}/health")
                        endpoint = "/health"
                        method = "GET"
                    else:
                        payload = self.generate_test_request(endpoint_type)
                        response = await client.post(
                            f"{self.base_url}/api/generate-offer",
                            json=payload
                        )
                        endpoint = "/api/generate-offer"
                        method = "POST"

                    response_time = time.time() - start_time

                    return TestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status_code,
                        response_time=response_time,
                        success=response.status_code == 200,
                        response_size=len(response.content)
                    )
                except Exception as e:
                    return TestResult(
                        endpoint=endpoint if 'endpoint' in locals() else "/unknown",
                        method=method if 'method' in locals() else "UNKNOWN",
                        status_code=None,
                        response_time=time.time() - start_time,
                        success=False,
                        error_message=str(e)
                    )

            # Create tasks with progress reporting
            tasks = []
            for i in range(num_requests):
                task = make_request(i)
                tasks.append(task)

                if (i + 1) % 50 == 0:
                    self._report_progress(
                        f"HTTP/2 test: queued {i + 1}/{num_requests} requests",
                        ((i + 1) / num_requests) * 50
                    )

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=False)

        return results

    def run_http2_test(self, num_requests: int, endpoint_type: str = "docx") -> TestSummary:
        """
        Run HTTP/2 test - Maximum performance for modern servers
        Best for 600 Mbit/s connections

        Args:
            num_requests: Number of requests to send
            endpoint_type: Type of endpoint to test

        Returns:
            TestSummary with results
        """
        self.results.clear()
        self.running = True
        start_time = time.time()

        self._report_progress(f"Starting HTTP/2 test with {num_requests} requests", 0)

        # Run HTTP/2 test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            self.results = loop.run_until_complete(
                self._run_http2_test(num_requests, endpoint_type)
            )
        finally:
            loop.close()

        total_duration = time.time() - start_time
        self._report_progress("HTTP/2 test completed", 100)

        return self._calculate_summary(total_duration)

    def _calculate_summary(self, total_duration: float) -> TestSummary:
        """Calculate test summary statistics - Enhanced with more metrics"""
        if not self.results:
            return TestSummary()

        response_times = [r.response_time for r in self.results]
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        # Status code distribution
        status_codes = {}
        for result in self.results:
            if result.status_code:
                status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1

        # Calculate total bytes
        total_bytes_sent = sum(r.request_size for r in self.results)
        total_bytes_received = sum(r.response_size for r in self.results)

        # Calculate throughput in Mbps
        total_bytes = total_bytes_sent + total_bytes_received
        throughput_mbps = (total_bytes * 8) / (total_duration * 1_000_000) if total_duration > 0 else 0

        # Calculate percentiles
        sorted_times = sorted(response_times)
        n = len(sorted_times)

        # Standard deviation
        std_dev = statistics.stdev(response_times) if len(response_times) > 1 else 0

        summary = TestSummary(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            total_duration=total_duration,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p50_response_time=sorted_times[int(n * 0.50)] if n > 0 else 0,
            p75_response_time=sorted_times[int(n * 0.75)] if n > 0 else 0,
            p90_response_time=sorted_times[int(n * 0.90)] if n > 0 else 0,
            p95_response_time=sorted_times[int(n * 0.95)] if n > 0 else 0,
            p99_response_time=sorted_times[int(n * 0.99)] if n > 0 else 0,
            p999_response_time=sorted_times[int(n * 0.999)] if n >= 1000 else (sorted_times[-1] if n > 0 else 0),
            requests_per_second=len(self.results) / total_duration if total_duration > 0 else 0,
            errors_per_second=len(failed) / total_duration if total_duration > 0 else 0,
            status_codes=status_codes,
            total_bytes_sent=total_bytes_sent,
            total_bytes_received=total_bytes_received,
            throughput_mbps=throughput_mbps,
            std_dev_response_time=std_dev
        )

        return summary

    def stop(self):
        """Stop running test"""
        self.running = False

    def get_results(self) -> List[TestResult]:
        """Get all test results"""
        return self.results

    def cleanup(self):
        """Cleanup resources - close session"""
        if hasattr(self, 'session'):
            self.session.close()

    def __del__(self):
        """Destructor - ensure cleanup"""
        self.cleanup()
