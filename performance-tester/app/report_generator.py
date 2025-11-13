"""
Report generation module with charts and visualizations
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json


class ReportGenerator:
    """Generate performance test reports with visualizations"""

    def __init__(self, output_dir: Path):
        """
        Initialize report generator

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_response_time_chart(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Generate response time distribution chart"""
        if not results:
            return go.Figure()

        response_times = [r['response_time'] for r in results]
        timestamps = [r.get('timestamp', i) for i, r in enumerate(results)]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Response Time Over Time', 'Response Time Distribution'),
            vertical_spacing=0.15
        )

        # Time series
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=response_times,
                mode='lines',
                name='Response Time',
                line=dict(color='#3498db', width=2)
            ),
            row=1, col=1
        )

        # Histogram
        fig.add_trace(
            go.Histogram(
                x=response_times,
                nbinsx=50,
                name='Distribution',
                marker=dict(color='#2ecc71')
            ),
            row=2, col=1
        )

        fig.update_xaxes(title_text="Request Number", row=1, col=1)
        fig.update_yaxes(title_text="Response Time (s)", row=1, col=1)
        fig.update_xaxes(title_text="Response Time (s)", row=2, col=1)
        fig.update_yaxes(title_text="Count", row=2, col=1)

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="Response Time Analysis",
            title_font_size=20
        )

        return fig

    def generate_throughput_chart(self, results: List[Dict[str, Any]],
                                  window_size: int = 10) -> go.Figure:
        """Generate requests per second chart"""
        if not results:
            return go.Figure()

        # Calculate rolling throughput
        timestamps = []
        throughputs = []

        for i in range(window_size, len(results)):
            window = results[i-window_size:i]
            if window:
                time_diff = window[-1]['response_time'] - window[0]['response_time']
                if time_diff > 0:
                    rps = window_size / time_diff
                    throughputs.append(rps)
                    timestamps.append(i)

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=timestamps,
            y=throughputs,
            mode='lines',
            name='Requests/Second',
            line=dict(color='#e74c3c', width=2),
            fill='tozeroy'
        ))

        fig.update_layout(
            title='Throughput Over Time',
            xaxis_title='Request Number',
            yaxis_title='Requests per Second',
            height=400,
            showlegend=False
        )

        return fig

    def generate_percentile_chart(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Generate percentile response time chart"""
        if not results:
            return go.Figure()

        response_times = sorted([r['response_time'] for r in results])
        n = len(response_times)

        percentiles = [50, 75, 90, 95, 99]
        values = []

        for p in percentiles:
            idx = int(n * p / 100)
            if idx < n:
                values.append(response_times[idx])
            else:
                values.append(response_times[-1])

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[f'P{p}' for p in percentiles],
            y=values,
            marker=dict(
                color=values,
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Time (s)")
            ),
            text=[f'{v:.3f}s' for v in values],
            textposition='auto'
        ))

        fig.update_layout(
            title='Response Time Percentiles',
            xaxis_title='Percentile',
            yaxis_title='Response Time (s)',
            height=400,
            showlegend=False
        )

        return fig

    def generate_status_code_chart(self, results: List[Dict[str, Any]]) -> go.Figure:
        """Generate status code distribution chart"""
        if not results:
            return go.Figure()

        # Count status codes
        status_counts = {}
        for r in results:
            code = r.get('status_code', 'None')
            status_counts[str(code)] = status_counts.get(str(code), 0) + 1

        # Define colors
        colors = {
            '200': '#2ecc71',  # Green for success
            '201': '#2ecc71',
            '400': '#f39c12',  # Orange for client errors
            '404': '#f39c12',
            '500': '#e74c3c',  # Red for server errors
            '502': '#e74c3c',
            '503': '#e74c3c',
            'None': '#95a5a6'  # Gray for no response
        }

        fig = go.Figure()

        fig.add_trace(go.Pie(
            labels=list(status_counts.keys()),
            values=list(status_counts.values()),
            marker=dict(colors=[colors.get(str(k), '#3498db') for k in status_counts.keys()]),
            textinfo='label+percent+value',
            hovertemplate='Status Code: %{label}<br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
        ))

        fig.update_layout(
            title='HTTP Status Code Distribution',
            height=400
        )

        return fig

    def generate_system_metrics_chart(self, metrics: List[Dict[str, Any]]) -> go.Figure:
        """Generate system resource usage chart"""
        if not metrics:
            return go.Figure()

        timestamps = [m.get('timestamp', i) for i, m in enumerate(metrics)]
        cpu = [m.get('cpu_percent', 0) for m in metrics]
        memory = [m.get('memory_percent', 0) for m in metrics]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('CPU Usage', 'Memory Usage'),
            vertical_spacing=0.15
        )

        # CPU
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cpu,
                mode='lines',
                name='CPU %',
                line=dict(color='#e74c3c', width=2),
                fill='tozeroy'
            ),
            row=1, col=1
        )

        # Memory
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=memory,
                mode='lines',
                name='Memory %',
                line=dict(color='#3498db', width=2),
                fill='tozeroy'
            ),
            row=2, col=1
        )

        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_yaxes(title_text="CPU %", row=1, col=1, range=[0, 100])
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="Memory %", row=2, col=1, range=[0, 100])

        fig.update_layout(
            height=800,
            showlegend=False,
            title_text="System Resource Usage",
            title_font_size=20
        )

        return fig

    def generate_io_metrics_chart(self, metrics: List[Dict[str, Any]]) -> go.Figure:
        """Generate disk and network I/O chart"""
        if not metrics:
            return go.Figure()

        timestamps = [m.get('timestamp', i) for i, m in enumerate(metrics)]
        disk_read = [m.get('disk_io_read_mb', 0) for m in metrics]
        disk_write = [m.get('disk_io_write_mb', 0) for m in metrics]
        net_sent = [m.get('network_sent_mb', 0) for m in metrics]
        net_recv = [m.get('network_recv_mb', 0) for m in metrics]

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Disk I/O', 'Network I/O'),
            vertical_spacing=0.15
        )

        # Disk I/O
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=disk_read,
                mode='lines',
                name='Disk Read',
                line=dict(color='#3498db', width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=disk_write,
                mode='lines',
                name='Disk Write',
                line=dict(color='#e74c3c', width=2)
            ),
            row=1, col=1
        )

        # Network I/O
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=net_sent,
                mode='lines',
                name='Network Sent',
                line=dict(color='#2ecc71', width=2)
            ),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=net_recv,
                mode='lines',
                name='Network Received',
                line=dict(color='#f39c12', width=2)
            ),
            row=2, col=1
        )

        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_yaxes(title_text="MB", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_yaxes(title_text="MB", row=2, col=1)

        fig.update_layout(
            height=800,
            title_text="I/O Metrics",
            title_font_size=20
        )

        return fig

    def generate_html_report(self, test_run: Dict[str, Any],
                           results: List[Dict[str, Any]],
                           metrics: List[Dict[str, Any]]) -> str:
        """
        Generate complete HTML report

        Returns:
            Path to generated report
        """
        # Generate all charts
        response_time_chart = self.generate_response_time_chart(results)
        throughput_chart = self.generate_throughput_chart(results)
        percentile_chart = self.generate_percentile_chart(results)
        status_chart = self.generate_status_code_chart(results)
        system_chart = self.generate_system_metrics_chart(metrics)
        io_chart = self.generate_io_metrics_chart(metrics)

        # Create HTML
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Performance Test Report - {test_run.get('test_name', 'Unknown')}</title>
    <meta charset="utf-8">
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f6fa;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric.success {{
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        }}
        .metric.warning {{
            background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        }}
        .metric.error {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 14px;
            opacity: 0.9;
        }}
        .chart {{
            margin: 30px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
            margin: 20px 0;
        }}
        .info-item {{
            padding: 15px;
            background: #ecf0f1;
            border-radius: 5px;
        }}
        .info-label {{
            font-weight: bold;
            color: #7f8c8d;
            font-size: 12px;
            text-transform: uppercase;
        }}
        .info-value {{
            font-size: 16px;
            color: #2c3e50;
            margin-top: 5px;
        }}
    </style>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
