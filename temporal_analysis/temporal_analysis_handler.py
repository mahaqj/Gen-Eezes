"""
Temporal Analysis Handler Module
Detects trends, keyword shifts, and cluster drift over time
"""

import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')


class TemporalAnalysisHandler:
    """Handles temporal analysis of clusters and keywords"""
    
    def __init__(self):
        """Initialize temporal analysis handler"""
        self.trend_history = {}
        self.keyword_history = {}
        self.cluster_history = {}
        
    def analyze_keyword_shifts(self, keyword_timeline: Dict[str, List[Tuple[datetime, int]]]) -> Dict:
        """
        Analyze keyword frequency shifts over time
        
        Args:
            keyword_timeline: Dict mapping keywords to list of (date, frequency) tuples
            
        Returns:
            Dictionary with keyword shift analysis
        """
        print("\n📊 Analyzing Keyword Frequency Shifts...")
        keyword_shifts = {}
        
        for keyword, timeline in keyword_timeline.items():
            if len(timeline) < 2:
                continue
            
            # Sort by date
            sorted_timeline = sorted(timeline, key=lambda x: x[0])
            frequencies = [freq for _, freq in sorted_timeline]
            dates = [date for date, _ in sorted_timeline]
            
            # Calculate shifts
            shift_data = {
                'keyword': keyword,
                'timeline': sorted_timeline,
                'current_frequency': frequencies[-1],
                'previous_frequency': frequencies[-2] if len(frequencies) > 1 else 0,
                'change': frequencies[-1] - (frequencies[-2] if len(frequencies) > 1 else 0),
                'percent_change': self._calculate_percent_change(
                    frequencies[-2] if len(frequencies) > 1 else 1,
                    frequencies[-1]
                ),
                'trend': self._detect_simple_trend(frequencies[-3:]),
                'history': frequencies,
                'dates': dates
            }
            
            keyword_shifts[keyword] = shift_data
        
        print(f"  ✓ Analyzed {len(keyword_shifts)} keywords")
        return keyword_shifts
    
    def _calculate_percent_change(self, old_value: float, new_value: float) -> float:
        """Calculate percentage change"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return ((new_value - old_value) / old_value) * 100
    
    def _detect_simple_trend(self, recent_values: List[int]) -> str:
        """Detect trend from recent values"""
        if len(recent_values) < 2:
            return "STABLE"
        
        # Count ups and downs
        ups = sum(1 for i in range(1, len(recent_values)) if recent_values[i] > recent_values[i-1])
        downs = sum(1 for i in range(1, len(recent_values)) if recent_values[i] < recent_values[i-1])
        
        if ups > downs and ups >= len(recent_values) - 1:
            return "RISING"
        elif downs > ups and downs >= len(recent_values) - 1:
            return "FALLING"
        else:
            return "STABLE"
    
    def detect_cluster_drift(self, cluster_timeline: Dict[str, List[Dict]]) -> Dict:
        """
        Detect cluster drift (changes in size, centroid, cohesion)
        
        Args:
            cluster_timeline: Dict mapping cluster_id to list of cluster state dicts over time
                             Each dict has: size, centroid, std_dev, keywords, date
            
        Returns:
            Dictionary with drift analysis
        """
        print("🌊 Detecting Cluster Drift...")
        drift_analysis = {}
        
        for cluster_id, timeline in cluster_timeline.items():
            if len(timeline) < 2:
                continue
            
            # Sort by date
            sorted_timeline = sorted(timeline, key=lambda x: x.get('date', datetime.now()))
            
            # Extract metrics over time
            sizes = [cluster['size'] for cluster in sorted_timeline]
            std_devs = [cluster.get('std_dev', 1.0) for cluster in sorted_timeline]
            dates = [cluster.get('date', datetime.now()) for cluster in sorted_timeline]
            
            # Calculate drift metrics
            size_change = sizes[-1] - sizes[-2]
            size_percent_change = self._calculate_percent_change(sizes[-2], sizes[-1])
            
            avg_std_dev = np.mean(std_devs)
            std_dev_change = std_devs[-1] - std_devs[-2]
            
            # Drift magnitude (how much cluster is changing)
            drift_magnitude = self._calculate_drift_magnitude(size_change, std_dev_change)
            
            drift_analysis[cluster_id] = {
                'cluster_id': cluster_id,
                'timeline': sorted_timeline,
                'size_history': sizes,
                'std_dev_history': std_devs,
                'dates': dates,
                'current_size': sizes[-1],
                'previous_size': sizes[-2],
                'size_change': size_change,
                'size_percent_change': size_percent_change,
                'avg_cohesion': 1 / avg_std_dev,  # Lower std_dev = higher cohesion
                'std_dev_change': std_dev_change,
                'drift_magnitude': drift_magnitude,
                'drift_severity': self._classify_drift_severity(drift_magnitude)
            }
        
        print(f"  ✓ Analyzed drift for {len(drift_analysis)} clusters")
        return drift_analysis
    
    def _calculate_drift_magnitude(self, size_change: int, std_dev_change: float) -> float:
        """Calculate overall drift magnitude (0-100)"""
        # Normalize: size change is at most dataset size, std_dev change is at most 3
        normalized_size_drift = abs(size_change) / max(1, size_change + 10) * 50
        normalized_std_drift = abs(std_dev_change) / 3 * 50
        
        return min(100, normalized_size_drift + normalized_std_drift)
    
    def _classify_drift_severity(self, magnitude: float) -> str:
        """Classify drift severity"""
        if magnitude < 10:
            return "MINIMAL"
        elif magnitude < 25:
            return "LOW"
        elif magnitude < 50:
            return "MEDIUM"
        elif magnitude < 75:
            return "HIGH"
        else:
            return "EXTREME"
    
    def model_time_series(self, metric_timeline: List[Tuple[datetime, float]]) -> Dict:
        """
        Model time series data and detect trends
        
        Args:
            metric_timeline: List of (date, value) tuples
            
        Returns:
            Dictionary with time series analysis and trend prediction
        """
        if len(metric_timeline) < 2:
            return {'error': 'Insufficient data for time series modeling'}
        
        # Sort by date
        sorted_timeline = sorted(metric_timeline, key=lambda x: x[0])
        dates = np.array([i for i in range(len(sorted_timeline))])  # Use index as time
        values = np.array([val for _, val in sorted_timeline])
        
        # Fit linear regression
        X = dates.reshape(-1, 1)
        y = values.reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Calculate trend metrics
        slope = float(model.coef_[0][0])
        intercept = float(model.intercept_[0])
        r_squared = model.score(X, y)
        
        # Predict next value
        next_index = len(sorted_timeline)
        next_prediction = float(model.predict([[next_index]])[0][0])
        
        # Detect trend direction
        trend_direction = "RISING" if slope > 0 else ("FALLING" if slope < 0 else "STABLE")
        trend_strength = min(1.0, abs(slope) / max(1, np.mean(values)))
        
        # Calculate residuals (how well model fits)
        predictions = model.predict(X)
        residuals = values - predictions.flatten()
        rmse = np.sqrt(np.mean(residuals ** 2))
        
        return {
            'timeline': sorted_timeline,
            'values': values.tolist(),
            'slope': slope,
            'intercept': intercept,
            'r_squared': r_squared,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'next_prediction': next_prediction,
            'rmse': rmse,
            'model_quality': 'STRONG' if r_squared > 0.7 else ('MODERATE' if r_squared > 0.4 else 'WEAK')
        }
    
    def label_trends(self, trend_analyses: Dict) -> Dict:
        """
        Label trends as Rising, Falling, or Stable
        
        Args:
            trend_analyses: Dictionary of trend data for different metrics
            
        Returns:
            Dictionary with labeled trends
        """
        print("🏷️  Labeling Trends...")
        labeled_trends = {}
        
        for metric_name, trend_data in trend_analyses.items():
            if isinstance(trend_data, dict) and 'timeline' in trend_data:
                # This is time series data
                direction = trend_data.get('trend_direction', 'STABLE')
                strength = trend_data.get('trend_strength', 0)
                
                label = {
                    'metric': metric_name,
                    'direction': direction,
                    'strength': strength,
                    'confidence': min(1.0, trend_data.get('r_squared', 0)),
                    'label_text': self._generate_trend_label(direction, strength),
                    'emoji': self._get_trend_emoji(direction),
                    'forecast': trend_data.get('next_prediction'),
                    'model_quality': trend_data.get('model_quality')
                }
                
                labeled_trends[metric_name] = label
        
        print(f"  ✓ Labeled {len(labeled_trends)} trends")
        return labeled_trends
    
    def _generate_trend_label(self, direction: str, strength: float) -> str:
        """Generate human-readable trend label"""
        if direction == "RISING":
            if strength > 0.7:
                return "STRONG RISING TREND"
            else:
                return "MODERATE RISING TREND"
        elif direction == "FALLING":
            if strength > 0.7:
                return "STRONG FALLING TREND"
            else:
                return "MODERATE FALLING TREND"
        else:
            return "STABLE TREND"
    
    def _get_trend_emoji(self, direction: str) -> str:
        """Get emoji for trend direction"""
        if direction == "RISING":
            return "📈"
        elif direction == "FALLING":
            return "📉"
        else:
            return "→"
    
    def generate_trend_report(self, keyword_shifts: Dict, cluster_drifts: Dict, 
                             trend_labels: Dict) -> str:
        """
        Generate a human-readable trend report
        
        Args:
            keyword_shifts: Keyword shift analysis
            cluster_drifts: Cluster drift analysis
            trend_labels: Labeled trends
            
        Returns:
            Formatted trend report string
        """
        report = "\n" + "="*80 + "\n"
        report += "TEMPORAL TREND ANALYSIS REPORT\n"
        report += "="*80 + "\n"
        
        # Top rising keywords
        report += "\n🔥 TOP RISING KEYWORDS:\n"
        report += "-" * 80 + "\n"
        rising_keywords = sorted(
            [(k, v) for k, v in keyword_shifts.items() if v['trend'] == 'RISING'],
            key=lambda x: x[1]['percent_change'],
            reverse=True
        )[:5]
        
        for keyword, data in rising_keywords:
            report += f"  📍 {keyword.upper()}\n"
            report += f"     Current: {data['current_frequency']} | "
            report += f"Previous: {data['previous_frequency']} | "
            report += f"Change: +{data['percent_change']:.1f}%\n"
        
        # Top falling keywords
        report += "\n❄️  TOP FALLING KEYWORDS:\n"
        report += "-" * 80 + "\n"
        falling_keywords = sorted(
            [(k, v) for k, v in keyword_shifts.items() if v['trend'] == 'FALLING'],
            key=lambda x: x[1]['percent_change'],
        )[:5]
        
        for keyword, data in falling_keywords:
            report += f"  📍 {keyword.upper()}\n"
            report += f"     Current: {data['current_frequency']} | "
            report += f"Previous: {data['previous_frequency']} | "
            report += f"Change: {data['percent_change']:.1f}%\n"
        
        # Cluster drift analysis
        report += "\n🌊 CLUSTER DRIFT ANALYSIS:\n"
        report += "-" * 80 + "\n"
        
        high_drift = sorted(
            cluster_drifts.items(),
            key=lambda x: x[1]['drift_magnitude'],
            reverse=True
        )[:3]
        
        for cluster_id, drift_data in high_drift:
            report += f"  Cluster {cluster_id}: {drift_data['drift_severity']} DRIFT\n"
            report += f"     Size: {drift_data['previous_size']} → {drift_data['current_size']} "
            report += f"({drift_data['size_percent_change']:+.1f}%)\n"
            report += f"     Magnitude: {drift_data['drift_magnitude']:.1f}/100\n"
        
        # Trend labels
        report += "\n📊 OVERALL TREND SUMMARY:\n"
        report += "-" * 80 + "\n"
        for metric, label_data in trend_labels.items():
            report += f"  {label_data['emoji']} {metric}: {label_data['label_text']}\n"
            report += f"     Strength: {label_data['strength']:.2f} | "
            report += f"Confidence: {label_data['confidence']:.2f}\n"
        
        report += "\n" + "="*80 + "\n"
        
        return report
