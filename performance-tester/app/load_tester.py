"""
Load testing module
Performs various types of load tests on the MS-Oferta API
"""
import asyncio
import aiohttp
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from dataclasses import dataclass, field


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
    """Test run summary statistics"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_duration: float = 0.0
    avg_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    p50_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    requests_per_second: float = 0.0
    errors_per_second: float = 0.0
    status_codes: Dict[int, int] = field(default_factory=dict)


class LoadTester:
    """Main load testing class"""

    def __init__(self, base_url: str, timeout: int = 30):
        """
        Initialize load tester

        Args:
            base_url: Base URL of the API to test
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.results: List[TestResult] = []
        self.running = False
        self.progress_callback: Optional[Callable] = None

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
        """Test health check endpoint"""
        start_time = time.time()
        endpoint = f"{self.base_url}/health"

        try:
            response = requests.get(endpoint, timeout=self.timeout)
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
        """Test offer generation endpoint"""
        start_time = time.time()
        endpoint = f"{self.base_url}/api/generate-offer"
        payload = self.generate_test_request(output_format)

        try:
            response = requests.post(
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

    def _calculate_summary(self, total_duration: float) -> TestSummary:
        """Calculate test summary statistics"""
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

        # Calculate percentiles
        sorted_times = sorted(response_times)
        n = len(sorted_times)

        summary = TestSummary(
            total_requests=len(self.results),
            successful_requests=len(successful),
            failed_requests=len(failed),
            total_duration=total_duration,
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p50_response_time=sorted_times[int(n * 0.50)] if n > 0 else 0,
            p95_response_time=sorted_times[int(n * 0.95)] if n > 0 else 0,
            p99_response_time=sorted_times[int(n * 0.99)] if n > 0 else 0,
            requests_per_second=len(self.results) / total_duration if total_duration > 0 else 0,
            errors_per_second=len(failed) / total_duration if total_duration > 0 else 0,
            status_codes=status_codes
        )

        return summary

    def stop(self):
        """Stop running test"""
        self.running = False

    def get_results(self) -> List[TestResult]:
        """Get all test results"""
        return self.results