</head>
<body>
    <div class="container">
        <h1>📊 Performance Test Report</h1>

        <div class="info-grid">
            <div class="info-item">
                <div class="info-label">Test Name</div>
                <div class="info-value">{test_run.get('test_name', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Test Type</div>
                <div class="info-value">{test_run.get('test_type', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Start Time</div>
                <div class="info-value">{test_run.get('start_time', 'N/A')}</div>
            </div>
            <div class="info-item">
                <div class="info-label">Duration</div>
                <div class="info-value">{test_run.get('duration_seconds', 0):.2f} seconds</div>
            </div>
        </div>

        <h2>Summary Metrics</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{test_run.get('total_requests', 0)}</div>
            </div>
            <div class="metric success">
                <div class="metric-label">Successful</div>
                <div class="metric-value">{test_run.get('successful_requests', 0)}</div>
            </div>
            <div class="metric error">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{test_run.get('failed_requests', 0)}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Avg Response Time</div>
                <div class="metric-value">{test_run.get('avg_response_time', 0):.3f}s</div>
            </div>
            <div class="metric">
                <div class="metric-label">P95 Response Time</div>
                <div class="metric-value">{test_run.get('p95_response_time', 0):.3f}s</div>
            </div>
            <div class="metric">
                <div class="metric-label">Requests/Second</div>
                <div class="metric-value">{test_run.get('requests_per_second', 0):.2f}</div>
            </div>
        </div>

        <h2>Response Time Analysis</h2>
        <div class="chart" id="response-time-chart"></div>

        <h2>Throughput</h2>
        <div class="chart" id="throughput-chart"></div>

        <h2>Percentiles</h2>
        <div class="chart" id="percentile-chart"></div>

        <h2>Status Codes</h2>
        <div class="chart" id="status-chart"></div>

        <h2>System Resources</h2>
        <div class="chart" id="system-chart"></div>

        <h2>I/O Metrics</h2>
        <div class="chart" id="io-chart"></div>

        <footer style="margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 12px;">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by MS-Oferta Performance Tester
        </footer>
    </div>

    <script>
        Plotly.newPlot('response-time-chart', {response_time_chart.to_json()}.data, {response_time_chart.to_json()}.layout);
        Plotly.newPlot('throughput-chart', {throughput_chart.to_json()}.data, {throughput_chart.to_json()}.layout);
        Plotly.newPlot('percentile-chart', {percentile_chart.to_json()}.data, {percentile_chart.to_json()}.layout);
        Plotly.newPlot('status-chart', {status_chart.to_json()}.data, {status_chart.to_json()}.layout);
        Plotly.newPlot('system-chart', {system_chart.to_json()}.data, {system_chart.to_json()}.layout);
        Plotly.newPlot('io-chart', {io_chart.to_json()}.data, {io_chart.to_json()}.layout);
    </script>
</body>
</html>
"""

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.output_dir / f"report_{timestamp}.html"
        report_path.write_text(html_content, encoding='utf-8')

        return str(report_path)

    def export_json(self, test_run: Dict[str, Any],
                   results: List[Dict[str, Any]],
                   metrics: List[Dict[str, Any]]) -> str:
        """Export test results as JSON"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = self.output_dir / f"results_{timestamp}.json"

        data = {
            'test_run': test_run,
            'results': results,
            'metrics': metrics,
            'generated_at': datetime.now().isoformat()
        }

        json_path.write_text(json.dumps(data, indent=2, default=str), encoding='utf-8')
        return str(json_path)
