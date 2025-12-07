"""
Retrieval Context Module
Extracts Module 4 temporal analysis data and formats as context for LLM
"""

import sys
from pathlib import Path
from pymongo import MongoClient
from datetime import datetime
import json

class RetrievalContext:
    """Retrieves and formats temporal analysis data for newsletter generation"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.mongo_client = MongoClient('localhost', 27017)
        self.db = self.mongo_client['gen_eezes']
    
    def get_latest_trends(self):
        """
        Retrieve latest temporal analysis and format as rich context
        
        Returns:
            dict: Formatted context for LLM with all trend information
        """
        # Get latest temporal analysis
        analysis = self.db['temporal_analysis_real'].find_one(
            sort=[('timestamp', -1)]
        )
        
        if not analysis:
            raise ValueError("No temporal analysis found. Run analyze_real_trends.py first.")
        
        # Extract and format key data
        context = {
            'analysis_date': analysis['timestamp'].strftime('%B %d, %Y'),
            'week_ending': analysis['timestamp'].strftime('%Y-%m-%d'),
            'summary_stats': {
                'total_keywords': analysis.get('keywords_analyzed', 0),
                'clusters_tracked': analysis.get('clusters_analyzed', 0),
                'weeks_analyzed': analysis.get('weeks_analyzed', 52)
            },
            'keyword_shifts': self._format_keyword_shifts(analysis.get('keyword_shifts', {})),
            'cluster_insights': self._format_cluster_insights(analysis.get('cluster_stats', {})),
            'narrative': self._generate_narrative(analysis)
        }
        
        return context
    
    def _format_keyword_shifts(self, keyword_shifts):
        """Format keyword shifts for readability"""
        
        rising = []
        falling = []
        stable = []
        
        for keyword, data in keyword_shifts.items():
            entry = {
                'keyword': keyword.upper(),
                'start': data.get('start_frequency', 0),
                'end': data.get('end_frequency', 0),
                'change': f"{data.get('percent_change', 0):+.1f}%",
                'direction': data.get('trend_direction', 'UNKNOWN')
            }
            
            if data.get('trend_direction') == 'RISING':
                rising.append(entry)
            elif data.get('trend_direction') == 'FALLING':
                falling.append(entry)
            else:
                stable.append(entry)
        
        # Sort by magnitude of change
        rising_sorted = sorted(rising, key=lambda x: float(x['change'].rstrip('%')), reverse=True)
        falling_sorted = sorted(falling, key=lambda x: float(x['change'].rstrip('%')))
        
        return {
            'rising_keywords': rising_sorted[:10],  # Top 10 rising
            'falling_keywords': falling_sorted[:10],  # Top 10 falling
            'stable_keywords': stable
        }
    
    def _format_cluster_insights(self, cluster_stats):
        """Format cluster drift analysis for narrative"""
        
        insights = {}
        
        for cluster_name, stats in cluster_stats.items():
            insights[cluster_name] = {
                'name': cluster_name.replace('_', ' ').title(),
                'drift_severity': stats.get('drift_severity', 'UNKNOWN'),
                'size_change': f"{stats.get('size_change_percent', 0):+.1f}%",
                'drift_magnitude': f"{stats.get('drift_magnitude', 0):.1f}/100",
                'interpretation': self._interpret_drift(
                    cluster_name,
                    stats.get('drift_severity'),
                    stats.get('size_change_percent'),
                )
            }
        
        return insights
    
    def _interpret_drift(self, cluster_name, severity, size_change):
        """Generate interpretation of cluster drift"""
        
        interpretations = {
            ('ai_llm', 'EXTREME'): "Explosive growth in AI/LLM interest with increasing topic diversity",
            ('frontend', 'MINIMAL'): "Web technologies remain stable and reliable - foundational",
            ('devops', 'EXTREME'): "Sharp decline in DevOps focus - shift to managed services",
        }
        
        key = (cluster_name, severity)
        if key in interpretations:
            return interpretations[key]
        
        if size_change > 50:
            return f"Significant growth in {cluster_name} cluster"
        elif size_change < -50:
            return f"Significant decline in {cluster_name} cluster"
        else:
            return f"{cluster_name} cluster remains relatively stable"
    
    def _generate_narrative(self, analysis):
        """Generate high-level narrative about trends"""
        
        keyword_shifts = analysis.get('keyword_shifts', {})
        
        # Count trend types
        rising_count = sum(1 for d in keyword_shifts.values() if d.get('trend_direction') == 'RISING')
        falling_count = sum(1 for d in keyword_shifts.values() if d.get('trend_direction') == 'FALLING')
        stable_count = sum(1 for d in keyword_shifts.values() if d.get('trend_direction') == 'STABLE')
        
        # Identify top movers
        top_rising = max(
            ((k, v) for k, v in keyword_shifts.items() if v.get('trend_direction') == 'RISING'),
            key=lambda x: x[1].get('percent_change', 0),
            default=None
        )
        
        top_falling = min(
            ((k, v) for k, v in keyword_shifts.items() if v.get('trend_direction') == 'FALLING'),
            key=lambda x: x[1].get('percent_change', 0),
            default=None
        )
        
        narrative = f"""
