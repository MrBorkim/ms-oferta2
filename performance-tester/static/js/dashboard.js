// MS-Oferta Performance Tester - Dashboard JavaScript

// Initialize Socket.IO connection
const socket = io();

// Global state
let currentTestRunId = null;
let testRunning = false;
let cpuData = [];
let memoryData = [];
let timestamps = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
    loadSystemInfo();
    loadTestHistory();
    initializeCharts();
    setupEventListeners();
});

// WebSocket initialization
function initializeWebSocket() {
    socket.on('connect', function() {
        updateConnectionStatus('connected');
        addLog('Connected to server', 'success');
    });

    socket.on('disconnect', function() {
        updateConnectionStatus('disconnected');
        addLog('Disconnected from server', 'error');
    });

    socket.on('connected', function(data) {
        addLog(data.message, 'success');
    });

    socket.on('test_started', function(data) {
        currentTestRunId = data.test_run_id;
        showProgressCard();
        addLog(`Test started (ID: ${currentTestRunId})`, 'success');
    });

    socket.on('test_progress', function(data) {
        updateProgress(data.progress, data.message);
    });

    socket.on('test_completed', function(data) {
        testRunning = false;
        hideProgressCard();
        updateTestButtons(false);
        addLog('Test completed successfully!', 'success');
        addLog(`Results: ${data.summary.total_requests} requests, ` +
               `${data.summary.successful_requests} successful, ` +
               `avg ${data.summary.avg_response_time.toFixed(3)}s`, 'success');
        loadTestHistory();
    });

    socket.on('test_error', function(data) {
        testRunning = false;
        hideProgressCard();
        updateTestButtons(false);
        addLog(`Test error: ${data.error}`, 'error');
    });

    socket.on('system_metrics', function(data) {
        updateSystemMetrics(data);
        updateLiveCharts(data);
    });
}

// Update connection status indicator
function updateConnectionStatus(status) {
    const statusBadge = document.getElementById('connectionStatus');
    statusBadge.className = 'status-badge';

    if (status === 'connected') {
        statusBadge.classList.add('status-running');
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Connected';
    } else {
        statusBadge.classList.add('status-stopped');
        statusBadge.innerHTML = '<i class="bi bi-circle-fill"></i> Disconnected';
    }
}

// Load system information
async function loadSystemInfo() {
    try {
        const response = await fetch('/api/system-info');
        const data = await response.json();

        const infoHtml = `
            <span class="system-info-badge"><i class="bi bi-cpu"></i> ${data.cpu_cores} Cores / ${data.cpu_threads} Threads</span>
            <span class="system-info-badge"><i class="bi bi-memory"></i> ${data.total_memory_gb.toFixed(1)} GB RAM</span>
            <span class="system-info-badge"><i class="bi bi-hdd"></i> ${data.total_disk_gb.toFixed(1)} GB Disk</span>
            <span class="system-info-badge"><i class="bi bi-pc-display"></i> ${data.platform}</span>
            <span class="system-info-badge"><i class="bi bi-processor"></i> ${data.processor}</span>
        `;

        document.getElementById('systemInfo').innerHTML = infoHtml;
    } catch (error) {
        console.error('Error loading system info:', error);
        document.getElementById('systemInfo').innerHTML = '<span class="text-danger">Failed to load system information</span>';
    }
}

// Load test history
async function loadTestHistory() {
    try {
        const response = await fetch('/api/test-history?limit=20');
        const tests = await response.json();

        const historyContainer = document.getElementById('testHistory');

        if (tests.length === 0) {
            historyContainer.innerHTML = '<div class="text-center p-4 text-muted">No test history yet</div>';
            return;
        }

        let html = '';
        tests.forEach(test => {
            const statusClass = test.status === 'completed' ? 'success' : test.status === 'running' ? 'warning' : 'danger';
            const successRate = test.total_requests > 0
                ? ((test.successful_requests / test.total_requests) * 100).toFixed(1)
                : 0;

            html += `
                <div class="test-history-item" onclick="viewTestDetails(${test.id})">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${test.test_name}</strong>
                            <span class="badge bg-${statusClass} ms-2">${test.status}</span>
                        </div>
                        <small class="text-muted">${formatDate(test.start_time)}</small>
                    </div>
                    <small class="text-muted">
                        ${test.total_requests || 0} requests |
                        ${successRate}% success |
                        ${(test.avg_response_time || 0).toFixed(3)}s avg
                    </small>
                </div>
            `;
        });

        historyContainer.innerHTML = html;
    } catch (error) {
        console.error('Error loading test history:', error);
    }
}

// View test details
async function viewTestDetails(testRunId) {
    try {
        const response = await fetch(`/api/test-run/${testRunId}`);
        const data = await response.json();

        // Show modal or navigate to detailed view
        alert(`Test Run ${testRunId}\n\n` +
              `Total Requests: ${data.test_run.total_requests}\n` +
              `Successful: ${data.test_run.successful_requests}\n` +
              `Failed: ${data.test_run.failed_requests}\n` +
              `Avg Response Time: ${data.test_run.avg_response_time?.toFixed(3)}s\n` +
              `P95: ${data.test_run.p95_response_time?.toFixed(3)}s\n` +
              `RPS: ${data.test_run.requests_per_second?.toFixed(2)}`);

        // Generate report
        if (confirm('Generate HTML report for this test?')) {
            await generateReport(testRunId);
        }
    } catch (error) {
        console.error('Error loading test details:', error);
        alert('Failed to load test details');
    }
}

