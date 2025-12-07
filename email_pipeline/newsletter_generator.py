"""
Newsletter Generator using Google Gemini 2.5 API

Converts trend data from Module 4 into compelling newsletter content.
Uses textual context descriptions (not raw embeddings) for LLM prompting.

Author: Gen-Eezes Team
Date: December 2025
"""

import os
import json
import logging
from typing import Dict, List, Optional
import google.generativeai as genai
from datetime import datetime

logger = logging.getLogger(__name__)


class NewsletterGenerator:
    """
    Generates newsletter content using Google Gemini 2.5 API.
    
    Takes trend data from Module 4 (keyword shifts, cluster insights)
    and transforms it into engaging newsletter HTML/text.
    
    Key Insight: Gemini 2.5 doesn't need raw embedding vectors.
    Instead, we provide semantic descriptions of trends (which are MORE
    interpretable and flexible than vectors). This is actually BETTER
    than trying to pass embeddings directly.
    """
    
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        """
        Initialize Gemini 2.5 API client.
        
        Args:
            api_key: Google Gemini API key. If None, uses GEMINI_API_KEY env var.
            model: Model to use (default: gemini-2.5-flash for speed, can use gemini-2.5-pro for quality)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not provided. Set GEMINI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        logger.info(f"Initialized Gemini 2.5 with model: {model}")
    
    def generate_newsletter(
        self,
        context: Dict,
        recipient_name: str = "Tech Enthusiast",
        tone: str = "professional-friendly"
    ) -> Dict[str, str]:
        """
        Generate newsletter content from trend data.
        
        Args:
            context: Dictionary with keys:
                - 'keyword_shifts': List of trending keywords with changes
                - 'cluster_insights': Cluster drift and evolution info
                - 'narrative': High-level summary of tech trends
                - 'timestamp': When analysis was generated
            
            recipient_name: Name of the person receiving the newsletter
            tone: Style of writing ("professional-friendly", "technical", "casual")
        
        Returns:
            Dictionary with keys:
            - 'html': Full HTML email body
            - 'text': Plain text version
            - 'subject': Email subject line
            - 'preview': Text preview (first 150 chars)
        """
        
        # Build the prompt for Gemini
        prompt = self._build_prompt(context, recipient_name, tone)
        
        logger.info(f"Generating newsletter for {recipient_name} with tone: {tone}")
        
        try:
            # Call Gemini 2.5 API
            response = self.model.generate_content(prompt)
            
            # Parse the response
            newsletter_content = response.text
            
            # Extract structure (Gemini should provide HTML, Text, Subject, Preview)
            html_content = self._extract_section(newsletter_content, "HTML")
            text_content = self._extract_section(newsletter_content, "TEXT")
            subject_line = self._extract_section(newsletter_content, "SUBJECT")
            preview_text = self._extract_section(newsletter_content, "PREVIEW")
            
            result = {
                'html': html_content,
                'text': text_content,
                'subject': subject_line,
                'preview': preview_text,
                'model': self.model_name,
                'generated_at': datetime.now().isoformat(),
                'recipient': recipient_name
            }
            
            logger.info(f"Newsletter generated successfully for {recipient_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating newsletter: {str(e)}")
            raise
    
    def _build_prompt(self, context: Dict, recipient_name: str, tone: str) -> str:
        """
        Build the prompt to send to Gemini 2.5.
        
        This is where we solve the embedding compatibility concern:
        Instead of trying to pass 384-dimensional vectors, we provide
        textual semantic descriptions of what the embeddings showed.
        This is MORE interpretable and works better with LLMs!
        """
        
        keyword_shifts = context.get('keyword_shifts', {})
        cluster_insights = context.get('cluster_insights', {})
        narrative = context.get('narrative', "")
        timestamp = context.get('timestamp', "")
        
        # Format keyword data for the prompt
        rising_keywords = []
        falling_keywords = []
        
        for keyword, data in keyword_shifts.items():
            percent_change = data.get('percent_change', 0)
            # Ensure it's a float
            if isinstance(percent_change, str):
                percent_change = float(percent_change.rstrip('%').lstrip('+'))
            
            start_freq = data.get('start_freq', 0)
            end_freq = data.get('end_freq', 0)
            
            if data.get('direction') == 'RISING':
                rising_keywords.append(
                    f"- {keyword}: +{percent_change:.1f}% "
                    f"(from {start_freq} to {end_freq} mentions)"
                )
            elif data.get('direction') == 'FALLING':
                falling_keywords.append(
                    f"- {keyword}: {percent_change:.1f}% "
                    f"(from {start_freq} to {end_freq} mentions)"
                )
        
        # Format cluster data
        cluster_summary = ""
        for cluster, stats in cluster_insights.items():
            size_change = stats.get('size_change_percent', 0)
            drift_magnitude = stats.get('drift_magnitude', 0)
            
            # Ensure they're floats
            if isinstance(size_change, str):
                size_change = float(size_change.rstrip('%').lstrip('+'))
            if isinstance(drift_magnitude, str):
                # Handle "126.0/100" format
                try:
                    if '/' in str(drift_magnitude):
                        drift_magnitude = float(str(drift_magnitude).split('/')[0])
                    else:
                        drift_magnitude = float(str(drift_magnitude).rstrip('%').lstrip('+'))
                except:
                    drift_magnitude = 0.0
            
            cluster_summary += f"""
