// DOM Elements
const urlInput = document.getElementById('url-input');
const analyzeBtn = document.getElementById('analyze-btn');
const loadingDiv = document.getElementById('loading');
const resultsContainer = document.getElementById('results-container');
const batchAnalyzeBtn = document.getElementById('batch-analyze-btn');
const batchLoading = document.getElementById('batch-loading');
const batchResultsContainer = document.getElementById('batch-results-container');
const compareBtn = document.getElementById('compare-btn');
const compareLoading = document.getElementById('compare-loading');
const compareResultsContainer = document.getElementById('compare-results-container');

// Tab switching
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        const tab = link.dataset.tab;
        
        // Update active states
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
        
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        
        document.getElementById(`${tab}-tab`).classList.add('active');
    });
});

// Single URL Analysis
if (analyzeBtn) {
    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        
        if (!url) {
            showError('Please enter a URL');
            return;
        }
        
        // Show loading
        loadingDiv.style.display = 'block';
        resultsContainer.style.display = 'none';
        
        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `url=${encodeURIComponent(url)}`
            });
            
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
            } else {
                displayResults(data);
                // Store for report generation
                localStorage.setItem('analysisResults', JSON.stringify(data));
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Error:', error);
        } finally {
            loadingDiv.style.display = 'none';
        }
    });
}

// Batch Analysis
if (batchAnalyzeBtn) {
    batchAnalyzeBtn.addEventListener('click', async () => {
        const urlsText = document.getElementById('urls-input').value;
        const urls = urlsText.split('\n').filter(url => url.trim());
        
        if (urls.length === 0 || urls.length > 10) {
            showError('Please enter 1-10 URLs (one per line)');
            return;
        }
        
        batchLoading.style.display = 'block';
        batchResultsContainer.style.display = 'none';
        
        try {
            const response = await fetch('/api/batch-analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls: urls })
            });
            
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
            } else {
                displayBatchResults(data);
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Error:', error);
        } finally {
            batchLoading.style.display = 'none';
        }
    });
}

// Compare Websites
if (compareBtn) {
    compareBtn.addEventListener('click', async () => {
        const urlsText = document.getElementById('compare-urls').value;
        const urls = urlsText.split('\n').filter(url => url.trim());
        
        if (urls.length < 2 || urls.length > 5) {
            showError('Please enter 2-5 URLs for comparison');
            return;
        }
        
        compareLoading.style.display = 'block';
        compareResultsContainer.style.display = 'none';
        
        try {
            const response = await fetch('/api/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ urls: urls })
            });
            
            const data = await response.json();
            
            if (data.error) {
                showError(data.error);
            } else {
                displayComparisonResults(data);
            }
        } catch (error) {
            showError('Network error. Please try again.');
            console.error('Error:', error);
        } finally {
            compareLoading.style.display = 'none';
        }
    });
}

