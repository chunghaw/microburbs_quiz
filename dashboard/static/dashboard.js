// Microburbs Multi-Period Dashboard JavaScript

let currentPeriod = '9_year';
let allPeriodsData = {};
let comparisonData = [];
let charts = {};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
    setupPeriodButtons();
});

// Setup period selector buttons
function setupPeriodButtons() {
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            currentPeriod = btn.dataset.period;
            
            // Update active state
            document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Reload dashboard for selected period
            loadPeriodData(currentPeriod);
        });
    });
}

// Load all periods data
async function loadAllData() {
    try {
        showLoading();
        
        // Load each period
        const periods = ['1_year', '3_year', '5_year', '9_year'];
        for (const period of periods) {
            const response = await fetch(`/api/data/${period}`);
            const result = await response.json();
            if (result.success) {
                allPeriodsData[period] = result.data;
            }
        }
        
        // Load comparison data
        const compResponse = await fetch('/api/comparison');
        const compResult = await compResponse.json();
        if (compResult.success) {
            comparisonData = compResult.data;
        }
        
        // Load initial period (9-year)
        loadPeriodData('9_year');
        
        hideLoading();
    } catch (error) {
        console.error('Error loading data:', error);
        hideLoading();
    }
}

// Load specific period data
async function loadPeriodData(period) {
    try {
        // Load stats
        const statsResponse = await fetch(`/api/stats/${period}`);
        const statsData = await statsResponse.json();
        
        if (statsData.success) {
            updateStats(statsData.stats);
        }
        
        // Update all charts
        const periodData = allPeriodsData[period] || [];
        updateAllCharts(periodData, period);
        
    } catch (error) {
        console.error('Error loading period data:', error);
    }
}

// Update stats cards
function updateStats(stats) {
    document.getElementById('statSuburbs').textContent = stats.total_suburbs;
    document.getElementById('statScore').textContent = stats.avg_score.toFixed(1);
    document.getElementById('statGrowth').textContent = `${stats.avg_growth > 0 ? '+' : ''}${stats.avg_growth.toFixed(1)}%`;
    document.getElementById('statBuy').textContent = stats.buy_signals;
}

// Update all charts
function updateAllCharts(data, period) {
    createSignalDistChart(data);
    createGrowthChart(data);
    createYieldChart(data);
    createTransactionsChart(data);
    createScoresAcrossPeriodsChart();
    createHeatmap();
    createRankingTable(data);
}

// 1. Signal Distribution (Pie Chart)
function createSignalDistChart(data) {
    const ctx = document.getElementById('signalDistChart');
    
    if (charts.signalDist) charts.signalDist.destroy();
    
    const signalCounts = {
        'BUY': data.filter(d => d.total_score >= 60).length,
        'HOLD': data.filter(d => d.total_score >= 45 && d.total_score < 60).length,
        'CAUTION': data.filter(d => d.total_score < 45).length
    };
    
    charts.signalDist = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(signalCounts),
            datasets: [{
                data: Object.values(signalCounts),
                backgroundColor: ['#f39c12', '#3498db', '#e67e22'],
                borderColor: '#1e1e1e',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { labels: { color: '#cccccc', font: { size: 12 } } },
                tooltip: { enabled: true }
            }
        }
    });
}

// 2. Growth Chart (Bar)
function createGrowthChart(data) {
    const ctx = document.getElementById('growthChart');
    
    if (charts.growth) charts.growth.destroy();
    
    const sorted = [...data].sort((a, b) => b.price_growth_pct - a.price_growth_pct).slice(0, 10);
    
    charts.growth = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(d => d.suburb),
            datasets: [{
                label: 'Price Growth (%)',
                data: sorted.map(d => d.price_growth_pct),
                backgroundColor: sorted.map(d => d.price_growth_pct > 0 ? '#2ecc71' : '#e74c3c'),
                borderColor: '#1e1e1e',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { enabled: true }
            },
            scales: {
                x: { ticks: { color: '#cccccc' }, grid: { color: '#3e3e42' } },
                y: { ticks: { color: '#cccccc', font: { weight: 'bold' } }, grid: { display: false } }
            }
        }
    });
}

// 3. Yield Chart
function createYieldChart(data) {
    const ctx = document.getElementById('yieldChart');
    
    if (charts.yield) charts.yield.destroy();
    
    const sorted = [...data].sort((a, b) => b.estimated_yield_pct - a.estimated_yield_pct).slice(0, 10);
    
    charts.yield = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(d => d.suburb),
            datasets: [{
                label: 'Rental Yield (%)',
                data: sorted.map(d => d.estimated_yield_pct),
                backgroundColor: '#2ecc71',
                borderColor: '#1e1e1e',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#cccccc' }, grid: { color: '#3e3e42' } },
                y: { ticks: { color: '#cccccc', font: { weight: 'bold' } }, grid: { display: false } }
            }
        }
    });
}

// 4. Transactions Chart
function createTransactionsChart(data) {
    const ctx = document.getElementById('transactionsChart');
    
    if (charts.transactions) charts.transactions.destroy();
    
    const sorted = [...data].sort((a, b) => b.period_transactions - a.period_transactions).slice(0, 10);
    
    charts.transactions = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(d => d.suburb),
            datasets: [{
                label: 'Transactions',
                data: sorted.map(d => d.period_transactions),
                backgroundColor: '#9b59b6',
                borderColor: '#1e1e1e',
                borderWidth: 2
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#cccccc' }, grid: { color: '#3e3e42' } },
                y: { ticks: { color: '#cccccc', font: { weight: 'bold' } }, grid: { display: false } }
            }
        }
    });
}