// Generate report
async function generateReport(testRunId) {
    try {
        const response = await fetch(`/api/generate-report/${testRunId}`, {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            addLog(`Report generated: ${data.report_path}`, 'success');
            alert('Report generated successfully!\n\nPath: ' + data.report_path);
        }
    } catch (error) {
        console.error('Error generating report:', error);
        alert('Failed to generate report');
    }
}

// Start test
async function startTest() {
    if (testRunning) {
        alert('Test already running!');
        return;
    }

    const config = {
        test_name: document.getElementById('testName').value ||
                   `Test ${new Date().toLocaleString()}`,
        scenario: document.getElementById('testScenario').value,
        test_type: document.getElementById('testType').value,
        endpoint_type: document.getElementById('endpointType').value,
        num_requests: parseInt(document.getElementById('numRequests').value),
        max_workers: parseInt(document.getElementById('maxWorkers').value)
    };

    try {
        addLog('Starting test...', 'success');
        const response = await fetch('/api/start-test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });

        const data = await response.json();

        if (data.success) {
            testRunning = true;
            currentTestRunId = data.test_run_id;
            updateTestButtons(true);
            showMetrics();
            addLog(data.message, 'success');
        } else {
            addLog(`Error: ${data.error}`, 'error');
        }
    } catch (error) {
        console.error('Error starting test:', error);
        addLog(`Failed to start test: ${error.message}`, 'error');
    }
}

// Stop test
async function stopTest() {
    if (!testRunning) {
        return;
    }

    if (!confirm('Are you sure you want to stop the test?')) {
        return;
    }

    try {
        const response = await fetch('/api/stop-test', {
            method: 'POST'
        });
        const data = await response.json();

        if (data.success) {
            testRunning = false;
            updateTestButtons(false);
            hideProgressCard();
            addLog('Test stopped by user', 'error');
        }
    } catch (error) {
        console.error('Error stopping test:', error);
    }
}

// Update test buttons
function updateTestButtons(running) {
    const startBtn = document.getElementById('startTestBtn');
    const stopBtn = document.getElementById('stopTestBtn');

    if (running) {
        startBtn.style.display = 'none';
        stopBtn.style.display = 'block';
        document.getElementById('testConfigForm').querySelectorAll('input, select').forEach(el => {
            el.disabled = true;
        });
    } else {
        startBtn.style.display = 'block';
        stopBtn.style.display = 'none';
        document.getElementById('testConfigForm').querySelectorAll('input, select').forEach(el => {
            el.disabled = false;
        });
    }
}

// Show/hide progress card
function showProgressCard() {
    document.getElementById('progressCard').style.display = 'block';
    updateProgress(0, 'Starting test...');
}

function hideProgressCard() {
    document.getElementById('progressCard').style.display = 'none';
}

// Update progress bar
function updateProgress(percent, message) {
    const progressBar = document.getElementById('testProgress');
    const progressMessage = document.getElementById('progressMessage');

    progressBar.style.width = `${percent}%`;
    progressBar.textContent = `${Math.round(percent)}%`;
    progressMessage.textContent = message;
}

// Show metrics
function showMetrics() {
    document.getElementById('metricsRow').style.display = 'flex';
}

// Update system metrics display
function updateSystemMetrics(metrics) {
    document.getElementById('cpuMetric').textContent =
        `${metrics.cpu_percent.toFixed(1)}%`;
    document.getElementById('memoryMetric').textContent =
        `${metrics.memory_percent.toFixed(1)}%`;

    // These will be calculated from test results
    // For now, just show placeholder
}

// Initialize charts
function initializeCharts() {
    const layout = {
        margin: { t: 30, r: 10, l: 50, b: 30 },
        xaxis: { title: 'Time' },
        yaxis: { title: 'Percentage', range: [0, 100] },
        showlegend: false
    };

    // CPU Chart
    Plotly.newPlot('cpuChart', [{
        y: [],
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        line: { color: '#3498db', width: 2 },
        name: 'CPU %'
    }], {
        ...layout,
        title: 'CPU Usage (%)'
    }, { responsive: true });

    // Memory Chart
    Plotly.newPlot('memoryChart', [{
        y: [],
        type: 'scatter',
        mode: 'lines',
        fill: 'tozeroy',
        line: { color: '#2ecc71', width: 2 },
        name: 'Memory %'
    }], {
        ...layout,
        title: 'Memory Usage (%)'
    }, { responsive: true });
}

// Update live charts
function updateLiveCharts(metrics) {
    cpuData.push(metrics.cpu_percent);
    memoryData.push(metrics.memory_percent);
    timestamps.push(new Date());

    // Keep last 60 data points
    if (cpuData.length > 60) {
        cpuData.shift();
        memoryData.shift();
        timestamps.shift();
    }

    // Update CPU chart
    Plotly.update('cpuChart', {
        y: [cpuData],
        x: [timestamps]
    }, {}, [0]);

    // Update Memory chart
    Plotly.update('memoryChart', {
        y: [memoryData],
        x: [timestamps]
    }, {}, [0]);
}

// Add log entry
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('activityLog');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;

    logContainer.insertBefore(logEntry, logContainer.firstChild);

    // Keep only last 50 log entries
    while (logContainer.children.length > 50) {
        logContainer.removeChild(logContainer.lastChild);
    }
}

// Clear logs
function clearLogs() {
    document.getElementById('activityLog').innerHTML = '';
    addLog('Logs cleared', 'info');
}

// Setup event listeners
function setupEventListeners() {
    document.getElementById('startTestBtn').addEventListener('click', startTest);
    document.getElementById('stopTestBtn').addEventListener('click', stopTest);

    // Update scenario details when changed
    document.getElementById('testScenario').addEventListener('change', function() {
        // Could load scenario details and update form
    });
}

// Utility function to format dates
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

// Request system metrics periodically
setInterval(() => {
    if (testRunning) {
        socket.emit('request_system_metrics');
    }
}, 2000);