// Display performance graphs
function displayPerformanceGraphs(graphs) {
    if (!graphs) return '';
    
    let html = `
        <div class="graphs-section">
            <div class="section-header">
                <h2><i class="fas fa-chart-line"></i> Performance Graphs & Visualizations</h2>
                <div class="graph-controls">
                    <button class="btn-graph-view active" data-view="all">All Graphs</button>
                    <button class="btn-graph-view" data-view="core">Core Vitals</button>
                    <button class="btn-graph-view" data-view="resources">Resources</button>
                    <button class="btn-graph-view" data-view="comparison">Comparison</button>
                </div>
            </div>
            <div class="graphs-grid">
    `;
    
    // Core Web Vitals Bar Chart
    if (graphs.core_vitals_bar) {
        html += `
            <div class="graph-card" data-category="core">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-bar"></i> Core Web Vitals Analysis</h3>
                    <span class="graph-badge">Core Metrics</span>
                </div>
                <img src="${graphs.core_vitals_bar}" alt="Core Web Vitals Chart" class="graph-image">
                <div class="graph-footer">
                    <p>Comparison of LCP, FID, CLS, TTFB, and FCP against industry standards</p>
                    <div class="graph-stats">
                        <span class="stat"><i class="fas fa-check-circle"></i> Green = Good</span>
                        <span class="stat"><i class="fas fa-exclamation-triangle"></i> Yellow = Needs Improvement</span>
                        <span class="stat"><i class="fas fa-times-circle"></i> Red = Poor</span>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Score Gauge
    if (graphs.score_gauge) {
        html += `
            <div class="graph-card" data-category="core">
                <div class="graph-header">
                    <h3><i class="fas fa-tachometer-alt"></i> Overall Performance Score</h3>
                    <span class="graph-badge">Score</span>
                </div>
                <img src="${graphs.score_gauge}" alt="Performance Score Gauge" class="graph-image">
                <div class="graph-footer">
                    <p>Your website's overall performance score out of 100</p>
                    <div class="score-scale">
                        <div class="scale-bar">
                            <span class="scale-label">0</span>
                            <span class="scale-label">50</span>
                            <span class="scale-label">100</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    // Resource Distribution
    if (graphs.resource_pie) {
        html += `
            <div class="graph-card" data-category="resources">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-pie"></i> Resource Distribution</h3>
                    <span class="graph-badge">Resources</span>
                </div>
                <img src="${graphs.resource_pie}" alt="Resource Distribution" class="graph-image">
                <div class="graph-footer">
                    <p>Distribution of different resource types on your page</p>
                </div>
            </div>
        `;
    }
    
    // Resource Horizontal Chart
    if (graphs.resource_horizontal) {
        html += `
            <div class="graph-card" data-category="resources">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-simple"></i> Resource Size Breakdown</h3>
                    <span class="graph-badge">Sizes</span>
                </div>
                <img src="${graphs.resource_horizontal}" alt="Resource Sizes" class="graph-image">
                <div class="graph-footer">
                    <p>Estimated size breakdown by resource type</p>
                </div>
            </div>
        `;
    }
    
    // Time Series Chart
    if (graphs.time_series) {
        html += `
            <div class="graph-card" data-category="comparison">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-line"></i> Performance Trends</h3>
                    <span class="graph-badge">Historical</span>
                </div>
                <img src="${graphs.time_series}" alt="Time Series Analysis" class="graph-image">
                <div class="graph-footer">
                    <p>Historical performance trends based on current metrics</p>
                    <div class="insight">
                        <i class="fas fa-lightbulb"></i> Track improvements over time
                    </div>
                </div>
            </div>
        `;
    }
    
    // Radar Chart
    if (graphs.radar_chart) {
        html += `
            <div class="graph-card" data-category="comparison">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-radar"></i> Performance Radar</h3>
                    <span class="graph-badge">Multi-dimensional</span>
                </div>
                <img src="${graphs.radar_chart}" alt="Radar Chart" class="graph-image">
                <div class="graph-footer">
                    <p>Multi-dimensional performance comparison (higher score is better)</p>
                </div>
            </div>
        `;
    }
    
    // Improvement Chart
    if (graphs.improvement) {
        html += `
            <div class="graph-card" data-category="comparison">
                <div class="graph-header">
                    <h3><i class="fas fa-arrow-trend-up"></i> Improvement Opportunities</h3>
                    <span class="graph-badge">Actionable</span>
                </div>
                <img src="${graphs.improvement}" alt="Improvement Chart" class="graph-image">
                <div class="graph-footer">
                    <p>Areas with the biggest potential for improvement</p>
                </div>
            </div>
        `;
    }
    
    // Normalized Comparison
    if (graphs.comparison_normalized) {
        html += `
            <div class="graph-card" data-category="comparison">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-gantt"></i> Normalized Scores</h3>
                    <span class="graph-badge">0-100 Scale</span>
                </div>
                <img src="${graphs.comparison_normalized}" alt="Normalized Comparison" class="graph-image">
                <div class="graph-footer">
                    <p>Normalized performance scores (higher is better)</p>
                </div>
            </div>
        `;
    }
    
    // Metric Breakdown
    if (graphs.metric_breakdown) {
        html += `
            <div class="graph-card" data-category="core">
                <div class="graph-header">
                    <h3><i class="fas fa-chart-simple"></i> Metric Breakdown</h3>
                    <span class="graph-badge">Detailed</span>
                </div>
                <img src="${graphs.metric_breakdown}" alt="Metric Breakdown" class="graph-image">
                <div class="graph-footer">
                    <p>Detailed breakdown of each metric with threshold indicators</p>
                </div>
            </div>
        `;
    }
    
    // Recommendation Priority
    if (graphs.recommendation_priority) {
        html += `
            <div class="graph-card" data-category="comparison">
                <div class="graph-header">
                    <h3><i class="fas fa-list-check"></i> Recommendation Analysis</h3>
                    <span class="graph-badge">Priority</span>
                </div>
                <img src="${graphs.recommendation_priority}" alt="Recommendation Priority" class="graph-image">
                <div class="graph-footer">
                    <p>Distribution of recommendations by priority and category</p>
                </div>
            </div>
        `;
    }
    
    html += `
            </div>
        </div>
    `;
    
    return html;
}

// Display single analysis results
function displayResults(data) {
    const overallScore = data.overall_score;
    const metrics = data.metrics;
    const analysis = data.analysis;
    const recommendations = data.recommendations;
    const graphs = data.graphs;
    
    // Determine score color
    let scoreColor = '#ef4444';
    let scoreCardClass = '';
    if (overallScore >= 80) {
        scoreColor = '#10b981';
        scoreCardClass = 'excellent';
    } else if (overallScore >= 50) {
        scoreColor = '#f59e0b';
        scoreCardClass = 'average';
    } else {
        scoreCardClass = 'poor';
    }
    
    const html = `
        <div class="results-card ${scoreCardClass}">
            <div class="score-header">
                <div class="score-circle" style="border: 4px solid ${scoreColor}">
                    <div class="score-number">${overallScore}</div>
                </div>
                <div class="score-label">Overall Performance Score</div>
                <div class="url-badge">
                    <i class="fas fa-globe"></i> ${data.url}
                </div>
                <div class="timestamp">
                    <i class="far fa-clock"></i> ${new Date(data.timestamp).toLocaleString()}
                </div>
            </div>
            
            <div class="summary-stats">
                <div class="stat-card">
                    <i class="fas fa-tachometer-alt"></i>
                    <span class="stat-value">${metrics.response_time_ms}ms</span>
                    <span class="stat-label">Response Time</span>
                </div>
                <div class="stat-card">
                    <i class="fas fa-weight-hanging"></i>
                    <span class="stat-value">${metrics.page_size_kb}KB</span>
                    <span class="stat-label">Page Size</span>
                </div>
                <div class="stat-card">
                    <i class="fas fa-code"></i>
                    <span class="stat-value">${metrics.resource_counts.total_resources}</span>
                    <span class="stat-label">Total Resources</span>
                </div>
                <div class="stat-card">
                    <i class="fas fa-star"></i>
                    <span class="stat-value">${analysis.overall_rating.toUpperCase()}</span>
                    <span class="stat-label">Rating</span>
                </div>
            </div>
            
            ${displayPerformanceGraphs(graphs)}
            
            <div class="metrics-grid">
                ${renderCoreWebVitals(analysis)}
                ${renderResourceMetrics(metrics)}
                ${renderSEOMetrics(metrics.html_structure)}
            </div>
            
            <div class="recommendations-list">
                <div class="section-header">
                    <h3><i class="fas fa-list-check"></i> Optimization Recommendations</h3>
                    <span class="recommendation-count">${recommendations.length} recommendations</span>
                </div>
                ${renderRecommendations(recommendations)}
            </div>
            
            <div class="action-buttons">
                <button id="download-report-btn" class="btn btn-success">
                    <i class="fas fa-download"></i> Download PDF Report
                </button>
                <button id="share-results-btn" class="btn btn-secondary">
                    <i class="fas fa-share-alt"></i> Share Results
                </button>
            </div>
        </div>
    `;
    
    resultsContainer.innerHTML = html;
    resultsContainer.style.display = 'block';
    
    // Add event listeners for buttons
    document.getElementById('download-report-btn')?.addEventListener('click', () => downloadReport(data));
    document.getElementById('share-results-btn')?.addEventListener('click', () => shareResults(data));
    
    // Add graph view filtering
    setupGraphFilters();
    
    // Scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// Setup graph filter functionality
function setupGraphFilters() {
    const filterButtons = document.querySelectorAll('.btn-graph-view');
    const graphCards = document.querySelectorAll('.graph-card');
    
    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            
            // Update active state
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Filter graphs
            if (view === 'all') {
                graphCards.forEach(card => card.style.display = 'block');
            } else {
                graphCards.forEach(card => {
                    if (card.dataset.category === view) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            }
        });
    });
}

