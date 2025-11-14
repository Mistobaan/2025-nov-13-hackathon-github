// Chart instances
let latencyChart = null;
let costChart = null;
let qualityChart = null;

// Chronometer
let chronometerInterval = null;
let chronometerStartTime = null;

// Fetch and populate models on page load
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        const checkboxesContainer = document.getElementById('modelCheckboxes');
        checkboxesContainer.innerHTML = '';
        
        data.models.forEach(model => {
            const label = document.createElement('label');
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.value = model.id;
            checkbox.id = `model-${model.id}`;
            
            label.appendChild(checkbox);
            label.appendChild(document.createTextNode(model.label));
            label.setAttribute('for', `model-${model.id}`);
            
            checkboxesContainer.appendChild(label);
        });
    } catch (error) {
        console.error('Failed to load models:', error);
        document.getElementById('statusText').textContent = 'Failed to load models';
    }
}

// Start chronometer
function startChronometer() {
    chronometerStartTime = Date.now();
    const chronometerEl = document.getElementById('chronometer');
    const timeEl = document.getElementById('chronometerTime');
    chronometerEl.style.display = 'block';
    
    chronometerInterval = setInterval(() => {
        const elapsed = (Date.now() - chronometerStartTime) / 1000;
        timeEl.textContent = elapsed.toFixed(2) + 's';
    }, 10);
}

// Stop chronometer
function stopChronometer() {
    if (chronometerInterval) {
        clearInterval(chronometerInterval);
        chronometerInterval = null;
    }
}

// Format latency
function formatLatency(ms) {
    if (ms < 1000) {
        return ms.toFixed(0) + 'ms';
    }
    return (ms / 1000).toFixed(2) + 's';
}

// Format cost
function formatCost(usd) {
    if (usd < 0.001) {
        return '$' + (usd * 1000).toFixed(3) + 'm';
    }
    return '$' + usd.toFixed(6);
}

// Format quality score
function formatQuality(score) {
    if (score === null || score === undefined) return 'N/A';
    return score.toFixed(1) + '/10';
}

// Render charts
function renderCharts(results) {
    const successfulResults = results.filter(r => !r.error);
    
    if (successfulResults.length === 0) return;
    
    const labels = successfulResults.map(r => r.label);
    const latencyData = successfulResults.map(r => r.latency_ms);
    const costData = successfulResults.map(r => r.estimated_cost_usd);
    const qualityData = successfulResults.map(r => r.quality_score || 0);
    
    // Revolut-inspired blue shades for charts
    const blueShades = [
        '#007AFF',  // Primary blue
        '#0051D5',  // Darker blue
        '#5AC8FA',  // Light blue
        '#0071E3',  // Medium blue
        '#00A8FF',  // Bright blue
        '#004DE6',  // Deep blue
        '#34AADC',  // Sky blue
        '#0066CC',  // Classic blue
        '#0084FF',  // Vibrant blue
        '#003D99',  // Navy blue
    ];
    
    const chartColors = successfulResults.map((r, i) => {
        return blueShades[i % blueShades.length];
    });
    
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                padding: 12,
                titleFont: {
                    size: 14,
                    weight: '600'
                },
                bodyFont: {
                    size: 13
                },
                cornerRadius: 8,
                displayColors: true
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#86868B'
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 12
                    },
                    color: '#86868B',
                    maxRotation: 45,
                    minRotation: 45
                }
            }
        },
        animation: {
            duration: 1000,
            easing: 'easeOutQuart'
        }
    };
    
    // Latency Chart
    const latencyCtx = document.getElementById('latencyChart').getContext('2d');
    if (latencyChart) latencyChart.destroy();
    latencyChart = new Chart(latencyCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Latency (ms)',
                data: latencyData,
                backgroundColor: chartColors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                tooltip: {
                    ...chartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return 'Latency: ' + formatLatency(context.parsed.y);
                        }
                    }
                }
            }
        }
    });
    
    // Cost Chart
    const costCtx = document.getElementById('costChart').getContext('2d');
    if (costChart) costChart.destroy();
    costChart = new Chart(costCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Cost (USD)',
                data: costData,
                backgroundColor: chartColors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...chartOptions,
            plugins: {
                ...chartOptions.plugins,
                tooltip: {
                    ...chartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return 'Cost: ' + formatCost(context.parsed.y);
                        }
                    }
                }
            }
        }
    });
    
    // Quality Chart
    const qualityCtx = document.getElementById('qualityChart').getContext('2d');
    if (qualityChart) qualityChart.destroy();
    qualityChart = new Chart(qualityCtx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Quality Score',
                data: qualityData,
                backgroundColor: chartColors,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            ...chartOptions,
            scales: {
                ...chartOptions.scales,
                y: {
                    ...chartOptions.scales.y,
                    max: 10,
                    ticks: {
                        ...chartOptions.scales.y.ticks,
                        stepSize: 1
                    }
                }
            },
            plugins: {
                ...chartOptions.plugins,
                tooltip: {
                    ...chartOptions.plugins.tooltip,
                    callbacks: {
                        label: function(context) {
                            return 'Quality: ' + formatQuality(context.parsed.y);
                        }
                    }
                }
            }
        }
    });
}

