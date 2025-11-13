"""
Configuration module for MS-Oferta Performance Tester
Optimized for 8 vCPU, 24GB RAM, 400GB SSD, 600 Mbit/s server
"""
import os
from pathlib import Path
from typing import Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""

    # Base directories
    BASE_DIR: Path = Path(__file__).parent.parent
    DATABASE_DIR: Path = BASE_DIR / "database"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    LOGS_DIR: Path = BASE_DIR / "logs"

    # API endpoints to test
    API_BASE_URL: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    API_ENDPOINTS: Dict[str, str] = {
        "health": "/health",
        "generate_docx": "/api/generate-offer",
        "generate_pdf": "/api/generate-offer",
        "generate_jpg": "/api/generate-offer",
        "list_products": "/api/list-produkty",
    }

    # Load testing configuration (optimized for 8 vCPU server)
    DEFAULT_USERS: int = 50
    MAX_USERS: int = 500
    SPAWN_RATE: int = 10  # users per second
    TEST_DURATION: int = 300  # seconds

    # Concurrent testing
    CONCURRENT_REQUESTS_MIN: int = 1
    CONCURRENT_REQUESTS_MAX: int = 200
    CONCURRENT_REQUESTS_STEP: int = 10

    # Performance thresholds
    RESPONSE_TIME_WARNING: float = 2.0  # seconds
    RESPONSE_TIME_ERROR: float = 5.0  # seconds
    ERROR_RATE_WARNING: float = 0.05  # 5%
    ERROR_RATE_ERROR: float = 0.10  # 10%

    # System monitoring
    MONITOR_INTERVAL: float = 1.0  # seconds
    CPU_WARNING: float = 80.0  # percentage
    MEMORY_WARNING: float = 85.0  # percentage
    DISK_WARNING: float = 90.0  # percentage

    # Database
    DATABASE_URL: str = f"sqlite:///{DATABASE_DIR}/performance.db"

    # Flask settings
    FLASK_HOST: str = "0.0.0.0"
    FLASK_PORT: int = 5000
    FLASK_DEBUG: bool = False
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")

    # Test scenarios - OPTIMIZED for 8 vCPU / 24GB RAM / 400GB SSD / 600 Mbit/s
    TEST_SCENARIOS: Dict[str, Dict[str, Any]] = {
        "quick": {
            "name": "Quick Test",
            "duration": 60,
            "users": 10,
            "description": "Fast test to verify basic functionality"
        },
        "standard": {
            "name": "Standard Load Test",
            "duration": 300,
            "users": 50,
            "description": "Standard load test with moderate traffic"
        },
        "heavy": {
            "name": "Heavy Load Test",
            "duration": 600,
            "users": 100,
            "description": "Heavy load test to stress the system"
        },
        "stress": {
            "name": "Stress Test",
            "duration": 900,
            "users": 200,
            "description": "Stress test to find system limits"
        },
        "spike": {
            "name": "Spike Test",
            "duration": 300,
            "users": 300,
            "description": "Sudden spike in traffic"
        },
        "endurance": {
            "name": "Endurance Test",
            "duration": 3600,
            "users": 50,
            "description": "Long-running test to check stability"
        },
        # NEW: Advanced scenarios for 8 vCPU / 600 Mbit/s
        "burst_100": {
            "name": "Burst Test - 100 RPS",
            "duration": 60,
            "users": 100,
            "burst_size": 100,
            "num_bursts": 5,
            "burst_delay": 10,
            "description": "5 bursts of 100 requests, 10s apart - tests peak capacity"
        },
        "burst_200": {
            "name": "Burst Test - 200 RPS",
            "duration": 120,
            "users": 200,
            "burst_size": 200,
            "num_bursts": 3,
            "burst_delay": 20,
            "description": "3 bursts of 200 requests - stress test for 8 vCPU"
        },
        "extreme_500": {
            "name": "Extreme Load - 500 RPS",
            "duration": 180,
            "users": 500,
            "description": "500 concurrent requests - MAXIMUM LOAD for 600 Mbit/s"
        },
        "http2_ultra": {
            "name": "HTTP/2 Ultra Fast",
            "duration": 300,
            "users": 300,
            "description": "HTTP/2 test - 300 requests for maximum throughput"
        },
        "sustained_high": {
            "name": "Sustained High Load",
            "duration": 600,
            "users": 150,
            "description": "10 min sustained high load - 150 concurrent users"
        },
        "mega_burst": {
            "name": "MEGA Burst - Max Speed",
            "duration": 300,
            "users": 500,
            "burst_size": 500,
            "num_bursts": 10,
            "burst_delay": 15,
            "description": "🚀 MEGA TEST: 10 bursts of 500 requests - ULTIMATE STRESS"
        }
    }

    # Sample test data
    SAMPLE_REQUEST: Dict[str, Any] = {
        "KLIENT(NIP)": "1234567890",
        "Oferta z dnia": "2024-11-13",
        "wazna_do": "2024-12-13",
        "firmaM": "Test Company Sp. z o.o.",
        "temat": "Performance Test Offer",
        "kategoria": "IT",
        "opis": "Automated performance testing",
        "produkty": ["1.docx", "2.docx"],
        "cena": 15000.00,
        "RBG": 120,
        "uzasadnienie": "Performance testing purposes",
        "output_format": "docx"
    }

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    """Get application settings instance"""
    return Settings()


# Create required directories
settings = get_settings()
for directory in [settings.DATABASE_DIR, settings.REPORTS_DIR, settings.LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