// Render Core Web Vitals
function renderCoreWebVitals(analysis) {
    const vitals = ['lcp', 'fid', 'cls', 'ttfb', 'fcp'];
    const vitalNames = {
        'lcp': 'Largest Contentful Paint',
        'fid': 'First Input Delay',
        'cls': 'Cumulative Layout Shift',
        'ttfb': 'Time to First Byte',
        'fcp': 'First Contentful Paint'
    };
    
    let html = '<div class="metric-card"><div class="metric-header"><i class="fas fa-heartbeat"></i><h3>Core Web Vitals</h3></div><div class="vitals-list">';
    
    for (const vital of vitals) {
        if (analysis[vital]) {
            const metric = analysis[vital];
            const ratingClass = `rating-${metric.rating}`;
            const ratingText = metric.rating.replace('_', ' ').toUpperCase();
            
            let valueText = metric.value;
            let unit = '';
            if (vital === 'lcp' || vital === 'fcp' || vital === 'ttfb') {
                valueText = Math.round(metric.value);
                unit = 'ms';
            } else if (vital === 'cls') {
                valueText = metric.value.toFixed(3);
                unit = '';
            } else if (vital === 'fid') {
                valueText = Math.round(metric.value);
                unit = 'ms';
            }
            
            let icon = 'fa-gauge-high';
            if (metric.rating === 'good') icon = 'fa-circle-check';
            else if (metric.rating === 'poor') icon = 'fa-circle-exclamation';
            
            html += `
                <div class="vital-item">
                    <div class="vital-info">
                        <i class="fas ${icon}"></i>
                        <span class="vital-name">${vitalNames[vital]}</span>
                    </div>
                    <div class="vital-value">
                        <span class="value">${valueText}${unit}</span>
                        <span class="metric-rating ${ratingClass}">${ratingText}</span>
                    </div>
                    <div class="vital-progress">
                        <div class="progress-bar" style="width: ${getProgressWidth(metric.value, vital)}%; background: ${getProgressColor(metric.rating)}"></div>
                    </div>
                </div>
            `;
        }
    }
    
    html += '</div></div>';
    return html;
}

