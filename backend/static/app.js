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
    const statusText = document.getElementById('statusText');
    runButton.disabled = true;
    statusText.textContent = 'Running...';
    
    // Clear previous results
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('resultsTableBody').innerHTML = '';
    document.getElementById('responseTexts').innerHTML = '';
    document.getElementById('winnerInfo').innerHTML = '';
    
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
        
        // Display winner info
        if (data.winner) {
            const winnerInfo = document.getElementById('winnerInfo');
            winnerInfo.innerHTML = `
                <h2>Winner: ${data.results.find(r => r.model_id === data.winner).label}</h2>
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
            
            const winnerCell = result.model_id === data.winner ? '✓' : '';
            
            row.innerHTML = `
                <td>${result.label}</td>
                <td>${result.provider}</td>
                <td>${result.error ? 'N/A' : result.latency_ms.toFixed(2)}</td>
                <td>${result.error ? 'N/A' : result.estimated_cost_usd.toFixed(6)}</td>
                <td>${result.error ? 'N/A' : result.tokens_estimate}</td>
                <td>${winnerCell}</td>
            `;
            
            tableBody.appendChild(row);
        });
        
        // Display response texts
        const responseTexts = document.getElementById('responseTexts');
        data.results.forEach(result => {
            const details = document.createElement('details');
            const summary = document.createElement('summary');
            summary.textContent = `${result.label} - Response`;
            const pre = document.createElement('pre');
            
            if (result.error) {
                pre.textContent = `Error: ${result.error}`;
                pre.style.color = '#dc3545';
            } else {
                pre.textContent = result.text;
            }
            
            details.appendChild(summary);
            details.appendChild(pre);
            responseTexts.appendChild(details);
        });
        
        // Show results section
        document.getElementById('resultsSection').style.display = 'block';
        statusText.textContent = 'Done';
        
    } catch (error) {
        console.error('Benchmark error:', error);
        statusText.textContent = `Error: ${error.message}`;
    } finally {
        runButton.disabled = false;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadModels();
    document.getElementById('runButton').addEventListener('click', runBenchmark);
});

