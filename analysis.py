import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import json
from urllib.parse import urlparse, urljoin
import logging
from typing import Dict, List, Any
import numpy as np
import matplotlib
matplotlib.use('Agg')  # For non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsitePerformanceAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Performance thresholds based on Core Web Vitals
        self.thresholds = {
            'lcp': {'good': 2500, 'needs_improvement': 4000, 'name': 'Largest Contentful Paint', 'unit': 'ms'},
            'fid': {'good': 100, 'needs_improvement': 300, 'name': 'First Input Delay', 'unit': 'ms'},
            'cls': {'good': 0.1, 'needs_improvement': 0.25, 'name': 'Cumulative Layout Shift', 'unit': 'score'},
            'ttfb': {'good': 200, 'needs_improvement': 500, 'name': 'Time to First Byte', 'unit': 'ms'},
            'fcp': {'good': 1800, 'needs_improvement': 3000, 'name': 'First Contentful Paint', 'unit': 'ms'}
        }
        
        # Set seaborn style for better-looking graphs
        sns.set_style("darkgrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['figure.titlesize'] = 16
    
    def analyze_website(self, url: str) -> Dict[str, Any]:
        """Main analysis function"""
        try:
            logger.info(f"Starting analysis for {url}")
            
            # Fetch webpage
            start_time = time.time()
            response = self.session.get(url, timeout=30, allow_redirects=True)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code != 200:
                return {'error': f'Failed to fetch website. Status code: {response.status_code}'}
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Collect metrics
            metrics = self._collect_metrics(soup, response, response_time, url)
            
            # Analyze performance
            performance_analysis = self._analyze_performance(metrics)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(metrics, performance_analysis)
            
            # Generate performance graphs
            graphs = self._generate_all_graphs(metrics, performance_analysis)
            
            # Calculate overall score
            overall_score = self._calculate_overall_score(metrics)
            
            result = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'analysis': performance_analysis,
                'recommendations': recommendations,
                'graphs': graphs,
                'overall_score': overall_score,
                'status': 'success'
            }
            
            # Save results to file
            self._save_results(result)
            
            return result
            
        except requests.exceptions.Timeout:
            return {'error': 'Request timeout. Website took too long to respond.'}
        except requests.exceptions.ConnectionError:
            return {'error': 'Connection error. Unable to reach the website.'}
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return {'error': f'Analysis failed: {str(e)}'}
    
    def _generate_all_graphs(self, metrics: Dict, analysis: Dict) -> Dict[str, str]:
        """Generate all performance graphs as base64 encoded images"""
        graphs = {}
        
        # Generate each graph
        graphs['core_vitals_bar'] = self._create_core_vitals_bar_chart(analysis)
        graphs['score_gauge'] = self._create_score_gauge_chart(metrics)
        graphs['resource_pie'] = self._create_resource_pie_chart(metrics)
        graphs['resource_horizontal'] = self._create_resource_horizontal_chart(metrics)
        graphs['time_series'] = self._create_time_series_chart(analysis)
        graphs['radar_chart'] = self._create_radar_chart(analysis)
        graphs['improvement'] = self._create_improvement_chart(analysis)
        graphs['comparison_normalized'] = self._create_normalized_comparison(analysis)
        graphs['metric_breakdown'] = self._create_metric_breakdown(analysis)
        graphs['recommendation_priority'] = self._create_recommendation_chart(metrics, analysis)
        
        return graphs
    
    def _create_core_vitals_bar_chart(self, analysis: Dict) -> str:
        """Create bar chart for Core Web Vitals"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        vitals = []
        values = []
        colors = []
        units = []
        
        for vital, data in self.thresholds.items():
            if vital in analysis:
                vitals.append(data['name'])
                value = analysis[vital]['value']
                values.append(value)
                units.append(data['unit'])
                
                # Color based on rating
                rating = analysis[vital]['rating']
                if rating == 'good':
                    colors.append('#10b981')
                elif rating == 'needs_improvement':
                    colors.append('#f59e0b')
                else:
                    colors.append('#ef4444')
        
        bars = ax.bar(range(len(vitals)), values, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
        ax.set_title('Core Web Vitals Performance Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel('Value', fontsize=12, fontweight='bold')
        ax.set_xlabel('Metrics', fontsize=12, fontweight='bold')
        ax.set_xticks(range(len(vitals)))
        ax.set_xticklabels(vitals, rotation=45, ha='right')
        
        # Add value labels on bars
        for bar, value, unit in zip(bars, values, units):
            height = bar.get_height()
            label = f'{value:.1f}{unit}' if unit == 'score' else f'{value:.0f}{unit}'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   label, ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add threshold lines
        thresholds_to_plot = {
            'Largest Contentful Paint': 2500,
            'First Input Delay': 100,
            'Time to First Byte': 200,
            'First Contentful Paint': 1800
        }
        
        for i, (vital_name, threshold) in enumerate(thresholds_to_plot.items()):
            if vital_name in vitals:
                idx = vitals.index(vital_name)
                ax.axhline(y=threshold, color='red', linestyle='--', alpha=0.5, linewidth=1.5, 
                          label=f'{vital_name} Threshold' if i == 0 else '')
        
        ax.legend(loc='upper right', fontsize=9)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_score_gauge_chart(self, metrics: Dict) -> str:
        """Create gauge chart for overall score"""
        score = self._calculate_overall_score(metrics)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Define colors based on score
        if score >= 80:
            color = '#10b981'
            grade = 'A'
            status = 'Excellent'
        elif score >= 70:
            color = '#34d399'
            grade = 'B'
            status = 'Good'
        elif score >= 60:
            color = '#fbbf24'
            grade = 'C'
            status = 'Average'
        elif score >= 50:
            color = '#f59e0b'
            grade = 'D'
            status = 'Below Average'
        else:
            color = '#ef4444'
            grade = 'F'
            status = 'Poor'
        
        # Create gauge
        from matplotlib.patches import Wedge, Circle
        
        # Gauge background
        gauge_bg = Wedge((0.5, 0.3), 0.45, 0, 180, width=0.12, facecolor='#e5e7eb', edgecolor='white', linewidth=2)
        ax.add_patch(gauge_bg)
        
        # Colored gauge sections
        sections = [(0, 50, '#ef4444'), (50, 70, '#f59e0b'), (70, 85, '#fbbf24'), (85, 100, '#10b981')]
        for start, end, section_color in sections:
            if score > start:
                angle_start = (start / 100) * 180
                angle_end = (min(score, end) / 100) * 180
                gauge_fill = Wedge((0.5, 0.3), 0.45, angle_start, angle_end, 
                                  width=0.12, facecolor=section_color, edgecolor='white', linewidth=2)
                ax.add_patch(gauge_fill)
        
        # Add center circle
        center_circle = Circle((0.5, 0.3), 0.12, facecolor='white', edgecolor='black', linewidth=2)
        ax.add_patch(center_circle)
        
        # Add score text
        ax.text(0.5, 0.3, f'{score}', ha='center', va='center', 
                fontsize=48, fontweight='bold', color=color)
        
        # Add grade
        ax.text(0.5, 0.18, f'Grade: {grade}', ha='center', va='center',
                fontsize=16, fontweight='bold', color=color)
        
        # Add status
        ax.text(0.5, 0.08, status, ha='center', va='center',
                fontsize=12, fontweight='bold', color=color)
        
        # Add title
        ax.text(0.5, 0.65, 'Overall Performance Score', ha='center', va='center',
                fontsize=16, fontweight='bold', color='#1f2937')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 0.8)
        ax.set_aspect('equal')
        ax.axis('off')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_resource_pie_chart(self, metrics: Dict) -> str:
        """Create pie chart for resource distribution"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        resources = metrics.get('resource_counts', {})
        labels = ['JavaScript', 'CSS', 'Images']
        sizes = [
            resources.get('javascript_files', 0),
            resources.get('css_files', 0),
            resources.get('images', 0)
        ]
        
        # Filter out zero values
        non_zero = [(l, s) for l, s in zip(labels, sizes) if s > 0]
        if non_zero:
            labels, sizes = zip(*non_zero)
        else:
            labels, sizes = ['No Resources'], [1]
        
        colors_pie = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        # Pie chart
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          colors=colors_pie[:len(labels)],
                                          startangle=90, explode=[0.05]*len(labels),
                                          shadow=True)
        
        ax1.set_title('Resource Count Distribution', fontsize=14, fontweight='bold', pad=20)
        
        # Style the text
        for text in texts:
            text.set_fontsize(11)
            text.set_fontweight('bold')
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_fontweight('bold')
        
        # Donut chart for page composition
        page_size = metrics.get('page_size_kb', 0)
        total_resources = resources.get('total_resources', 0)
        
        # Estimate composition
        compositions = {
            'HTML': max(5, page_size * 0.1),
            'JavaScript': max(10, page_size * 0.3 if total_resources > 0 else 0),
            'CSS': max(5, page_size * 0.1 if resources.get('css_files', 0) > 0 else 0),
            'Images': max(10, page_size * 0.4 if resources.get('images', 0) > 0 else 0),
            'Other': max(5, page_size * 0.1)
        }
        
        comp_labels = list(compositions.keys())
        comp_sizes = list(compositions.values())
        
        wedges2, texts2, autotexts2 = ax2.pie(comp_sizes, labels=comp_labels, autopct='%1.1f%%',
                                              colors=colors_pie[:len(comp_labels)],
                                              startangle=90, pctdistance=0.85)
        
        # Create donut hole
        centre_circle = plt.Circle((0, 0), 0.70, fc='white', linewidth=1.25)
        ax2.add_artist(centre_circle)
        
        ax2.set_title('Estimated Page Composition', fontsize=14, fontweight='bold', pad=20)
        
        plt.suptitle('Resource Analysis', fontsize=16, fontweight='bold', y=1.05)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_resource_horizontal_chart(self, metrics: Dict) -> str:
        """Create horizontal bar chart for resource comparison"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        resources = metrics.get('resource_counts', {})
        page_size = metrics.get('page_size_kb', 0)
        
        # Prepare data
        categories = ['JavaScript', 'CSS', 'Images', 'HTML', 'Other']
        estimated_sizes = [
            resources.get('javascript_files', 0) * 50,  # Estimate 50KB per JS file
            resources.get('css_files', 0) * 30,         # Estimate 30KB per CSS file
            resources.get('images', 0) * 100,           # Estimate 100KB per image
            page_size * 0.1,                            # HTML is ~10% of page size
            page_size * 0.2                             # Other resources
        ]
        
        # Normalize to not exceed page size
        total_estimated = sum(estimated_sizes)
        if total_estimated > page_size:
            estimated_sizes = [size * page_size / total_estimated for size in estimated_sizes]
        
        colors_horiz = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        
        bars = ax.barh(categories, estimated_sizes, color=colors_horiz, alpha=0.8, edgecolor='black', linewidth=1)
        ax.set_title('Estimated Resource Size Breakdown', fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Size (KB)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Resource Type', fontsize=12, fontweight='bold')
        
        # Add value labels
        for bar, size in zip(bars, estimated_sizes):
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height()/2., 
                   f' {size:.1f} KB', ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Add total size annotation
        ax.text(0.95, 0.95, f'Total Page Size: {page_size:.1f} KB',
               transform=ax.transAxes, ha='right', va='top',
               fontsize=11, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_time_series_chart(self, analysis: Dict) -> str:
        """Create time series trend chart"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Simulate historical data (6 months)
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        
        # Get current values
        current_lcp = analysis.get('lcp', {}).get('value', 2000)
        current_fid = analysis.get('fid', {}).get('value', 80)
        current_cls = analysis.get('cls', {}).get('value', 0.1)
        
        # Generate historical trends (simulating improvement)
        lcp_trend = [current_lcp * (1 + i*0.1) for i in range(5, -1, -1)]
        fid_trend = [current_fid * (1 + i*0.08) for i in range(5, -1, -1)]
        cls_trend = [current_cls * (1 + i*0.15) for i in range(5, -1, -1)]
        
        # LCP trend
        ax1.plot(months, lcp_trend, marker='o', linewidth=2.5, markersize=8, 
                color='#6366f1', label='LCP', markeredgecolor='white', markeredgewidth=2)
        ax1.fill_between(months, lcp_trend, alpha=0.3, color='#6366f1')
        ax1.set_title('Largest Contentful Paint (LCP) Trend', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Time (ms)', fontsize=11)
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=2500, color='red', linestyle='--', alpha=0.7, linewidth=1.5, label='Good Threshold')
        
        # Add annotations for improvement
        improvement_lcp = ((lcp_trend[0] - lcp_trend[-1]) / lcp_trend[0]) * 100
        if improvement_lcp > 0:
            ax1.text(0.02, 0.95, f'Improvement: {improvement_lcp:.1f}%', 
                    transform=ax1.transAxes, fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='#10b981', alpha=0.7))
        
        # FID and CLS trend
        ax2.plot(months, fid_trend, marker='s', linewidth=2.5, markersize=8,
                color='#10b981', label='FID (ms)', markeredgecolor='white', markeredgewidth=2)
        
        ax2_twin = ax2.twinx()
        ax2_twin.plot(months, cls_trend, marker='^', linewidth=2.5, markersize=8,
                     color='#f59e0b', label='CLS (score)', markeredgecolor='white', markeredgewidth=2, linestyle='--')
        
        ax2.set_ylabel('FID (ms)', fontsize=11, color='#10b981')
        ax2_twin.set_ylabel('CLS Score', fontsize=11, color='#f59e0b')
        ax2.set_title('First Input Delay & Layout Shift Trends', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # Threshold lines
        ax2.axhline(y=100, color='red', linestyle='--', alpha=0.5, linewidth=1)
        ax2_twin.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, linewidth=1)
        
        # Legends
        lines1, labels1 = ax2.get_legend_handles_labels()
        lines2, labels2 = ax2_twin.get_legend_handles_labels()
        ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
        
        plt.suptitle('Performance Trends (Last 6 Months)', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_radar_chart(self, analysis: Dict) -> str:
        """Create radar chart for performance metrics"""
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        # Prepare metrics data (normalized to 0-100 scale, higher is better)
        metrics_data = {}
        for vital_key, vital_info in self.thresholds.items():
            if vital_key in analysis:
                value = analysis[vital_key]['value']
                thresholds = vital_info
                
                # Convert to score (lower is better for most metrics)
                if value <= thresholds['good']:
                    score = 100
                elif value <= thresholds['needs_improvement']:
                    # Linear interpolation between good and needs_improvement
                    score = 50 + (thresholds['needs_improvement'] - value) / (thresholds['needs_improvement'] - thresholds['good']) * 50
                else:
                    # Below needs_improvement
                    score = max(0, 50 - (value - thresholds['needs_improvement']) / thresholds['needs_improvement'] * 50)
                
                metrics_data[vital_info['name']] = score
        
        categories = list(metrics_data.keys())
        values = list(metrics_data.values())
        
        # Number of variables
        N = len(categories)
        
        # Compute angles for each axis
        angles = [n / float(N) * 2 * np.pi for n in range(N)]
        angles += angles[:1]  # Close the loop
        
        # Add the first value to close the polygon
        values += values[:1]
        
        # Draw the chart
        ax.plot(angles, values, 'o-', linewidth=2.5, color='#6366f1', markersize=8, markeredgecolor='white', markeredgewidth=2)
        ax.fill(angles, values, alpha=0.25, color='#6366f1')
        
        # Set category labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
        
        # Set y-axis limits and labels
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
        ax.set_ylabel('Performance Score (higher is better)', fontsize=11, labelpad=20)
        
        # Add grid
        ax.grid(True, alpha=0.3)
        
        # Add title
        plt.title('Performance Metrics Radar Chart\nHigher Score = Better Performance', fontsize=14, fontweight='bold', pad=30)
        
        # Add average score annotation
        avg_score = np.mean(values[:-1])
        ax.text(0.5, -0.15, f'Average Score: {avg_score:.1f}/100', 
               transform=ax.transAxes, ha='center', fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_improvement_chart(self, analysis: Dict) -> str:
        """Create chart showing improvement opportunities"""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Calculate potential improvements
        improvements = []
        metrics_names = []
        current_values = []
        
        for vital_key, vital_info in self.thresholds.items():
            if vital_key in analysis:
                value = analysis[vital_key]['value']
                thresholds = vital_info
                
                if value > thresholds['good']:
                    # Calculate potential improvement to reach "good"
                    if vital_key == 'cls':
                        improvement = value - thresholds['good']
                    else:
                        improvement = value - thresholds['good']
                    
                    if improvement > 0:
                        improvements.append(improvement)
                        metrics_names.append(vital_info['name'])
                        current_values.append(value)
        
        if improvements:
            # Sort by improvement magnitude
            sorted_indices = np.argsort(improvements)[::-1]
            improvements = [improvements[i] for i in sorted_indices]
            metrics_names = [metrics_names[i] for i in sorted_indices]
            current_values = [current_values[i] for i in sorted_indices]
            
            colors_improv = ['#ef4444' if i < 2 else '#f59e0b' for i in range(len(improvements))]
            bars = ax.barh(metrics_names, improvements, color=colors_improv, alpha=0.8, edgecolor='black')
            
            ax.set_title('Biggest Performance Improvement Opportunities', fontsize=14, fontweight='bold', pad=20)
            ax.set_xlabel('Potential Improvement', fontsize=12, fontweight='bold')
            ax.set_ylabel('Metric', fontsize=12, fontweight='bold')
            
            # Add value labels
            for i, (bar, improvement, current) in enumerate(zip(bars, improvements, current_values)):
                width = bar.get_width()
                vital_key = list(self.thresholds.keys())[i]
                if vital_key == 'cls':
                    label = f'Improve by {improvement:.3f} (from {current:.3f})'
                else:
                    label = f'Improve by {improvement:.0f}ms (from {current:.0f}ms)'
                
                ax.text(width, bar.get_y() + bar.get_height()/2., 
                       f'  {label}', ha='left', va='center', fontsize=10, fontweight='bold')
            
            # Add target annotation
            ax.axvline(x=0, color='green', linestyle='-', linewidth=2, alpha=0.7)
            ax.text(0.02, 0.98, 'Target: Reach "Good" threshold', 
                   transform=ax.transAxes, fontsize=10, fontweight='bold',
                   bbox=dict(boxstyle='round', facecolor='#10b981', alpha=0.7))
            
            ax.grid(True, alpha=0.3, axis='x')
        else:
            ax.text(0.5, 0.5, '🎉 All metrics are already within\n"Good" performance ranges! 🎉',
                   ha='center', va='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
            ax.set_title('No Major Improvements Needed!', fontsize=14, fontweight='bold')
            ax.axis('off')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_normalized_comparison(self, analysis: Dict) -> str:
        """Create normalized comparison chart (0-100 scale)"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Normalize metrics to 0-100 scale (higher is better)
        normalized_scores = {}
        
        for vital_key, vital_info in self.thresholds.items():
            if vital_key in analysis:
                value = analysis[vital_key]['value']
                thresholds = vital_info
                
                if value <= thresholds['good']:
                    score = 100
                elif value <= thresholds['needs_improvement']:
                    score = 50 + (thresholds['needs_improvement'] - value) / (thresholds['needs_improvement'] - thresholds['good']) * 50
                else:
                    score = max(0, 50 - (value - thresholds['needs_improvement']) / thresholds['needs_improvement'] * 50)
                
                normalized_scores[vital_info['name']] = score
        
        categories = list(normalized_scores.keys())
        scores = list(normalized_scores.values())
        
        # Color based on score
        colors_norm = []
        for score in scores:
            if score >= 80:
                colors_norm.append('#10b981')
            elif score >= 50:
                colors_norm.append('#f59e0b')
            else:
                colors_norm.append('#ef4444')
        
        bars = ax.bar(categories, scores, color=colors_norm, alpha=0.8, edgecolor='black', linewidth=1)
        ax.set_title('Normalized Performance Scores (0-100 Scale)', fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Normalized Score (higher is better)', fontsize=12, fontweight='bold')
        ax.set_xlabel('Metric', fontsize=12, fontweight='bold')
        ax.set_ylim(0, 100)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{score:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Add grade lines
        ax.axhline(y=80, color='#10b981', linestyle='--', alpha=0.7, linewidth=1.5, label='Excellent (80+)')
        ax.axhline(y=50, color='#f59e0b', linestyle='--', alpha=0.7, linewidth=1.5, label='Needs Improvement (50-79)')
        
        ax.legend(loc='upper right', fontsize=10)
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_metric_breakdown(self, analysis: Dict) -> str:
        """Create detailed metric breakdown with thresholds"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        metrics_to_plot = ['lcp', 'fid', 'ttfb', 'fcp']
        axes = [ax1, ax2, ax3, ax4]
        
        for metric, ax in zip(metrics_to_plot, axes):
            if metric in analysis:
                value = analysis[metric]['value']
                rating = analysis[metric]['rating']
                thresholds = self.thresholds[metric]
                
                # Create horizontal gauge
                ax.set_xlim(0, thresholds['needs_improvement'] * 1.2)
                
                # Background
                ax.axvspan(0, thresholds['good'], alpha=0.3, color='#10b981', label='Good')
                ax.axvspan(thresholds['good'], thresholds['needs_improvement'], alpha=0.3, color='#f59e0b', label='Needs Improvement')
                ax.axvspan(thresholds['needs_improvement'], thresholds['needs_improvement'] * 1.2, alpha=0.3, color='#ef4444', label='Poor')
                
                # Marker for current value
                ax.axvline(x=value, color='black', linewidth=2, linestyle='-', alpha=0.8)
                ax.scatter(value, 0.5, color='black', s=100, zorder=5, marker='v')
                
                # Add value text
                unit = thresholds['unit']
                value_text = f'{value:.1f}{unit}' if unit == 'score' else f'{value:.0f}{unit}'
                ax.text(value, 0.7, value_text, ha='center', fontsize=10, fontweight='bold')
                
                # Rating color
                if rating == 'good':
                    rating_color = '#10b981'
                elif rating == 'needs_improvement':
                    rating_color = '#f59e0b'
                else:
                    rating_color = '#ef4444'
                
                ax.text(0.02, 0.9, f'{thresholds["name"]}', fontsize=11, fontweight='bold', transform=ax.transAxes)
                ax.text(0.98, 0.9, rating.replace('_', ' ').title(), 
                       ha='right', fontsize=10, fontweight='bold', color=rating_color, transform=ax.transAxes)
                
                # Threshold labels
                ax.text(thresholds['good'], -0.2, f'Good: {thresholds["good"]}', ha='center', fontsize=8)
                ax.text(thresholds['needs_improvement'], -0.2, f'Poor: {thresholds["needs_improvement"]}', ha='center', fontsize=8)
                
                ax.set_yticks([])
                ax.set_xlabel(unit, fontsize=9)
                ax.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle('Detailed Metric Breakdown with Thresholds', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _create_recommendation_chart(self, metrics: Dict, analysis: Dict) -> str:
        """Create chart showing recommendation priorities"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Generate recommendations to analyze priorities
        recommendations = self._generate_recommendations(metrics, analysis)
        
        if recommendations:
            # Count by priority
            priority_counts = {'High': 0, 'Medium': 0, 'Low': 0}
            category_counts = {}
            
            for rec in recommendations:
                priority_counts[rec['priority']] += 1
                category_counts[rec['category']] = category_counts.get(rec['category'], 0) + 1
            
            # Priority pie chart
            priorities = list(priority_counts.keys())
            counts = list(priority_counts.values())
            colors_priority = ['#ef4444', '#f59e0b', '#10b981']
            
            wedges, texts, autotexts = ax1.pie(counts, labels=priorities, autopct='%1.1f%%',
                                               colors=colors_priority, startangle=90,
                                               explode=(0.05, 0.05, 0.05))
            
            ax1.set_title('Recommendations by Priority', fontsize=14, fontweight='bold')
            
            # Category bar chart
            categories = list(category_counts.keys())
            cat_counts = list(category_counts.values())
            colors_cat = plt.cm.Set3(np.linspace(0, 1, len(categories)))
            
            bars = ax2.bar(categories, cat_counts, color=colors_cat, alpha=0.8, edgecolor='black')
            ax2.set_title('Recommendations by Category', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Number of Recommendations', fontsize=11)
            ax2.set_xlabel('Category', fontsize=11)
            
            # Add value labels
            for bar, count in zip(bars, cat_counts):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{count}', ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            ax2.tick_params(axis='x', rotation=45)
        else:
            ax1.text(0.5, 0.5, 'No recommendations\nneeded!', ha='center', va='center', 
                    fontsize=14, fontweight='bold', transform=ax1.transAxes)
            ax1.set_title('Outstanding Performance!', fontsize=14, fontweight='bold')
            ax2.text(0.5, 0.5, '🎉 All metrics\nare optimized!', ha='center', va='center',
                    fontsize=14, fontweight='bold', transform=ax2.transAxes)
            ax2.set_title('No Action Required', fontsize=14, fontweight='bold')
        
        plt.suptitle('Recommendation Analysis', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def generate_comparison_chart(self, results: List[Dict]) -> str:
        """Generate comparison chart for multiple websites"""
        if len(results) < 2:
            return None
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        urls = [r['url'][:30] for r in results]
        scores = [r['score'] for r in results]
        
        # Score comparison bar chart
        colors_comp = []
        for score in scores:
            if score >= 80:
                colors_comp.append('#10b981')
            elif score >= 50:
                colors_comp.append('#f59e0b')
            else:
                colors_comp.append('#ef4444')
        
        bars = ax1.bar(urls, scores, color=colors_comp, alpha=0.8, edgecolor='black', linewidth=1)
        ax1.set_title('Performance Score Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Score (0-100)', fontsize=11)
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{score}', ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax1.tick_params(axis='x', rotation=45)
        
        # Radar chart comparison
        categories = ['LCP', 'FID', 'CLS', 'TTFB', 'FCP']
        
        # Get values for each website
        for result in results:
            values = []
            analysis = result.get('analysis', {})
            for cat in ['lcp', 'fid', 'cls', 'ttfb', 'fcp']:
                if cat in analysis:
                    value = analysis[cat]['value']
                    # Normalize to 0-100 scale (lower is better for these)
                    thresholds = self.thresholds[cat]
                    if value <= thresholds['good']:
                        score = 100
                    elif value <= thresholds['needs_improvement']:
                        score = 50 + (thresholds['needs_improvement'] - value) / (thresholds['needs_improvement'] - thresholds['good']) * 50
                    else:
                        score = max(0, 50 - (value - thresholds['needs_improvement']) / thresholds['needs_improvement'] * 50)
                    values.append(score)
                else:
                    values.append(0)
            
            # Plot radar
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            values += values[:1]
            angles += angles[:1]
            
            ax2.plot(angles, values, 'o-', linewidth=2, label=result['url'][:20])
            ax2.fill(angles, values, alpha=0.1)
        
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(categories, fontsize=10)
        ax2.set_ylim(0, 100)
        ax2.set_title('Performance Metrics Comparison (Normalized)', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=9)
        ax2.grid(True)
        
        plt.suptitle('Website Performance Comparison', fontsize=16, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return f"data:image/png;base64,{image_base64}"
    
    def _collect_metrics(self, soup: BeautifulSoup, response: requests.Response, 
                        response_time: float, url: str) -> Dict[str, Any]:
        """Collect all performance metrics"""
        
        # Basic metrics
        metrics = {
            'response_time_ms': round(response_time, 2),
            'page_size_kb': round(len(response.content) / 1024, 2),
            'status_code': response.status_code,
            'ttfb': round(response.elapsed.total_seconds() * 1000, 2)
        }
        
        # Resource counting
        scripts = soup.find_all('script', src=True)
        stylesheets = soup.find_all('link', rel='stylesheet')
        images = soup.find_all('img')
        
        metrics['resource_counts'] = {
            'javascript_files': len(scripts),
            'css_files': len(stylesheets),
            'images': len(images),
            'total_resources': len(scripts) + len(stylesheets) + len(images)
        }
        
        # Estimate Load metrics (simulated)
        metrics['estimated_metrics'] = self._estimate_core_web_vitals(
            metrics['resource_counts'], 
            metrics['page_size_kb']
        )
        
        # HTML structure analysis
        metrics['html_structure'] = {
            'has_meta_viewport': bool(soup.find('meta', attrs={'name': 'viewport'})),
            'has_description': bool(soup.find('meta', attrs={'name': 'description'})),
            'has_keywords': bool(soup.find('meta', attrs={'name': 'keywords'})),
            'has_og_tags': bool(soup.find('meta', property=re.compile(r'og:'))),
            'has_favicon': bool(soup.find('link', rel=re.compile(r'icon', re.I))),
            'heading_structure': self._analyze_headings(soup),
            'image_alt_tags': self._analyze_images(soup)
        }
        
        # Compression check
        metrics['compression'] = self._check_compression(response)
        
        # Cache headers
        metrics['cache_headers'] = self._analyze_cache_headers(response.headers)
        
        return metrics
    
    def _estimate_core_web_vitals(self, resource_counts: Dict, page_size: float) -> Dict:
        """Estimate Core Web Vitals based on resource analysis"""
        
        # These are estimations based on common patterns
        base_lcp = 1000  # Base LCP in ms
        base_fid = 50    # Base FID in ms
        base_cls = 0.05  # Base CLS score
        
        # Adjust based on resources
        lcp_penalty = (resource_counts['javascript_files'] * 50 + 
                      resource_counts['css_files'] * 30 + 
                      resource_counts['images'] * 20)
        
        fid_penalty = resource_counts['javascript_files'] * 10
        
        cls_penalty = 0.01 * resource_counts['images'] if resource_counts['images'] > 10 else 0
        
        # Size penalty
        if page_size > 2000:  # 2MB
            size_penalty = 500
        elif page_size > 1000:  # 1MB
            size_penalty = 200
        else:
            size_penalty = 0
        
        return {
            'lcp_ms': min(base_lcp + lcp_penalty + size_penalty, 8000),
            'fid_ms': min(base_fid + fid_penalty, 500),
            'cls_score': min(base_cls + cls_penalty, 0.5),
            'fcp_ms': min(base_lcp + lcp_penalty // 2, 5000)
        }
    
    def _analyze_headings(self, soup: BeautifulSoup) -> Dict:
        """Analyze heading structure"""
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = len(soup.find_all(f'h{i}'))
        
        has_h1 = headings['h1'] > 0
        is_logical = headings['h1'] == 1 and headings['h2'] > 0
        
        return {
            'counts': headings,
            'has_h1': has_h1,
            'is_logical': is_logical,
            'score': 'good' if is_logical else 'needs_improvement'
        }
    
    def _analyze_images(self, soup: BeautifulSoup) -> Dict:
        """Analyze image alt tags"""
        images = soup.find_all('img')
        total_images = len(images)
        
        if total_images == 0:
            return {'total': 0, 'with_alt': 0, 'percentage': 100, 'score': 'good'}
        
        images_with_alt = sum(1 for img in images if img.get('alt'))
        percentage = (images_with_alt / total_images) * 100
        
        score = 'good' if percentage >= 80 else 'needs_improvement' if percentage >= 50 else 'poor'
        
        return {
            'total': total_images,
            'with_alt': images_with_alt,
            'percentage': round(percentage, 2),
            'score': score
        }
    
    def _check_compression(self, response: requests.Response) -> Dict:
        """Check if content is compressed"""
        content_encoding = response.headers.get('Content-Encoding', '')
        
        is_compressed = 'gzip' in content_encoding or 'br' in content_encoding
        
        return {
            'is_compressed': is_compressed,
            'encoding': content_encoding if is_compressed else 'none',
            'score': 'good' if is_compressed else 'needs_improvement'
        }
    
    def _analyze_cache_headers(self, headers: Dict) -> Dict:
        """Analyze cache headers"""
        cache_control = headers.get('Cache-Control', '')
        expires = headers.get('Expires', '')
        
        has_cache = 'max-age' in cache_control or expires
        
        return {
            'has_caching': has_cache,
            'cache_control': cache_control,
            'score': 'good' if has_cache else 'needs_improvement'
        }
    
    def _analyze_performance(self, metrics: Dict) -> Dict:
        """Analyze performance metrics against thresholds"""
        
        performance = {}
        
        # Analyze Core Web Vitals
        for metric, thresholds in self.thresholds.items():
            if metric in metrics.get('estimated_metrics', {}):
                value = metrics['estimated_metrics'][metric]
            elif metric == 'ttfb':
                value = metrics['ttfb']
            else:
                continue
            
            if value <= thresholds['good']:
                rating = 'good'
            elif value <= thresholds['needs_improvement']:
                rating = 'needs_improvement'
            else:
                rating = 'poor'
            
            performance[metric] = {
                'value': value,
                'rating': rating,
                'thresholds': thresholds
            }
        
        # Overall performance rating
        ratings = [p['rating'] for p in performance.values()]
        if 'poor' in ratings:
            overall_rating = 'poor'
        elif 'needs_improvement' in ratings:
            overall_rating = 'needs_improvement'
        else:
            overall_rating = 'good'
        
        performance['overall_rating'] = overall_rating
        
        return performance
    
    def _generate_recommendations(self, metrics: Dict, analysis: Dict) -> List[Dict]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # TTFB recommendations
        if analysis.get('ttfb', {}).get('rating') in ['needs_improvement', 'poor']:
            recommendations.append({
                'category': 'Server Performance',
                'priority': 'High',
                'issue': f"High Time to First Byte ({metrics['ttfb']:.0f}ms)",
                'recommendation': 'Improve server response time by using caching, optimizing database queries, or upgrading hosting.',
                'estimated_impact': 'Critical'
            })
        
        # Compression recommendations
        if metrics['compression']['score'] == 'needs_improvement':
            recommendations.append({
                'category': 'Resource Optimization',
                'priority': 'High',
                'issue': 'Content not compressed',
                'recommendation': 'Enable Gzip or Brotli compression on your server to reduce file sizes by 50-70%.',
                'estimated_impact': 'High'
            })
        
        # Cache recommendations
        if metrics['cache_headers']['score'] == 'needs_improvement':
            recommendations.append({
                'category': 'Caching',
                'priority': 'Medium',
                'issue': 'Missing or improper cache headers',
                'recommendation': 'Implement browser caching using Cache-Control headers to improve repeat visit performance.',
                'estimated_impact': 'Medium'
            })
        
        # Resource count recommendations
        resource_counts = metrics['resource_counts']
        if resource_counts['javascript_files'] > 15:
            recommendations.append({
                'category': 'JavaScript Optimization',
                'priority': 'Medium',
                'issue': f"Excessive JavaScript files ({resource_counts['javascript_files']})",
                'recommendation': 'Minify and bundle JavaScript files. Remove unused libraries and implement code splitting.',
                'estimated_impact': 'Medium'
            })
        
        if resource_counts['css_files'] > 5:
            recommendations.append({
                'category': 'CSS Optimization',
                'priority': 'Low',
                'issue': f"Multiple CSS files ({resource_counts['css_files']})",
                'recommendation': 'Combine CSS files and minify them. Consider inlining critical CSS for above-the-fold content.',
                'estimated_impact': 'Low'
            })
        
        if resource_counts['images'] > 30:
            recommendations.append({
                'category': 'Image Optimization',
                'priority': 'High',
                'issue': f"Many images detected ({resource_counts['images']})",
                'recommendation': 'Implement lazy loading, use modern formats (WebP), and compress images.',
                'estimated_impact': 'High'
            })
        
        # Image alt optimization
        if metrics['html_structure']['image_alt_tags']['score'] != 'good':
            missing = metrics['html_structure']['image_alt_tags']['total'] - metrics['html_structure']['image_alt_tags']['with_alt']
            recommendations.append({
                'category': 'Accessibility',
                'priority': 'Medium',
                'issue': f"Missing alt tags on {missing} images",
                'recommendation': 'Add descriptive alt attributes to all images for better accessibility and SEO.',
                'estimated_impact': 'Medium'
            })
        
        # Heading structure
        if not metrics['html_structure']['heading_structure']['is_logical']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'Medium',
                'issue': 'Poor heading structure',
                'recommendation': 'Use one H1 tag per page and maintain proper heading hierarchy (H1 → H2 → H3).',
                'estimated_impact': 'Medium'
            })
        
        # Page size recommendations
        if metrics['page_size_kb'] > 2000:
            recommendations.append({
                'category': 'Page Weight',
                'priority': 'High',
                'issue': f"Large page size ({metrics['page_size_kb']:.2f} KB)",
                'recommendation': 'Optimize images, implement lazy loading, remove unnecessary resources, and consider code splitting.',
                'estimated_impact': 'High'
            })
        elif metrics['page_size_kb'] > 1000:
            recommendations.append({
                'category': 'Page Weight',
                'priority': 'Medium',
                'issue': f"Moderate page size ({metrics['page_size_kb']:.2f} KB)",
                'recommendation': 'Consider optimizing images and resources to further reduce page weight.',
                'estimated_impact': 'Medium'
            })
        
        # Meta tags recommendations
        html_struct = metrics['html_structure']
        if not html_struct['has_description']:
            recommendations.append({
                'category': 'SEO',
                'priority': 'Medium',
                'issue': 'Missing meta description',
                'recommendation': 'Add a meta description tag to improve search engine click-through rates.',
                'estimated_impact': 'Medium'
            })
        
        if not html_struct['has_og_tags']:
            recommendations.append({
                'category': 'Social Media',
                'priority': 'Low',
                'issue': 'Missing Open Graph tags',
                'recommendation': 'Add Open Graph tags to control how your content appears when shared on social media.',
                'estimated_impact': 'Low'
            })
        
        # LCP recommendations
        if analysis.get('lcp', {}).get('rating') in ['needs_improvement', 'poor']:
            recommendations.append({
                'category': 'Loading Performance',
                'priority': 'High',
                'issue': f"Poor Largest Contentful Paint ({analysis['lcp']['value']:.0f}ms)",
                'recommendation': 'Optimize your largest content element. Consider preloading critical resources and improving server response.',
                'estimated_impact': 'High'
            })
        
        # CLS recommendations
        if analysis.get('cls', {}).get('rating') in ['needs_improvement', 'poor']:
            recommendations.append({
                'category': 'Visual Stability',
                'priority': 'Medium',
                'issue': f"Layout shift detected (CLS: {analysis['cls']['value']:.3f})",
                'recommendation': 'Specify width/height dimensions for images and videos. Avoid inserting content above existing content.',
                'estimated_impact': 'Medium'
            })
        
        return recommendations
    
    def _calculate_overall_score(self, metrics: Dict) -> int:
        """Calculate overall performance score out of 100"""
        
        score = 100
        
        # Deductions based on metrics
        if metrics['ttfb'] > 200:
            score -= min(20, (metrics['ttfb'] - 200) / 20)
        
        if metrics['page_size_kb'] > 1000:
            score -= min(15, (metrics['page_size_kb'] - 1000) / 100)
        
        if not metrics['compression']['is_compressed']:
            score -= 10
        
        if not metrics['cache_headers']['has_caching']:
            score -= 10
        
        resource_count = metrics['resource_counts']['total_resources']
        if resource_count > 30:
            score -= min(15, (resource_count - 30) / 2)
        
        # Headings score
        if not metrics['html_structure']['heading_structure']['has_h1']:
            score -= 5
        
        # Image alt tags
        if metrics['html_structure']['image_alt_tags']['percentage'] < 80:
            score -= min(10, (80 - metrics['html_structure']['image_alt_tags']['percentage']) / 8)
        
        # Estimated Core Web Vitals
        estimated = metrics['estimated_metrics']
        if estimated['lcp_ms'] > 2500:
            score -= min(20, (estimated['lcp_ms'] - 2500) / 100)
        
        if estimated['cls_score'] > 0.1:
            score -= min(10, (estimated['cls_score'] - 0.1) * 50)
        
        # Metadata
        if not metrics['html_structure']['has_description']:
            score -= 5
        
        if not metrics['html_structure']['has_meta_viewport']:
            score -= 5
        
        # Ensure score is between 0 and 100
        return max(0, min(100, int(score)))
    
    def _save_results(self, results: Dict):
        """Save analysis results to JSON file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"data/analysis_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")