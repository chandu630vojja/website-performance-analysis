import re
from urllib.parse import urlparse
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import json
import os

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    # Add http:// if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def extract_domain(url: str) -> str:
    """Extract domain name from URL"""
    parsed = urlparse(url)
    return parsed.netloc

def format_size(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} TB"

def generate_report_pdf(url: str, metrics: dict, filename: str):
    """Generate PDF performance report with graphs"""
    doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#4f46e5'),
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    subheading_style = ParagraphStyle(
        'Subheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=10
    )
    
    story = []
    
    # Title
    story.append(Paragraph(f"Website Performance Analysis Report", title_style))
    story.append(Paragraph(f"URL: {url}", styles['Normal']))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    if 'error' in metrics:
        story.append(Paragraph(f"Error: {metrics['error']}", styles['Normal']))
    else:
        # Overall Score
        score = metrics.get('overall_score', 0)
        story.append(Paragraph(f"Overall Performance Score: {score}/100", heading_style))
        story.append(Spacer(1, 10))
        
        # Add graphs if available
        graphs = metrics.get('graphs', {})
        if graphs:
            story.append(Paragraph("Performance Visualizations", heading_style))
            
            # Add score gauge if available
            if graphs.get('score_gauge'):
                try:
                    import base64
                    from io import BytesIO
                    from PIL import Image as PILImage
                    
                    # Decode base64 image
                    img_data = graphs['score_gauge'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img = PILImage.open(BytesIO(img_bytes))
                    
                    # Save temporary file
                    temp_img = f"/tmp/gauge_{datetime.now().timestamp()}.png"
                    img.save(temp_img)
                    
                    # Add to PDF
                    story.append(Image(temp_img, width=4*inch, height=3*inch))
                    story.append(Spacer(1, 10))
                    
                    # Cleanup
                    os.remove(temp_img)
                except:
                    pass
            
            # Add core vitals chart
            if graphs.get('core_vitals_bar'):
                try:
                    import base64
                    from io import BytesIO
                    from PIL import Image as PILImage
                    
                    img_data = graphs['core_vitals_bar'].split(',')[1]
                    img_bytes = base64.b64decode(img_data)
                    img = PILImage.open(BytesIO(img_bytes))
                    
                    temp_img = f"/tmp/vitals_{datetime.now().timestamp()}.png"
                    img.save(temp_img)
                    
                    story.append(Image(temp_img, width=6*inch, height=4*inch))
                    story.append(Spacer(1, 10))
                    
                    os.remove(temp_img)
                except:
                    pass
            
            story.append(PageBreak())
        
        # Core Web Vitals
        story.append(Paragraph("Core Web Vitals", heading_style))
        analysis = metrics.get('analysis', {})
        vitals_data = []
        
        vital_names = {
            'lcp': 'Largest Contentful Paint',
            'fid': 'First Input Delay',
            'cls': 'Cumulative Layout Shift',
            'ttfb': 'Time to First Byte',
            'fcp': 'First Contentful Paint'
        }
        
        for vital in ['lcp', 'fid', 'cls', 'ttfb', 'fcp']:
            if vital in analysis:
                vital_data = analysis[vital]
                value = vital_data['value']
                rating = vital_data['rating'].replace('_', ' ').title()
                
                if vital in ['lcp', 'fcp', 'ttfb']:
                    value_str = f"{value:.0f} ms"
                elif vital == 'cls':
                    value_str = f"{value:.3f}"
                else:
                    value_str = f"{value:.0f} ms"
                
                # Color code rating
                if rating == 'Good':
                    rating = f'<font color="#10b981">{rating}</font>'
                elif rating == 'Needs Improvement':
                    rating = f'<font color="#f59e0b">{rating}</font>'
                else:
                    rating = f'<font color="#ef4444">{rating}</font>'
                
                vitals_data.append([
                    Paragraph(f"<b>{vital_names[vital]}</b>", styles['Normal']),
                    Paragraph(value_str, styles['Normal']),
                    Paragraph(rating, styles['Normal'])
                ])
        
        vitals_table = Table([['Metric', 'Value', 'Rating']] + vitals_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        vitals_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(vitals_table)
        story.append(Spacer(1, 20))
        
        # Resource Metrics
        story.append(Paragraph("Resource Analysis", heading_style))
        resource_metrics = metrics.get('metrics', {}).get('resource_counts', {})
        page_size = metrics.get('metrics', {}).get('page_size_kb', 0)
        compression = metrics.get('metrics', {}).get('compression', {})
        cache = metrics.get('metrics', {}).get('cache_headers', {})
        
        resources_data = [
            ['Metric', 'Value'],
            ['Page Size', f"{page_size} KB"],
            ['JavaScript Files', str(resource_metrics.get('javascript_files', 0))],
            ['CSS Files', str(resource_metrics.get('css_files', 0))],
            ['Images', str(resource_metrics.get('images', 0))],
            ['Total Resources', str(resource_metrics.get('total_resources', 0))],
            ['Compression', '✅ Enabled' if compression.get('is_compressed') else '❌ Not enabled'],
            ['Caching', '✅ Enabled' if cache.get('has_caching') else '❌ Not enabled']
        ]
        
        resources_table = Table(resources_data, colWidths=[2.5*inch, 2*inch])
        resources_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(resources_table)
        story.append(Spacer(1, 20))
        
        # SEO Metrics
        story.append(Paragraph("SEO & Accessibility", heading_style))
        html_struct = metrics.get('metrics', {}).get('html_structure', {})
        headings = html_struct.get('heading_structure', {})
        images = html_struct.get('image_alt_tags', {})
        
        seo_data = [
            ['Metric', 'Status'],
            ['Meta Viewport', '✅' if html_struct.get('has_meta_viewport') else '❌'],
            ['Meta Description', '✅' if html_struct.get('has_description') else '❌'],
            ['Open Graph Tags', '✅' if html_struct.get('has_og_tags') else '❌'],
            ['H1 Tag Present', '✅' if headings.get('has_h1') else '❌'],
            ['Logical Heading Structure', '✅' if headings.get('is_logical') else '⚠️'],
            ['Images with Alt Text', f"{images.get('percentage', 0)}%"]
        ]
        
        seo_table = Table(seo_data, colWidths=[2.5*inch, 2*inch])
        seo_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(seo_table)
        story.append(Spacer(1, 20))
        
        # Recommendations
        recommendations = metrics.get('recommendations', [])
        if recommendations:
            story.append(Paragraph("Optimization Recommendations", heading_style))
            for i, rec in enumerate(recommendations[:15], 1):  # Limit to top 15
                story.append(Paragraph(f"<b>{i}. {rec['category']} - {rec['priority']} Priority</b>", styles['Normal']))
                story.append(Paragraph(f"<b>Issue:</b> {rec['issue']}", styles['Normal']))
                story.append(Paragraph(f"<b>Solution:</b> {rec['recommendation']}", styles['Normal']))
                story.append(Paragraph(f"<b>Impact:</b> {rec['estimated_impact']}", styles['Normal']))
                story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)

def save_json_results(data: dict, filename: str):
    """Save results to JSON file"""
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_json_results(filename: str) -> dict:
    """Load results from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def calculate_percentile(data: list, percentile: int) -> float:
    """Calculate percentile of a list of numbers"""
    if not data:
        return 0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[index]

def get_performance_grade(score: int) -> str:
    """Convert numeric score to letter grade"""
    if score >= 90:
        return 'A+'
    elif score >= 80:
        return 'A'
    elif score >= 70:
        return 'B'
    elif score >= 60:
        return 'C'
    elif score >= 50:
        return 'D'
    else:
        return 'F'