// Helper function for progress bar width
function getProgressWidth(value, metric) {
    const maxValues = {
        'lcp': 4000,
        'fid': 300,
        'cls': 0.25,
        'ttfb': 500,
        'fcp': 3000
    };
    const max = maxValues[metric] || 100;
    return Math.min(100, (value / max) * 100);
}

function getProgressColor(rating) {
    if (rating === 'good') return '#10b981';
    if (rating === 'needs_improvement') return '#f59e0b';
    return '#ef4444';
}

// Render Resource Metrics
function renderResourceMetrics(metrics) {
    const resources = metrics.resource_counts;
    const pageSize = metrics.page_size_kb;
    const compression = metrics.compression;
    const cache = metrics.cache_headers;
    
    return `
        <div class="metric-card">
            <div class="metric-header">
                <i class="fas fa-boxes"></i>
                <h3>Resource Analysis</h3>
            </div>
            <div class="resource-stats">
                <div class="resource-item">
                    <i class="fab fa-js"></i>
                    <span class="resource-label">JavaScript</span>
                    <span class="resource-count">${resources.javascript_files} files</span>
                </div>
                <div class="resource-item">
                    <i class="fab fa-css3-alt"></i>
                    <span class="resource-label">CSS</span>
                    <span class="resource-count">${resources.css_files} files</span>
                </div>
                <div class="resource-item">
                    <i class="fas fa-image"></i>
                    <span class="resource-label">Images</span>
                    <span class="resource-count">${resources.images}</span>
                </div>
                <div class="resource-divider"></div>
                <div class="resource-item">
                    <i class="fas fa-weight-hanging"></i>
                    <span class="resource-label">Page Size</span>
                    <span class="resource-value">${pageSize} KB</span>
                </div>
                <div class="resource-item">
                    <i class="fas fa-compress"></i>
                    <span class="resource-label">Compression</span>
                    <span class="resource-value ${compression.is_compressed ? 'success' : 'error'}">
                        ${compression.is_compressed ? '✅ Enabled' : '❌ Not enabled'}
                    </span>
                </div>
                <div class="resource-item">
                    <i class="fas fa-database"></i>
                    <span class="resource-label">Caching</span>
                    <span class="resource-value ${cache.has_caching ? 'success' : 'error'}">
                        ${cache.has_caching ? '✅ Enabled' : '❌ Not enabled'}
                    </span>
                </div>
            </div>
        </div>
    `;
}

