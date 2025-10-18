// Microburbs Investment Dashboard - Interactive JavaScript

let allSuburbs = [];
let filteredSuburbs = [];

// Initialize dashboard
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    loadFilters();
    loadSuburbs();
    
    // Event listeners
    document.getElementById('stateFilter').addEventListener('change', applyFilters);
    document.getElementById('scoreFilter').addEventListener('change', applyFilters);
    document.getElementById('priceFilter').addEventListener('change', applyFilters);
    document.getElementById('reliabilityFilter').addEventListener('change', applyFilters);
    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
});

// Load dashboard statistics
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            document.querySelector('#headerStats').innerHTML = `
                <div class="stat-card">
                    <span class="stat-value">${stats.total_suburbs}</span>
                    <span class="stat-label">Suburbs</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${stats.avg_score.toFixed(1)}</span>
                    <span class="stat-label">Avg Score</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">${stats.buy_signals}</span>
                    <span class="stat-label">BUY Signals</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value">$${(stats.avg_price/1e6).toFixed(2)}M</span>
                    <span class="stat-label">Avg Price</span>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Load filter options
async function loadFilters() {
    try {
        const response = await fetch('/api/filters');
        const data = await response.json();
        
        if (data.success) {
            const filters = data.filters;
            
            // Populate state filter
            const stateFilter = document.getElementById('stateFilter');
            filters.states.forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                stateFilter.appendChild(option);
            });
            
            // Populate score filter
            const scoreFilter = document.getElementById('scoreFilter');
            filters.score_ranges.forEach(range => {
                const option = document.createElement('option');
                option.value = JSON.stringify(range);
                option.textContent = range.label;
                scoreFilter.appendChild(option);
            });
            
            // Populate price filter
            const priceFilter = document.getElementById('priceFilter');
            filters.price_ranges.forEach(range => {
                const option = document.createElement('option');
                option.value = JSON.stringify(range);
                option.textContent = range.label;
                priceFilter.appendChild(option);
            });
            
            // Populate reliability filter
            const reliabilityFilter = document.getElementById('reliabilityFilter');
            filters.reliability.forEach(rel => {
                const option = document.createElement('option');
                option.value = rel;
                option.textContent = rel;
                reliabilityFilter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Error loading filters:', error);
    }
}

// Load suburbs data
async function loadSuburbs() {
    try {
        document.getElementById('loading').style.display = 'block';
        document.getElementById('suburbsGrid').style.display = 'none';
        
        const response = await fetch('/api/suburbs');
        const data = await response.json();
        
        if (data.success) {
            allSuburbs = data.data;
            filteredSuburbs = [...allSuburbs];
            renderSuburbs();
        }
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('suburbsGrid').style.display = 'grid';
    } catch (error) {
        console.error('Error loading suburbs:', error);
        document.getElementById('loading').innerHTML = '<p>Error loading data. Please refresh the page.</p>';
    }
}

// Render suburbs grid
function renderSuburbs() {
    const grid = document.getElementById('suburbsGrid');
    const noResults = document.getElementById('noResults');
    
    if (filteredSuburbs.length === 0) {
        grid.style.display = 'none';
        noResults.style.display = 'block';
        return;
    }
    
    grid.style.display = 'grid';
    noResults.style.display = 'none';
    
    grid.innerHTML = filteredSuburbs.map(suburb => createSuburbCard(suburb)).join('');
    
    // Add click handlers
    document.querySelectorAll('.suburb-card').forEach(card => {
        card.addEventListener('click', () => {
            const suburbName = card.dataset.suburb;
            showSuburbDetail(suburbName);
        });
    });
}

// Create suburb card HTML
function createSuburbCard(suburb) {
    // Safe access to properties with defaults
    const totalScore = suburb.total_score || 0;
    const scoreClass = getScoreClass(totalScore);
    const priceGrowth = suburb.price_growth_pct || 0;
    const growthClass = priceGrowth > 0 ? 'positive' : priceGrowth < 0 ? 'negative' : 'neutral';
    const reliability = suburb.reliability || 'N/A';
    const reliabilityClass = reliability.toLowerCase();
    const hasScore = suburb.has_investment_score || false;
    
    const growthDisplay = priceGrowth === 0 ? 'N/A' : 
                         `${priceGrowth > 0 ? '+' : ''}${priceGrowth.toFixed(1)}%`;
    
    const scoreDisplay = hasScore ? totalScore.toFixed(1) : 'N/A';
    const actionDisplay = suburb.action || (hasScore ? 'N/A' : 'API Data Only');
    const medianPrice = suburb.recent_median_price || 0;
    const yieldPct = suburb.estimated_yield_pct || 0;
    const recentTrans = suburb.recent_transactions || 0;
    
    return `
        <div class="suburb-card" data-suburb="${suburb.suburb}">
            ${reliability !== 'N/A' ? `<div class="reliability-badge ${reliabilityClass}">${reliability}</div>` : ''}
            <div class="suburb-card-header">
                <div>
                    <h3 class="suburb-name">${suburb.suburb}</h3>
                    <p class="suburb-location">${suburb.state || 'NSW'} ${suburb.postcode || ''}</p>
                </div>
                <div class="score-badge ${scoreClass}">
                    <span class="score-number">${scoreDisplay}</span>
                    <span class="score-label">${hasScore ? 'SCORE' : 'API'}</span>
                </div>
            </div>
            
            <div class="action-tag ${scoreClass}">${actionDisplay}</div>
            
            <div class="suburb-metrics">
                <div class="metric">
                    <span class="metric-label">12M Growth</span>
                    <span class="metric-value ${growthClass}">${growthDisplay}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Median Price</span>
                    <span class="metric-value">${medianPrice > 0 ? '$' + (medianPrice/1e6).toFixed(2) + 'M' : 'N/A'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Rental Yield</span>
                    <span class="metric-value">${yieldPct > 0 ? yieldPct.toFixed(1) + '%' : 'N/A'}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Transactions</span>
                    <span class="metric-value">${recentTrans > 0 ? recentTrans + ' sales' : 'See API'}</span>
                </div>
            </div>
        </div>
    `;
}

// Get score class for styling
function getScoreClass(score) {
    if (score > 75) return 'excellent';
    if (score >= 60) return 'buy';
    if (score >= 45) return 'hold';
    if (score >= 30) return 'caution';
    return 'avoid';
}

// Apply filters
function applyFilters() {
    const stateValue = document.getElementById('stateFilter').value;
    const scoreValue = document.getElementById('scoreFilter').value;
    const priceValue = document.getElementById('priceFilter').value;
    const reliabilityValue = document.getElementById('reliabilityFilter').value;
    const searchValue = document.getElementById('searchInput').value.toLowerCase();
    
    filteredSuburbs = allSuburbs.filter(suburb => {
        // State filter
        if (stateValue && suburb.state !== stateValue) return false;
        
        // Score range filter
        if (scoreValue) {
            const range = JSON.parse(scoreValue);
            if (suburb.total_score < range.min || suburb.total_score > range.max) return false;
        }
        
        // Price range filter
        if (priceValue) {
            const range = JSON.parse(priceValue);
            if (suburb.recent_median_price < range.min || suburb.recent_median_price > range.max) return false;
        }
        
        // Reliability filter
        if (reliabilityValue && suburb.reliability !== reliabilityValue) return false;
        
        // Search filter
        if (searchValue && !suburb.suburb.toLowerCase().includes(searchValue)) return false;
        
        return true;
    });
    
    renderSuburbs();
}

// Reset filters
function resetFilters() {
    document.getElementById('stateFilter').value = '';
    document.getElementById('scoreFilter').value = '';
    document.getElementById('priceFilter').value = '';
    document.getElementById('reliabilityFilter').value = '';
    document.getElementById('searchInput').value = '';
    
    filteredSuburbs = [...allSuburbs];
    renderSuburbs();
}

// Show suburb detail modal
async function showSuburbDetail(suburbName) {
    const modal = document.getElementById('suburbModal');
    const content = document.getElementById('modalContent');
    
    content.innerHTML = '<div class="loading"><div class="spinner"></div><p>Loading details...</p></div>';
    modal.classList.add('active');
    
    try {
        const response = await fetch(`/api/suburb/${suburbName}`);
        const data = await response.json();
        
        if (data.success) {
            const suburb = data.data;
            content.innerHTML = createDetailContent(suburb);
        } else {
            content.innerHTML = '<p>Error loading suburb details</p>';
        }
    } catch (error) {
        console.error('Error loading suburb detail:', error);
        content.innerHTML = '<p>Error loading suburb details</p>';
    }
}

// Create detail modal content
function createDetailContent(suburb) {
    const scoreClass = getScoreClass(suburb.total_score);
    const growthDisplay = suburb.price_growth_pct === 0 ? 'N/A (insufficient data)' : 
                         `${suburb.price_growth_pct > 0 ? '+' : ''}${suburb.price_growth_pct.toFixed(1)}%`;
    
    return `
        <h2 style="color: var(--text-accent); margin-bottom: var(--spacing-lg);">
            ${suburb.suburb}
        </h2>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-lg); margin-bottom: var(--spacing-xl);">
            <div>
                <div style="font-size: 48px; font-weight: 700; color: var(--score-${scoreClass});">
                    ${suburb.total_score.toFixed(1)}
                </div>
                <div style="font-size: 14px; color: var(--text-secondary);">Investment Score</div>
                <div class="action-tag ${scoreClass}" style="margin-top: var(--spacing-md);">
                    ${suburb.action}
                </div>
            </div>
            <div style="background: var(--bg-elevated); padding: var(--spacing-md); border-radius: var(--radius-md);">
                <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: var(--spacing-xs);">MEDIAN PRICE</div>
                <div style="font-size: 24px; font-weight: 700; color: var(--text-accent);">$${(suburb.recent_median_price/1e6).toFixed(2)}M</div>
                <div style="font-size: 12px; color: var(--text-secondary); margin-top: var(--spacing-md);">EST. MONTHLY RENT</div>
                <div style="font-size: 18px; font-weight: 600; color: var(--accent-green);">$${suburb.estimated_monthly_rent.toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",")}</div>
            </div>
        </div>
        
        <h3 style="color: var(--text-accent); margin-bottom: var(--spacing-md);">Score Breakdown</h3>
        <div style="margin-bottom: var(--spacing-xl);">
            ${createComponentBar('Price Growth', suburb.price_growth_score, 35, '#e74c3c')}
            ${createComponentBar('Affordability', suburb.affordability_score, 15, '#3498db')}
            ${createComponentBar('Rental Yield', suburb.yield_score, 25, '#2ecc71')}
            ${createComponentBar('Accessibility', suburb.accessibility_score, 15, '#9b59b6')}
            ${createComponentBar('Market Liquidity', suburb.liquidity_score, 10, '#f39c12')}
        </div>
        
        <h3 style="color: var(--text-accent); margin-bottom: var(--spacing-md);">Key Metrics</h3>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: var(--spacing-md); margin-bottom: var(--spacing-xl);">
            <div class="metric">
                <span class="metric-label">12-Month Growth</span>
                <span class="metric-value ${suburb.price_growth_pct > 0 ? 'positive' : suburb.price_growth_pct < 0 ? 'negative' : 'neutral'}">${growthDisplay}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Rental Yield</span>
                <span class="metric-value">${suburb.estimated_yield_pct.toFixed(1)}% p.a.</span>
            </div>
            <div class="metric">
                <span class="metric-label">Recent Transactions</span>
                <span class="metric-value">${suburb.recent_transactions} sales</span>
            </div>
            <div class="metric">
                <span class="metric-label">Data Reliability</span>
                <span class="metric-value">${suburb.reliability}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Activity Change</span>
                <span class="metric-value ${suburb.activity_change_pct > 0 ? 'positive' : 'negative'}">${suburb.activity_change_pct > 0 ? '+' : ''}${suburb.activity_change_pct.toFixed(1)}%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Distance to Major Road</span>
                <span class="metric-value">${suburb.avg_distance_to_major_road_m ? Math.round(suburb.avg_distance_to_major_road_m) + 'm' : 'N/A'}</span>
            </div>
        </div>
        
        <div style="background: var(--bg-elevated); padding: var(--spacing-md); border-radius: var(--radius-md); border-left: 4px solid var(--accent-blue);">
            <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: var(--spacing-sm);">INVESTMENT SIGNAL</div>
            <div style="font-size: 14px; color: var(--text-primary); line-height: 1.6;">
                ${suburb.investment_signal}
            </div>
        </div>
    `;
}

// Create component progress bar
function createComponentBar(label, value, max, color) {
    const percentage = (value / max) * 100;
    return `
        <div style="margin-bottom: var(--spacing-md);">
            <div style="display: flex; justify-content: space-between; margin-bottom: var(--spacing-xs);">
                <span style="font-size: 12px; color: var(--text-secondary);">${label}</span>
                <span style="font-size: 12px; font-weight: 700; color: var(--text-accent);">${value.toFixed(1)}/${max}</span>
            </div>
            <div style="background: var(--bg-elevated); height: 8px; border-radius: 4px; overflow: hidden;">
                <div style="height: 100%; width: ${percentage}%; background: ${color}; transition: width 0.3s ease;"></div>
            </div>
        </div>
    `;
}

// Close modal
function closeModal() {
    document.getElementById('suburbModal').classList.remove('active');
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

