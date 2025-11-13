#!/usr/bin/env python3
"""
MS-Oferta Performance Tester - CLI Tool
Command-line interface for quick testing without web UI
"""
import sys
import argparse
import time
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.panel import Panel
from rich.layout import Layout
from rich import box

# Add app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from app.database import Database
from app.monitor import SystemMonitor
from app.load_tester import LoadTester, TestSummary
from app.report_generator import ReportGenerator

console = Console()
settings = get_settings()


def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║     MS-Oferta Performance Tester - CLI Mode                  ║
║     Professional Load Testing Tool                           ║
╚══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold blue")


def run_quick_test(args):
    """Run a quick test"""
    console.print("\n[bold yellow]Starting Quick Test...[/bold yellow]\n")

    # Initialize components
    tester = LoadTester(args.url, timeout=args.timeout)
    monitor = SystemMonitor(interval=1.0)

    # Test configuration
    console.print(Panel.fit(
        f"[bold]Test Configuration[/bold]\n\n"
        f"URL: {args.url}\n"
        f"Endpoint: {args.endpoint}\n"
        f"Requests: {args.requests}\n"
        f"Workers: {args.workers}\n"
        f"Type: {args.type}",
        border_style="blue"
    ))

    # Start monitoring
    monitor.start()

    # Run test with progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:

        task = progress.add_task(
            f"[cyan]Running {args.type} test...",
            total=100
        )

        def progress_callback(message, percent):
            progress.update(task, completed=percent, description=f"[cyan]{message}")

        tester.set_progress_callback(progress_callback)

        # Run the test
        start_time = time.time()

        if args.type == 'concurrent':
            summary = tester.run_concurrent_test(
                num_requests=args.requests,
                endpoint_type=args.endpoint,
                max_workers=args.workers
            )
        elif args.type == 'async':
            summary = tester.run_async_test(
                num_requests=args.requests,
                endpoint_type=args.endpoint
            )
        else:
            console.print("[red]Unknown test type![/red]")
            return

        elapsed = time.time() - start_time

    # Stop monitoring
    monitor.stop()
    stats = monitor.get_statistics()

    # Print results
    print_test_results(summary, stats, elapsed)


def print_test_results(summary: TestSummary, system_stats: dict, elapsed: float):
    """Print test results in a nice table"""
    console.print("\n[bold green]✅ Test Completed![/bold green]\n")

    # Request statistics table
    req_table = Table(title="Request Statistics", box=box.ROUNDED, border_style="green")
    req_table.add_column("Metric", style="cyan", justify="left")
    req_table.add_column("Value", style="white", justify="right")

    req_table.add_row("Total Requests", str(summary.total_requests))
    req_table.add_row("Successful", f"[green]{summary.successful_requests}[/green]")
    req_table.add_row("Failed", f"[red]{summary.failed_requests}[/red]")
    req_table.add_row("Success Rate", f"{(summary.successful_requests/summary.total_requests*100):.2f}%")
    req_table.add_row("Total Duration", f"{elapsed:.2f}s")
    req_table.add_row("", "")
    req_table.add_row("Avg Response Time", f"{summary.avg_response_time:.3f}s")
    req_table.add_row("Min Response Time", f"{summary.min_response_time:.3f}s")
    req_table.add_row("Max Response Time", f"{summary.max_response_time:.3f}s")
    req_table.add_row("", "")
    req_table.add_row("P50 (Median)", f"{summary.p50_response_time:.3f}s")
    req_table.add_row("P95", f"{summary.p95_response_time:.3f}s")
    req_table.add_row("P99", f"{summary.p99_response_time:.3f}s")
    req_table.add_row("", "")
    req_table.add_row("Requests/Second", f"{summary.requests_per_second:.2f}")
    req_table.add_row("Errors/Second", f"{summary.errors_per_second:.2f}")

    console.print(req_table)

    # System statistics table
    if system_stats:
        sys_table = Table(title="System Resources", box=box.ROUNDED, border_style="blue")
        sys_table.add_column("Resource", style="cyan", justify="left")
        sys_table.add_column("Average", style="white", justify="right")
        sys_table.add_column("Maximum", style="white", justify="right")

        if 'cpu' in system_stats:
            sys_table.add_row(
                "CPU Usage",
                f"{system_stats['cpu']['avg']:.1f}%",
                f"{system_stats['cpu']['max']:.1f}%"
            )
        if 'memory' in system_stats:
            sys_table.add_row(
                "Memory Usage",
                f"{system_stats['memory']['avg']:.1f}%",
                f"{system_stats['memory']['max']:.1f}%"
            )
        if 'disk_io' in system_stats:
            sys_table.add_row(
                "Disk Read",
                f"{system_stats['disk_io']['total_read_mb']:.2f} MB",
                "-"
            )
            sys_table.add_row(
                "Disk Write",
                f"{system_stats['disk_io']['total_write_mb']:.2f} MB",
                "-"
            )
        if 'network_io' in system_stats:
            sys_table.add_row(
                "Network Sent",
                f"{system_stats['network_io']['total_sent_mb']:.2f} MB",
                "-"
            )
            sys_table.add_row(
                "Network Received",
                f"{system_stats['network_io']['total_recv_mb']:.2f} MB",
                "-"
            )

        console.print("\n")
        console.print(sys_table)

    # Status codes
    if summary.status_codes:
        console.print("\n[bold]Status Code Distribution:[/bold]")
        for code, count in sorted(summary.status_codes.items()):
            color = "green" if code == 200 else "red"
            console.print(f"  [{color}]{code}[/{color}]: {count}")


def list_scenarios():
    """List available test scenarios"""
    table = Table(title="Available Test Scenarios", box=box.ROUNDED)
    table.add_column("Scenario", style="cyan")
    table.add_column("Duration", style="yellow")
    table.add_column("Users", style="magenta")
    table.add_column("Description", style="white")

    for key, scenario in settings.TEST_SCENARIOS.items():
        table.add_row(
            key,
            f"{scenario['duration']}s",
            str(scenario['users']),
            scenario['description']
        )

    console.print(table)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='MS-Oferta Performance Tester - CLI Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with 50 requests
  python cli.py test -r 50 -w 10

  # Test PDF generation
  python cli.py test -e pdf -r 100

  # Async test with 500 requests
  python cli.py test -t async -r 500

  # List available scenarios
  python cli.py scenarios
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run performance test')
    test_parser.add_argument('-u', '--url', default=settings.API_BASE_URL,
                           help='API base URL (default: from config)')
    test_parser.add_argument('-e', '--endpoint', default='docx',
                           choices=['health', 'docx', 'pdf', 'jpg'],
                           help='Endpoint to test (default: docx)')
    test_parser.add_argument('-r', '--requests', type=int, default=50,
                           help='Number of requests (default: 50)')
    test_parser.add_argument('-w', '--workers', type=int, default=10,
                           help='Number of workers (default: 10)')
    test_parser.add_argument('-t', '--type', default='concurrent',
                           choices=['concurrent', 'async'],
                           help='Test type (default: concurrent)')
    test_parser.add_argument('--timeout', type=int, default=30,
                           help='Request timeout in seconds (default: 30)')

    # Scenarios command
    subparsers.add_parser('scenarios', help='List available test scenarios')

    args = parser.parse_args()

    print_banner()

    if args.command == 'test':
        run_quick_test(args)
    elif args.command == 'scenarios':
        list_scenarios()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Test interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)