// Render SEO Metrics
function renderSEOMetrics(htmlStructure) {
    const headings = htmlStructure.heading_structure;
    const images = htmlStructure.image_alt_tags;
    
    return `
        <div class="metric-card">
            <div class="metric-header">
                <i class="fas fa-magnifying-glass"></i>
                <h3>SEO & Accessibility</h3>
            </div>
            <div class="seo-stats">
                <div class="seo-item ${htmlStructure.has_meta_viewport ? 'pass' : 'fail'}">
                    <i class="fas fa-${htmlStructure.has_meta_viewport ? 'check-circle' : 'times-circle'}"></i>
                    <span>Meta Viewport</span>
                </div>
                <div class="seo-item ${htmlStructure.has_description ? 'pass' : 'fail'}">
                    <i class="fas fa-${htmlStructure.has_description ? 'check-circle' : 'times-circle'}"></i>
                    <span>Meta Description</span>
                </div>
                <div class="seo-item ${htmlStructure.has_og_tags ? 'pass' : 'fail'}">
                    <i class="fas fa-${htmlStructure.has_og_tags ? 'check-circle' : 'times-circle'}"></i>
                    <span>Open Graph Tags</span>
                </div>
                <div class="seo-item ${headings.has_h1 ? 'pass' : 'fail'}">
                    <i class="fas fa-${headings.has_h1 ? 'check-circle' : 'times-circle'}"></i>
                    <span>H1 Tag Present</span>
                </div>
                <div class="seo-item ${headings.is_logical ? 'pass' : 'warn'}">
                    <i class="fas fa-${headings.is_logical ? 'check-circle' : 'exclamation-triangle'}"></i>
                    <span>Logical Heading Structure</span>
                </div>
                <div class="seo-item">
                    <i class="fas fa-image"></i>
                    <span>Images with Alt Text: ${images.percentage}%</span>
                    <div class="alt-progress">
                        <div class="progress-fill" style="width: ${images.percentage}%; background: ${images.percentage >= 80 ? '#10b981' : images.percentage >= 50 ? '#f59e0b' : '#ef4444'}"></div>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Render Recommendations
function renderRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return '<div class="no-recommendations"><i class="fas fa-trophy"></i><p>Excellent! No major issues found. Your website is well-optimized!</p></div>';
    }
    
    let html = '<div class="recommendations-list-container">';
    const priorityOrder = { 'High': 1, 'Medium': 2, 'Low': 3 };
    
    recommendations.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    
    recommendations.forEach((rec, index) => {
        let priorityIcon = '';
        let priorityClass = '';
        if (rec.priority === 'High') {
            priorityIcon = 'fa-flag';
            priorityClass = 'priority-high';
        } else if (rec.priority === 'Medium') {
            priorityIcon = 'fa-chart-line';
            priorityClass = 'priority-medium';
        } else {
            priorityIcon = 'fa-info-circle';
            priorityClass = 'priority-low';
        }
        
        let impactIcon = '';
        if (rec.estimated_impact === 'Critical') impactIcon = 'fa-skull-crossbones';
        else if (rec.estimated_impact === 'High') impactIcon = 'fa-arrow-up';
        else if (rec.estimated_impact === 'Medium') impactIcon = 'fa-minus';
        else impactIcon = 'fa-arrow-down';
        
        html += `
            <div class="recommendation-item" data-priority="${rec.priority}">
                <div class="recommendation-header">
                    <div class="recommendation-category">
                        <i class="fas ${priorityIcon} ${priorityClass}"></i>
                        <span>${rec.category}</span>
                    </div>
                    <div class="recommendation-priority ${priorityClass}">${rec.priority} Priority</div>
                </div>
                <div class="recommendation-issue">
                    <i class="fas fa-exclamation-circle"></i> ${rec.issue}
                </div>
                <div class="recommendation-text">
                    <i class="fas fa-lightbulb"></i> ${rec.recommendation}
                </div>
                <div class="recommendation-impact">
                    <i class="fas ${impactIcon}"></i> Expected Impact: ${rec.estimated_impact}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// Display batch results
function displayBatchResults(data) {
    let html = `
        <div class="results-card">
            <div class="score-header">
                <h2><i class="fas fa-layer-group"></i> Batch Analysis Results</h2>
                <p>Analyzed ${data.total_analyzed} websites</p>
            </div>
            <div class="batch-results-grid">
    `;
    
    data.results.forEach((result, index) => {
        if (result.error) {
            html += `
                <div class="batch-card error">
                    <div class="batch-header">
                        <i class="fas fa-exclamation-triangle"></i>
                        <h3>${result.url || `Website ${index + 1}`}</h3>
                    </div>
                    <p class="error-message">Error: ${result.error}</p>
                </div>
            `;
        } else {
            const score = result.overall_score;
            let scoreClass = '';
            if (score >= 80) scoreClass = 'excellent';
            else if (score >= 50) scoreClass = 'average';
            else scoreClass = 'poor';
            
            html += `
                <div class="batch-card ${scoreClass}">
                    <div class="batch-header">
                        <i class="fas fa-globe"></i>
                        <h3>${result.url}</h3>
                        <div class="batch-score ${scoreClass}">${score}</div>
                    </div>
                    <div class="batch-metrics">
                        <div class="batch-metric">
                            <i class="fas fa-weight-hanging"></i>
                            <span>${result.metrics.page_size_kb} KB</span>
                            <small>Page Size</small>
                        </div>
                        <div class="batch-metric">
                            <i class="fas fa-tachometer-alt"></i>
                            <span>${result.metrics.response_time_ms}ms</span>
                            <small>Response</small>
                        </div>
                        <div class="batch-metric">
                            <i class="fas fa-code"></i>
                            <span>${result.metrics.resource_counts.javascript_files}</span>
                            <small>JS Files</small>
                        </div>
                        <div class="batch-metric">
                            <i class="fas fa-image"></i>
                            <span>${result.metrics.resource_counts.images}</span>
                            <small>Images</small>
                        </div>
                    </div>
                    <div class="batch-rating">
                        <span class="rating-badge rating-${result.analysis.overall_rating}">
                            ${result.analysis.overall_rating.toUpperCase()}
                        </span>
                    </div>
                    <button onclick="viewDetails('${result.url}')" class="btn-view-details">
                        <i class="fas fa-chart-line"></i> View Details
                    </button>
                </div>
            `;
        }
    });
    
    html += `
            </div>
        </div>
    `;
    
    batchResultsContainer.innerHTML = html;
    batchResultsContainer.style.display = 'block';
}

// Display comparison results
function displayComparisonResults(data) {
    let html = `
        <div class="results-card">
            <div class="score-header">
                <h2><i class="fas fa-chart-comparison"></i> Website Comparison</h2>
                <p>Comparing ${data.comparison.length} websites</p>
            </div>
    `;
    
    if (data.chart) {
        html += `
            <div class="comparison-chart">
                <img src="${data.chart}" alt="Comparison Chart" class="comparison-image">
            </div>
        `;
    }
    
    html += `
            <div class="comparison-table-wrapper">
                <table class="comparison-table">
                    <thead>
                        <tr>
                            <th>Website</th>
                            <th>Score</th>
                            <th>LCP (ms)</th>
                            <th>FID (ms)</th>
                            <th>CLS</th>
                            <th>TTFB (ms)</th>
                            <th>Page Size (KB)</th>
                        </tr>
                    </thead>
                    <tbody>
    `;
    
    data.comparison.forEach(website => {
        const analysis = website.analysis;
        let scoreClass = '';
        if (website.score >= 80) scoreClass = 'score-excellent';
        else if (website.score >= 50) scoreClass = 'score-average';
        else scoreClass = 'score-poor';
        
        html += `
            <tr>
                <td><i class="fas fa-globe"></i> ${website.url}</td>
                <td class="${scoreClass}"><strong>${website.score}</strong></td>
                <td>${analysis.lcp ? Math.round(analysis.lcp.value) : 'N/A'}</td>
                <td>${analysis.fid ? Math.round(analysis.fid.value) : 'N/A'}</td>
                <td>${analysis.cls ? analysis.cls.value.toFixed(3) : 'N/A'}</td>
                <td>${analysis.ttfb ? Math.round(analysis.ttfb.value) : 'N/A'}</td>
                <td>${website.metrics.page_size_kb}</td>
            </tr>
        `;
    });
    
    html += `
                    </tbody>
                </table>
            </div>
            
            <div class="comparison-insights">
                <h3><i class="fas fa-chart-simple"></i> Insights</h3>
                <ul>
                    <li><i class="fas fa-trophy"></i> Best Performance: ${getBestWebsite(data.comparison)}</li>
                    <li><i class="fas fa-chart-line"></i> Average Score: ${calculateAverageScore(data.comparison)}/100</li>
                    <li><i class="fas fa-rocket"></i> ${getPerformanceInsight(data.comparison)}</li>
                </ul>
            </div>
        </div>
    `;
    
    compareResultsContainer.innerHTML = html;
    compareResultsContainer.style.display = 'block';
}

// Helper functions for comparison
function getBestWebsite(comparison) {
    const best = comparison.reduce((max, site) => site.score > max.score ? site : max, comparison[0]);
    return `${best.url} (${best.score}/100)`;
}

function calculateAverageScore(comparison) {
    const total = comparison.reduce((sum, site) => sum + site.score, 0);
    return Math.round(total / comparison.length);
}

function getPerformanceInsight(comparison) {
    const best = comparison.reduce((max, site) => site.score > max.score ? site : max, comparison[0]);
    const worst = comparison.reduce((min, site) => site.score < min.score ? site : min, comparison[0]);
    const diff = best.score - worst.score;
    
    if (diff > 30) {
        return `Large performance gap detected (${diff} points difference between best and worst)`;
    } else if (diff > 15) {
        return `Moderate performance variation across websites (${diff} point spread)`;
    } else {
        return `Consistent performance across all websites (only ${diff} point difference)`;
    }
}

// Download report
async function downloadReport(data) {
    if (!data || !data.url) {
        showError('No analysis results available');
        return;
    }
    
    showNotification('Generating PDF report...', 'info');
    
    try {
        const response = await fetch('/generate-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                url: data.url,
                metrics: data
            })
        });
        
        const result = await response.json();
        
        if (result.success && result.download_url) {
            window.location.href = result.download_url;
            showNotification('Report generated successfully!', 'success');
        } else {
            showError('Failed to generate report');
        }
    } catch (error) {
        showError('Error generating report');
        console.error('Error:', error);
    }
}

