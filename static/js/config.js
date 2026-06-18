// Chart configuration and helper functions
const ChartConfig = {
    colors: {
        good: '#10b981',
        warning: '#f59e0b',
        poor: '#ef4444',
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#ec4899'
    },
    
    thresholds: {
        lcp: { good: 2500, poor: 4000 },
        fid: { good: 100, poor: 300 },
        cls: { good: 0.1, poor: 0.25 },
        ttfb: { good: 200, poor: 500 },
        fcp: { good: 1800, poor: 3000 }
    },
    
    getRatingColor: function(value, metric) {
        const threshold = this.thresholds[metric];
        if (!threshold) return this.colors.primary;
        
        if (value <= threshold.good) return this.colors.good;
        if (value <= threshold.poor) return this.colors.warning;
        return this.colors.poor;
    },
    
    formatMetricValue: function(value, metric) {
        if (metric === 'cls') return value.toFixed(3);
        return `${Math.round(value)}ms`;
    },
    
    // Export graph as image
    exportGraph: function(elementId, format = 'png') {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        // This would require html2canvas library
        // For now, just show a message
        alert('Export feature requires html2canvas library. Add it to enable export.');
    }
};

// Export helper for batch results comparison
function compareWebsites(results) {
    const comparison = {
        bestScore: { url: '', score: 0 },
        worstScore: { url: '', score: 100 },
        averageScore: 0,
        metrics: {}
    };
    
    let totalScore = 0;
    results.forEach(result => {
        if (!result.error && result.overall_score) {
            totalScore += result.overall_score;
            
            if (result.overall_score > comparison.bestScore.score) {
                comparison.bestScore = { url: result.url, score: result.overall_score };
            }
            
            if (result.overall_score < comparison.worstScore.score) {
                comparison.worstScore = { url: result.url, score: result.overall_score };
            }
        }
    });
    
    comparison.averageScore = totalScore / results.length;
    
    return comparison;
}