- {cluster}: Drift Severity: {stats.get('drift_severity', 'UNKNOWN')}
  Size Change: {float(size_change):.1f}%
  Magnitude: {float(drift_magnitude):.3f}
"""
        
        prompt = f"""You are a tech industry analyst writing an engaging weekly newsletter.

CONTEXT DATA FROM THIS WEEK'S ANALYSIS:
============================================
Analysis Date: {timestamp}
Recipient: {recipient_name}

TRENDING TECHNOLOGIES (Rising):
{chr(10).join(rising_keywords) if rising_keywords else "No major rising trends detected"}

DECLINING TECHNOLOGIES (Falling):
{chr(10).join(falling_keywords) if falling_keywords else "No major declining trends"}

TECHNOLOGY CLUSTERS & EVOLUTION:
{cluster_summary}

HIGH-LEVEL NARRATIVE:
{narrative}

YOUR TASK:
============================================
Write a professional yet friendly tech newsletter addressing {recipient_name} personally.

Include sections:
1. Opening (personalized greeting to {recipient_name} mentioning key trends)
2. Top 3 Rising Technologies (with brief explanations of why they're trending)
3. Top 3 Declining Technologies (with context on market shifts)
4. Technology Clusters (how different tech areas are evolving together)
5. Key Takeaway (what developers/tech leaders should know)
6. Closing (invitation to explore further)

CRITICAL BRANDING & DESIGN REQUIREMENTS:
- Start with personalized greeting: "Hi {recipient_name},"
- Main header: "The Gen-Eezes Newsletter" with BRAND PINK background (#c93e8b)
- ALL TEXT COLOR: Pure black (#000000) for maximum readability
- Footer/signature section: "The Gen-Eezes Team" with brand pink (#c93e8b) background and pink heart emojis (💕💖💗)
- Closing text: "Want to dive deeper into specific trends or have questions? Just hit reply! Best regards, The Gen-Eezes Team 💕💖💗"
- Clean, professional design with brand pink accent color only
- All text in black for contrast and readability
- Generous padding and spacing for readability

Format your response EXACTLY as follows (use these headers):

===HTML===
[Full HTML email body - professional newsletter with brand pink (#c93e8b) header "The Gen-Eezes Newsletter", brand pink footer, black text throughout, heart emojis, NO other colors]

===TEXT===
[Plain text version with Gen-Eezes Team signature and heart emojis, personalized to {recipient_name}]

===SUBJECT===
[Catchy email subject line personalized to {recipient_name}]

===PREVIEW===
[First 150 characters of email preview text]

Make the content engaging, informative, and actionable. Use the data provided to back up claims.
Focus on WHY these trends matter to developers and tech professionals.
"""
        
        return prompt
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """
        Extract a specific section from Gemini's response.
        
        Looks for headers like ===HTML=== and extracts everything until next ===SECTION===
        """
        section_marker = f"==={section_name}==="
        
        if section_marker not in content:
            logger.warning(f"Section {section_name} not found in response")
            return ""
        
        start_idx = content.find(section_marker) + len(section_marker)
        
        # Find next section marker or end of content
        next_marker_idx = -1
        for other_section in ["HTML", "TEXT", "SUBJECT", "PREVIEW"]:
            if other_section == section_name:
                continue
            marker = f"==={other_section}==="
            idx = content.find(marker, start_idx)
            if idx != -1 and (next_marker_idx == -1 or idx < next_marker_idx):
                next_marker_idx = idx
        
        if next_marker_idx == -1:
            end_idx = len(content)
        else:
            end_idx = next_marker_idx
        
        extracted = content[start_idx:end_idx].strip()
        return extracted
    
    def generate_batch(
        self,
        contexts: List[Dict],
        recipient_names: List[str],
        tone: str = "professional-friendly"
    ) -> List[Dict[str, str]]:
        """
        Generate newsletters for multiple recipients.
        
        Args:
            contexts: List of context dictionaries
            recipient_names: List of recipient names
            tone: Writing tone for all newsletters
        
        Returns:
            List of newsletter dictionaries
        """
        newsletters = []
        for context, name in zip(contexts, recipient_names):
            try:
                newsletter = self.generate_newsletter(context, name, tone)
                newsletters.append(newsletter)
            except Exception as e:
                logger.error(f"Failed to generate newsletter for {name}: {str(e)}")
                continue
        
        return newsletters
    
    def preview_newsletter(self, newsletter: Dict[str, str]) -> str:
        """
        Generate a preview of the newsletter in terminal-friendly format.
        
        Useful for reviewing before sending.
        """
        preview = f"""
================================================================================
                        NEWSLETTER PREVIEW
================================================================================

RECIPIENT: {newsletter.get('recipient', 'Unknown')}
SUBJECT: {newsletter.get('subject', 'No Subject')}
GENERATED AT: {newsletter.get('generated_at', 'Unknown')}
MODEL: {newsletter.get('model', 'Unknown')}

PREVIEW TEXT:
{newsletter.get('preview', 'No preview available')}

TEXT VERSION:
----
{newsletter.get('text', 'No text version')}

================================================================================
HTML VERSION:
----
{newsletter.get('html', 'No HTML version')}

================================================================================
"""
        return preview


def main():
    """Test the newsletter generator with sample data."""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Sample context (would come from RetrievalContext in production)
    sample_context = {
        'keyword_shifts': {
            'embedding': {'direction': 'RISING', 'start_freq': 10, 'end_freq': 70, 'percent_change': 600},
            'transformer': {'direction': 'RISING', 'start_freq': 15, 'end_freq': 90, 'percent_change': 500},
            'llm': {'direction': 'RISING', 'start_freq': 20, 'end_freq': 90, 'percent_change': 350},
            'kubernetes': {'direction': 'FALLING', 'start_freq': 25, 'end_freq': 0, 'percent_change': -100},
            'docker': {'direction': 'FALLING', 'start_freq': 22, 'end_freq': 0, 'percent_change': -100},
        },
        'cluster_insights': {
            'AI/LLM Cluster': {'drift_severity': 'EXTREME', 'size_change_percent': 93.3, 'drift_magnitude': 0.8},
            'Frontend Cluster': {'drift_severity': 'MINIMAL', 'size_change_percent': -11, 'drift_magnitude': 0.05},
            'DevOps Cluster': {'drift_severity': 'EXTREME', 'size_change_percent': -66.7, 'drift_magnitude': 0.75},
        },
        'narrative': (
            'The tech industry is experiencing a massive shift toward AI/LLM technologies. '
            'Traditional DevOps tools are declining in relevance, while embedding and transformer '
            'technologies are exploding in adoption. Frontend development remains relatively stable '
            'despite some minor fluctuations.'
        ),
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Initialize generator
        generator = NewsletterGenerator()
        
        print("\n" + "="*80)
        print("GENERATING NEWSLETTER WITH GEMINI 2.5...")
        print("="*80 + "\n")
        
        # Generate newsletter
        newsletter = generator.generate_newsletter(
            context=sample_context,
            recipient_name="Ahmed Hassan",
            tone="professional-friendly"
        )
        
        # Preview
        print(generator.preview_newsletter(newsletter))
        
        # Also save to JSON for inspection
        with open('newsletter_sample.json', 'w') as f:
            json.dump(newsletter, f, indent=2)
        print("\nNewsletter saved to newsletter_sample.json")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