// Handle benchmark button click
async function runBenchmark() {
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput.value.trim();
    
    // Get selected model IDs
    const checkboxes = document.querySelectorAll('#modelCheckboxes input[type="checkbox"]:checked');
    const modelIds = Array.from(checkboxes).map(cb => cb.value);
    
    // Validate input
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }
    
    if (modelIds.length === 0) {
        alert('Please select at least one model');
        return;
    }
    
    // Update UI
    const runButton = document.getElementById('runButton');
    const buttonText = document.getElementById('buttonText');
    const statusText = document.getElementById('statusText');
    runButton.disabled = true;
    buttonText.textContent = 'Running...';
    statusText.textContent = 'Benchmark in progress...';
    
    // Clear previous results
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('resultsTableBody').innerHTML = '';
    document.getElementById('responseTexts').innerHTML = '';
    document.getElementById('winnerInfo').innerHTML = '';
    
    // Destroy previous charts
    if (latencyChart) {
        latencyChart.destroy();
        latencyChart = null;
    }
    if (costChart) {
        costChart.destroy();
        costChart = null;
    }
    if (qualityChart) {
        qualityChart.destroy();
        qualityChart = null;
    }
    
    // Start chronometer
    startChronometer();
    
    try {
        const response = await fetch('/api/benchmark', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                prompt: prompt,
                model_ids: modelIds,
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Benchmark failed');
        }
        
        const data = await response.json();
        
        // Stop chronometer
        stopChronometer();
        
        // Display winner info
        if (data.winner) {
            const winnerResult = data.results.find(r => r.model_id === data.winner);
            const winnerInfo = document.getElementById('winnerInfo');
            winnerInfo.innerHTML = `
                <h2>🏆 Winner: ${winnerResult.label}</h2>
                <p>${data.winner_reason || ''}</p>
            `;
        }
        
        // Build results table
        const tableBody = document.getElementById('resultsTableBody');
        data.results.forEach(result => {
            const row = document.createElement('tr');
            if (result.model_id === data.winner) {
                row.classList.add('winner-row');
            }
            
            const winnerCell = result.model_id === data.winner ? '🏆' : '';
            
            row.innerHTML = `
                <td><strong>${result.label}</strong></td>
                <td>${result.provider}</td>
                <td>${result.error ? 'N/A' : formatLatency(result.latency_ms)}</td>
                <td>${result.error ? 'N/A' : formatCost(result.estimated_cost_usd)}</td>
                <td>${result.error ? 'N/A' : result.tokens_estimate.toLocaleString()}</td>
                <td>${result.error ? 'N/A' : formatQuality(result.quality_score)}</td>
                <td>${winnerCell}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Render charts
        renderCharts(data.results);
        
        // Display response texts
        const responseTexts = document.getElementById('responseTexts');
        data.results.forEach(result => {
            const details = document.createElement('details');
            const summary = document.createElement('summary');
            summary.textContent = `${result.label} - Response`;
            const pre = document.createElement('pre');
            
            if (result.error) {
                pre.textContent = `Error: ${result.error}`;
                pre.style.color = '#FF3B30';
            } else {
                pre.textContent = result.text;
            }
            
            details.appendChild(summary);
            details.appendChild(pre);
            responseTexts.appendChild(details);
        });
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        statusText.textContent = 'Benchmark completed successfully';
        buttonText.textContent = 'Run Benchmark';
        
        // Scroll to results
        document.getElementById('resultsSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
        
    } catch (error) {
        console.error('Benchmark error:', error);
        stopChronometer();
        statusText.textContent = `Error: ${error.message}`;
        buttonText.textContent = 'Run Benchmark';
    } finally {
        runButton.disabled = false;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    document.getElementById('runButton').addEventListener('click', runBenchmark);
});