// Share results
function shareResults(data) {
    const shareText = `Check out the performance score of ${data.url}: ${data.overall_score}/100! ${data.analysis.overall_rating.toUpperCase()} performance rating.`;
    
    if (navigator.share) {
        navigator.share({
            title: 'Website Performance Analysis',
            text: shareText,
            url: data.url
        }).catch(() => {
            copyToClipboard(shareText);
        });
    } else {
        copyToClipboard(shareText);
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showError('Failed to copy to clipboard');
    });
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// View details from batch results
window.viewDetails = function(url) {
    document.getElementById('url-input').value = url;
    document.querySelector('[data-tab="single"]').click();
    setTimeout(() => {
        analyzeBtn.click();
    }, 100);
};

// Show error message
function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-toast';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()"><i class="fas fa-times"></i></button>
    `;
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        errorDiv.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        errorDiv.classList.remove('show');
        setTimeout(() => errorDiv.remove(), 300);
    }, 5000);
}

// Add enter key support
if (urlInput) {
    urlInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            analyzeBtn.click();
        }
    });
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});

// Initialize tooltips
document.querySelectorAll('[data-tooltip]').forEach(element => {
    element.addEventListener('mouseenter', (e) => {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = element.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = element.getBoundingClientRect();
        tooltip.style.left = `${rect.left + rect.width / 2}px`;
        tooltip.style.top = `${rect.top - 30}px`;
        tooltip.style.transform = 'translateX(-50%)';
        
        element.addEventListener('mouseleave', () => {
            tooltip.remove();
        }, { once: true });
    });
});