// 5. Scores Across Periods
function createScoresAcrossPeriodsChart() {
    const ctx = document.getElementById('scoresAcrossPeriodsChart');
    
    if (charts.scoresAcross) charts.scoresAcross.destroy();
    
    // Get top 8 suburbs from 9-year data
    const top9Year = allPeriodsData['9_year'] || [];
    const topSuburbs = top9Year.slice(0, 8).map(d => d.suburb);
    
    const datasets = [
        {
            label: '1-Year',
            data: topSuburbs.map(s => getScoreForSuburb(s, '1_year')),
            backgroundColor: 'rgba(231, 76, 60, 0.7)',
            borderColor: '#e74c3c',
            borderWidth: 2
        },
        {
            label: '3-Year',
            data: topSuburbs.map(s => getScoreForSuburb(s, '3_year')),
            backgroundColor: 'rgba(243, 156, 18, 0.7)',
            borderColor: '#f39c12',
            borderWidth: 2
        },
        {
            label: '5-Year',
            data: topSuburbs.map(s => getScoreForSuburb(s, '5_year')),
            backgroundColor: 'rgba(52, 152, 219, 0.7)',
            borderColor: '#3498db',
            borderWidth: 2
        },
        {
            label: '9-Year',
            data: topSuburbs.map(s => getScoreForSuburb(s, '9_year')),
            backgroundColor: 'rgba(46, 204, 113, 0.7)',
            borderColor: '#2ecc71',
            borderWidth: 2
        }
    ];
    
    charts.scoresAcross = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: topSuburbs,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: '#cccccc', font: { size: 12 } } }
            },
            scales: {
                x: { ticks: { color: '#cccccc', font: { weight: 'bold' } }, grid: { display: false } },
                y: { ticks: { color: '#cccccc' }, grid: { color: '#3e3e42' }, max: 100 }
            }
        }
    });
}

function getScoreForSuburb(suburb, period) {
    const periodData = allPeriodsData[period] || [];
    const suburbData = periodData.find(d => d.suburb === suburb);
    return suburbData ? suburbData.total_score : 0;
}

// 6. Heatmap
function createHeatmap() {
    const container = document.getElementById('heatmapContainer');
    
    const top9Year = allPeriodsData['9_year'] || [];
    const topSuburbs = top9Year.slice(0, 10).map(d => d.suburb);
    const periods = ['1-Year', '3-Year', '5-Year', '9-Year'];
    const periodIds = ['1_year', '3_year', '5_year', '9_year'];
    
    let html = '<table class="heatmap-table"><thead><tr><th>Suburb</th>';
    periods.forEach(p => html += `<th>${p}</th>`);
    html += '</tr></thead><tbody>';
    
    topSuburbs.forEach(suburb => {
        html += `<tr><td style="font-weight: 700;">${suburb}</td>`;
        periodIds.forEach(periodId => {
            const score = getScoreForSuburb(suburb, periodId);
            const scoreClass = score > 75 ? 'excellent' : score >= 60 ? 'buy' : 
                              score >= 45 ? 'hold' : score >= 30 ? 'caution' : 'avoid';
            html += `<td class="heatmap-cell ${scoreClass}">${score.toFixed(0)}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// 7. Ranking Table
function createRankingTable(data) {
    const container = document.getElementById('rankingTable');
    
    const sorted = [...data].sort((a, b) => b.total_score - a.total_score);
    
    let html = `
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Suburb</th>
                    <th>Score</th>
                    <th>Growth</th>
                    <th>Price</th>
                    <th>Yield</th>
                    <th>Transactions</th>
                    <th>Reliability</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    sorted.forEach((suburb, index) => {
        const growthDisplay = suburb.price_growth_pct === 0 ? 'N/A' : 
                            `${suburb.price_growth_pct > 0 ? '+' : ''}${suburb.price_growth_pct.toFixed(1)}%`;
        const growthColor = suburb.price_growth_pct > 0 ? 'color: #2ecc71' : 
                           suburb.price_growth_pct < 0 ? 'color: #e74c3c' : '';
        
        html += `
            <tr>
                <td style="font-weight: 700;">${index + 1}</td>
                <td style="font-weight: 700; color: var(--text-accent);">${suburb.suburb}</td>
                <td style="font-weight: 700; color: ${getScoreColor(suburb.total_score)};">${suburb.total_score.toFixed(1)}</td>
                <td style="${growthColor}; font-weight: 700;">${growthDisplay}</td>
                <td>$${(suburb.period_median_price / 1e6).toFixed(2)}M</td>
                <td>${suburb.estimated_yield_pct.toFixed(1)}%</td>
                <td>${suburb.period_transactions}</td>
                <td>${suburb.reliability}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function getScoreColor(score) {
    if (score > 75) return '#27ae60';
    if (score >= 60) return '#f39c12';
    if (score >= 45) return '#3498db';
    if (score >= 30) return '#e67e22';
    return '#e74c3c';
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.add('hidden');
}

