"""
Main Flask application - MS-Oferta Performance Tester
Web dashboard for load testing and performance monitoring
"""
from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from pathlib import Path
import threading
import time
from datetime import datetime

from .config import get_settings
from .database import Database
from .monitor import SystemMonitor
from .load_tester import LoadTester
from .report_generator import ReportGenerator


# Initialize Flask app
# Fix template and static folder paths (they are in parent directory)
BASE_DIR = Path(__file__).parent.parent
app = Flask(__name__,
    template_folder=str(BASE_DIR / 'templates'),
    static_folder=str(BASE_DIR / 'static')
)
settings = get_settings()
app.config['SECRET_KEY'] = settings.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Enable CORS and WebSocket
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize components
db = Database(settings.DATABASE_DIR / "performance.db")
monitor = SystemMonitor(interval=settings.MONITOR_INTERVAL)
load_tester = LoadTester(settings.API_BASE_URL)
report_generator = ReportGenerator(settings.REPORTS_DIR)

# Global state
current_test_run_id = None
test_running = False


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/system-info')
def system_info():
    """Get system information"""
    return jsonify(monitor.get_system_info())


@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'database': 'connected',
        'monitor': 'active' if monitor.monitoring else 'inactive'
    })


@app.route('/api/test-scenarios')
def test_scenarios():
    """Get available test scenarios"""
    return jsonify(settings.TEST_SCENARIOS)


@app.route('/api/test-history')
def test_history():
    """Get test history"""
    limit = request.args.get('limit', 50, type=int)
    runs = db.get_all_test_runs(limit=limit)
    return jsonify(runs)


@app.route('/api/test-run/<int:test_run_id>')
def get_test_run(test_run_id):
    """Get detailed test run information"""
    test_run = db.get_test_run(test_run_id)
    if not test_run:
        return jsonify({'error': 'Test run not found'}), 404

    results = db.get_test_requests(test_run_id)
    metrics = db.get_system_metrics(test_run_id)
    statistics = db.get_statistics(test_run_id)

    return jsonify({
        'test_run': test_run,
        'results': results[:1000],  # Limit for performance
        'metrics': metrics[:1000],
        'statistics': statistics
    })


