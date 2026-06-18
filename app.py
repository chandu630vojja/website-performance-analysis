from flask import Flask, render_template, request, jsonify, send_file
import os
import json
from datetime import datetime
from analysis import WebsitePerformanceAnalyzer
from utils.helper import validate_url, generate_report_pdf
import logging

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'reports'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure directories exist
os.makedirs('reports', exist_ok=True)
os.makedirs('data', exist_ok=True)
os.makedirs('models', exist_ok=True)

analyzer = WebsitePerformanceAnalyzer()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze website performance"""
    try:
        url = request.form.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Validate URL
        if not validate_url(url):
            return jsonify({'error': 'Invalid URL format. Please include http:// or https://'}), 400
        
        # Add https if no protocol specified
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Perform analysis
        logger.info(f"Analyzing website: {url}")
        results = analyzer.analyze_website(url)
        
        if results.get('error'):
            return jsonify({'error': results['error']}), 400
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}")
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    """Generate PDF report"""
    try:
        data = request.json
        url = data.get('url')
        metrics = data.get('metrics')
        
        if not url or not metrics:
            return jsonify({'error': 'Missing data for report generation'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_filename = f"performance_report_{timestamp}.pdf"
        report_path = os.path.join('reports', report_filename)
        
        # Generate PDF report
        generate_report_pdf(url, metrics, report_path)
        
        return jsonify({
            'success': True,
            'report_file': report_filename,
            'download_url': f'/download-report/{report_filename}'
        })
    
    except Exception as e:
        logger.error(f"Report generation error: {str(e)}")
        return jsonify({'error': f'Report generation failed: {str(e)}'}), 500

@app.route('/download-report/<filename>')
def download_report(filename):
    """Download generated report"""
    try:
        report_path = os.path.join('reports', filename)
        if os.path.exists(report_path):
            return send_file(report_path, as_attachment=True)
        else:
            return jsonify({'error': 'Report not found'}), 404
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return jsonify({'error': 'Failed to download report'}), 500

@app.route('/api/batch-analyze', methods=['POST'])
def batch_analyze():
    """Analyze multiple websites"""
    try:
        urls = request.json.get('urls', [])
        
        if not urls or len(urls) > 10:
            return jsonify({'error': 'Please provide 1-10 URLs for batch analysis'}), 400
        
        results = []
        for url in urls:
            url = url.strip()
            if validate_url(url):
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                result = analyzer.analyze_website(url)
                results.append(result)
        
        return jsonify({
            'total_analyzed': len(results),
            'results': results
        })
    
    except Exception as e:
        logger.error(f"Batch analysis error: {str(e)}")
        return jsonify({'error': f'Batch analysis failed: {str(e)}'}), 500

@app.route('/api/compare', methods=['POST'])
def compare_websites():
    """Compare multiple websites"""
    try:
        urls = request.json.get('urls', [])
        
        if len(urls) < 2 or len(urls) > 5:
            return jsonify({'error': 'Please provide 2-5 URLs for comparison'}), 400
        
        results = []
        for url in urls:
            url = url.strip()
            if validate_url(url):
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                result = analyzer.analyze_website(url)
                if not result.get('error'):
                    results.append({
                        'url': url,
                        'score': result.get('overall_score', 0),
                        'metrics': result.get('metrics', {}),
                        'analysis': result.get('analysis', {})
                    })
        
        # Generate comparison chart
        comparison_chart = analyzer.generate_comparison_chart(results)
        
        return jsonify({
            'comparison': results,
            'chart': comparison_chart
        })
    
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        return jsonify({'error': f'Comparison failed: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)