This week's analysis reveals significant shifts in technology focus across our ecosystem:

TREND SUMMARY:
- {rising_count} keywords showing growth trends
- {falling_count} keywords showing decline trends  
- {stable_count} keywords remaining stable

KEY OBSERVATIONS:
"""
        
        if top_rising:
            keyword, data = top_rising
            narrative += f"\n- {keyword.upper()} is the most explosive growth area ({data.get('percent_change', 0):+.1f}%)"
        
        if top_falling:
            keyword, data = top_falling
            narrative += f"\n- {keyword.upper()} shows the steepest decline ({data.get('percent_change', 0):.1f}%)"
        
        narrative += "\n- These patterns indicate a fundamental shift in developer priorities and technology adoption"
        
        return narrative.strip()
    
    def get_formatted_context_for_llm(self):
        """
        Get context formatted specifically for LLM consumption
        
        Returns:
            str: Formatted context ready to send to Gemini
        """
        context = self.get_latest_trends()
        
        formatted = f"""
=== WEEKLY TECH TRENDS ANALYSIS ===
Analysis Date: {context['analysis_date']}
Period: {context['week_ending']}

SUMMARY STATISTICS:
- Total Keywords Analyzed: {context['summary_stats']['total_keywords']}
- Clusters Tracked: {context['summary_stats']['clusters_tracked']}
- Time Period: {context['summary_stats']['weeks_analyzed']} weeks

TOP RISING KEYWORDS:
"""
        
        for i, kw in enumerate(context['keyword_shifts']['rising_keywords'][:5], 1):
            formatted += f"\n{i}. {kw['keyword']}: {kw['start']} → {kw['end']} ({kw['change']})"
        
        formatted += "\n\nTOP FALLING KEYWORDS:"
        
        for i, kw in enumerate(context['keyword_shifts']['falling_keywords'][:5], 1):
            formatted += f"\n{i}. {kw['keyword']}: {kw['start']} → {kw['end']} ({kw['change']})"
        
        formatted += "\n\nCLUSTER INSIGHTS:"
        
        for cluster_name, insight in context['cluster_insights'].items():
            formatted += f"\n- {insight['name']}: {insight['drift_severity']} DRIFT"
            formatted += f"\n  Size Change: {insight['size_change']}"
            formatted += f"\n  Insight: {insight['interpretation']}"
        
        formatted += f"\n\nOVERALL NARRATIVE:\n{context['narrative']}"
        
        return formatted, context
    
    def get_context_dict(self):
        """Get context as dictionary (easier for JSON serialization)"""
        context = self.get_latest_trends()
        return context


def main():
    """Test retrieval context"""
    
    print("\n" + "="*80)
    print("RETRIEVAL CONTEXT - MODULE 4 DATA EXTRACTION")
    print("="*80 + "\n")
    
    try:
        retrieval = RetrievalContext()
        
        # Get formatted context
        formatted_context, context_dict = retrieval.get_formatted_context_for_llm()
        
        print("✅ Successfully retrieved temporal analysis data")
        print("\nFORMATTED CONTEXT FOR LLM:")
        print("─" * 80)
        print(formatted_context)
        
        print("\n" + "─" * 80)
        print("✅ Context ready for Gemini 2.5 newsletter generation")
        print("="*80 + "\n")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\nPlease run temporal analysis first:")
        print("  python backfill_historical.py")
        print("  python snapshot_aggregator.py")
        print("  python analyze_real_trends.py")


if __name__ == '__main__':
    main()