@app.route('/api/start-test', methods=['POST'])
def start_test():
    """Start a new performance test"""
    global current_test_run_id, test_running

    if test_running:
        return jsonify({'error': 'Test already running'}), 400

    data = request.json
    test_type = data.get('test_type', 'concurrent')
    scenario = data.get('scenario', 'standard')
    endpoint_type = data.get('endpoint_type', 'docx')

    # Get scenario config
    scenario_config = settings.TEST_SCENARIOS.get(scenario, settings.TEST_SCENARIOS['standard'])

    # Override with custom values if provided
    config = {
        'test_type': test_type,
        'scenario': scenario,
        'endpoint_type': endpoint_type,
        'num_requests': data.get('num_requests', scenario_config.get('users', 50)),
        'duration': data.get('duration', scenario_config.get('duration', 300)),
        'max_workers': data.get('max_workers', 10),
        'api_url': settings.API_BASE_URL
    }

    # Create test run in database
    test_name = data.get('test_name', f"{scenario_config['name']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    current_test_run_id = db.create_test_run(test_name, test_type, config)

    # Start test in background thread
    test_running = True
    thread = threading.Thread(
        target=run_test,
        args=(current_test_run_id, test_type, config, endpoint_type)
    )
    thread.daemon = True
    thread.start()

    return jsonify({
        'success': True,
        'test_run_id': current_test_run_id,
        'message': 'Test started successfully'
    })


@app.route('/api/stop-test', methods=['POST'])
def stop_test():
    """Stop running test"""
    global test_running

    if not test_running:
        return jsonify({'error': 'No test running'}), 400

    test_running = False
    load_tester.stop()
    monitor.stop()

    if current_test_run_id:
        db.complete_test_run(current_test_run_id)

    return jsonify({'success': True, 'message': 'Test stopped'})


@app.route('/api/generate-report/<int:test_run_id>', methods=['POST'])
def generate_report(test_run_id):
    """Generate HTML report for a test run"""
    test_run = db.get_test_run(test_run_id)
    if not test_run:
        return jsonify({'error': 'Test run not found'}), 404

    results = db.get_test_requests(test_run_id)
    metrics = db.get_system_metrics(test_run_id)

    # Convert database rows to dicts if needed
    if results and hasattr(results[0], '_asdict'):
        results = [dict(r) for r in results]
    if metrics and hasattr(metrics[0], '_asdict'):
        metrics = [dict(r) for r in metrics]

    report_path = report_generator.generate_html_report(test_run, results, metrics)

    return jsonify({
        'success': True,
        'report_path': report_path,
        'message': 'Report generated successfully'
    })


@app.route('/api/download-report/<filename>')
def download_report(filename):
    """Download generated report"""
    report_path = settings.REPORTS_DIR / filename
    if not report_path.exists():
        return jsonify({'error': 'Report not found'}), 404

    return send_file(report_path, as_attachment=True)


@app.route('/api/delete-test/<int:test_run_id>', methods=['DELETE'])
def delete_test(test_run_id):
    """Delete a test run"""
    try:
        db.delete_test_run(test_run_id)
        return jsonify({'success': True, 'message': 'Test run deleted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_test(test_run_id: int, test_type: str, config: dict, endpoint_type: str):
    """Run performance test (called in background thread)"""
    global test_running

    try:
        # Setup progress callback
        def progress_callback(message, progress):
            socketio.emit('test_progress', {
                'test_run_id': test_run_id,
                'message': message,
                'progress': progress
            })

        load_tester.set_progress_callback(progress_callback)

        # Setup system monitoring callback
        def metric_callback(metrics):
            if test_running:
                db.add_system_metric(test_run_id, metrics)
                socketio.emit('system_metrics', metrics)

        monitor.reset()
        monitor.start(callback=metric_callback)

        socketio.emit('test_started', {
            'test_run_id': test_run_id,
            'config': config
        })

        # Run test based on type - ENHANCED with burst and HTTP/2
        if test_type == 'concurrent':
            summary = load_tester.run_concurrent_test(
                num_requests=config['num_requests'],
                endpoint_type=endpoint_type,
                max_workers=config['max_workers']
            )
        elif test_type == 'async':
            summary = load_tester.run_async_test(
                num_requests=config['num_requests'],
                endpoint_type=endpoint_type
            )
        elif test_type == 'ramp':
            summary = load_tester.run_ramp_up_test(
                max_users=config['num_requests'],
                ramp_duration=60,
                test_duration=config['duration'],
                endpoint_type=endpoint_type
            )
        elif test_type == 'burst':
            # NEW: Burst test for maximum speed
            burst_size = config.get('burst_size', 100)
            num_bursts = config.get('num_bursts', 1)
            burst_delay = config.get('burst_delay', 1.0)
            summary = load_tester.run_burst_test(
                burst_size=burst_size,
                num_bursts=num_bursts,
                burst_delay=burst_delay,
                endpoint_type=endpoint_type
            )
        elif test_type == 'http2':
            # NEW: HTTP/2 test for modern servers
            summary = load_tester.run_http2_test(
                num_requests=config['num_requests'],
                endpoint_type=endpoint_type
            )
        else:
            raise ValueError(f"Unknown test type: {test_type}")

        # Save results to database
        for result in load_tester.get_results():
            db.add_request(test_run_id, {
                'timestamp': result.timestamp,
                'endpoint': result.endpoint,
                'method': result.method,
                'status_code': result.status_code,
                'response_time': result.response_time,
                'success': result.success,
                'error_message': result.error_message,
                'request_size': result.request_size,
                'response_size': result.response_size
            })

        # Update test run with summary - ENHANCED with new metrics
        db.update_test_run(test_run_id, {
            'total_requests': summary.total_requests,
            'successful_requests': summary.successful_requests,
            'failed_requests': summary.failed_requests,
            'duration_seconds': summary.total_duration,
            'avg_response_time': summary.avg_response_time,
            'min_response_time': summary.min_response_time,
            'max_response_time': summary.max_response_time,
            'p50_response_time': summary.p50_response_time,
            'p75_response_time': summary.p75_response_time,
            'p90_response_time': summary.p90_response_time,
            'p95_response_time': summary.p95_response_time,
            'p99_response_time': summary.p99_response_time,
            'p999_response_time': summary.p999_response_time,
            'requests_per_second': summary.requests_per_second,
            'errors_per_second': summary.errors_per_second,
            'throughput_mbps': summary.throughput_mbps,
            'total_bytes_sent': summary.total_bytes_sent,
            'total_bytes_received': summary.total_bytes_received,
            'std_dev_response_time': summary.std_dev_response_time,
            'status': 'completed'
        })

        db.complete_test_run(test_run_id)
        monitor.stop()

        socketio.emit('test_completed', {
            'test_run_id': test_run_id,
            'summary': {
                'total_requests': summary.total_requests,
                'successful_requests': summary.successful_requests,
                'failed_requests': summary.failed_requests,
                'avg_response_time': summary.avg_response_time,
                'requests_per_second': summary.requests_per_second
            }
        })

    except Exception as e:
        print(f"Test error: {e}")
        db.update_test_run(test_run_id, {'status': 'failed'})
        socketio.emit('test_error', {
            'test_run_id': test_run_id,
            'error': str(e)
        })
    finally:
        test_running = False
        monitor.stop()


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    emit('connected', {'message': 'Connected to MS-Oferta Performance Tester'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    pass


@socketio.on('request_system_metrics')
def handle_metrics_request():
    """Send current system metrics to client"""
    metrics = monitor.get_current_metrics()
    emit('system_metrics', metrics)


def run_server(host: str = None, port: int = None, debug: bool = False):
    """Run Flask server"""
    host = host or settings.FLASK_HOST
    port = port or settings.FLASK_PORT

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     MS-Oferta Performance Tester - Web Dashboard             ║
╚══════════════════════════════════════════════════════════════╝

Server: http://{host}:{port}
API: http://{host}:{port}/api/health
WebSocket: ws://{host}:{port}

Target API: {settings.API_BASE_URL}

Press Ctrl+C to stop
    """)

    socketio.run(app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    run_server()
