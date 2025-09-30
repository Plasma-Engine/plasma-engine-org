"""Blog post templates for different styles and formats"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from app.models import BlogStyle

@dataclass
class BlogTemplate:
    """Blog post template structure"""
    name: str
    style: BlogStyle
    structure: List[Dict[str, str]]
    instructions: str
    example_topics: List[str]
    recommended_length: str
    seo_tips: List[str]

class BlogTemplateManager:
    """Manages blog post templates"""

    def __init__(self):
        self.templates = self._initialize_templates()

    def _initialize_templates(self) -> Dict[BlogStyle, BlogTemplate]:
        """Initialize default templates for each blog style"""
        return {
            BlogStyle.INFORMATIVE: BlogTemplate(
                name="Informative Blog Post",
                style=BlogStyle.INFORMATIVE,
                structure=[
                    {"section": "Introduction", "purpose": "Hook reader and introduce topic"},
                    {"section": "Background/Context", "purpose": "Provide necessary background information"},
                    {"section": "Main Points", "purpose": "Present key information in logical order"},
                    {"section": "Examples/Case Studies", "purpose": "Illustrate points with real examples"},
                    {"section": "Implications", "purpose": "Discuss what this means for readers"},
                    {"section": "Conclusion", "purpose": "Summarize and provide takeaways"}
                ],
                instructions="""Focus on delivering clear, factual information. Use data and statistics to support points.
                Break down complex topics into digestible sections. Include relevant examples and case studies.""",
                example_topics=["Industry trends", "Technology explanations", "Research findings"],
                recommended_length="1000-1500 words",
                seo_tips=["Use header tags (H2, H3) for structure", "Include statistics and data", "Add FAQ section if relevant"]
            ),

            BlogStyle.HOWTO: BlogTemplate(
                name="How-To Guide",
                style=BlogStyle.HOWTO,
                structure=[
                    {"section": "Introduction", "purpose": "Explain what readers will learn"},
                    {"section": "Prerequisites/Materials", "purpose": "List what's needed before starting"},
                    {"section": "Step-by-Step Instructions", "purpose": "Detailed, numbered steps"},
                    {"section": "Tips & Tricks", "purpose": "Pro tips for better results"},
                    {"section": "Common Mistakes", "purpose": "What to avoid"},
                    {"section": "Conclusion", "purpose": "Recap and next steps"}
                ],
                instructions="""Create clear, actionable steps. Use numbered lists for procedures. Include screenshots or
                image placeholders where helpful. Write in second person (you/your). Be specific about each action.""",
                example_topics=["Software tutorials", "DIY projects", "Process guides", "Setup instructions"],
                recommended_length="800-1200 words",
                seo_tips=["Start title with 'How to'", "Use numbered lists", "Include 'step-by-step' in meta description"]
            ),

            BlogStyle.LISTICLE: BlogTemplate(
                name="Listicle",
                style=BlogStyle.LISTICLE,
                structure=[
                    {"section": "Introduction", "purpose": "Preview what's in the list"},
                    {"section": "List Items", "purpose": "Numbered or bulleted list with descriptions"},
                    {"section": "Bonus Tips", "purpose": "Additional valuable information"},
                    {"section": "Conclusion", "purpose": "Wrap up and encourage action"}
                ],
                instructions="""Create scannable content with clear numbering. Each list item should have a bold heading
                and 2-3 sentences of explanation. Order items logically (chronological, importance, or categorical).""",
                example_topics=["Top tools", "Best practices", "Common mistakes", "Resources lists"],
                recommended_length="800-1500 words",
                seo_tips=["Use numbers in title", "Create scannable format", "Bold key points"]
            ),

            BlogStyle.OPINION: BlogTemplate(
                name="Opinion Piece",
                style=BlogStyle.OPINION,
                structure=[
                    {"section": "Hook", "purpose": "Strong opening statement"},
                    {"section": "Thesis", "purpose": "Clear position statement"},
                    {"section": "Arguments", "purpose": "Supporting points with evidence"},
                    {"section": "Counter-arguments", "purpose": "Address opposing views"},
                    {"section": "Conclusion", "purpose": "Reinforce position and call to action"}
                ],
                instructions="""Take a clear stance. Support arguments with evidence. Acknowledge counter-arguments
                respectfully. Use persuasive language while maintaining professionalism. Include personal insights.""",
                example_topics=["Industry predictions", "Technology debates", "Business strategies", "Market analysis"],
                recommended_length="1000-1500 words",
                seo_tips=["Use power words in title", "Include author bio", "Encourage comments"]
            ),

            BlogStyle.CASE_STUDY: BlogTemplate(
                name="Case Study",
                style=BlogStyle.CASE_STUDY,
                structure=[
                    {"section": "Executive Summary", "purpose": "Brief overview of the case"},
                    {"section": "Background", "purpose": "Context and initial situation"},
                    {"section": "Challenge", "purpose": "Problem that needed solving"},
                    {"section": "Solution", "purpose": "How the problem was addressed"},
                    {"section": "Implementation", "purpose": "Step-by-step process"},
                    {"section": "Results", "purpose": "Outcomes with metrics"},
                    {"section": "Key Takeaways", "purpose": "Lessons learned"}
                ],
                instructions="""Focus on real-world examples with concrete results. Include specific metrics and data.
                Tell a compelling story while maintaining objectivity. Highlight challenges and how they were overcome.""",
                example_topics=["Success stories", "Project implementations", "Problem-solving examples", "Transformation stories"],
                recommended_length="1500-2000 words",
                seo_tips=["Include company/project name", "Use 'case study' in title", "Add results/metrics in meta description"]
            ),

            BlogStyle.TECHNICAL: BlogTemplate(
                name="Technical Blog Post",
                style=BlogStyle.TECHNICAL,
                structure=[
                    {"section": "Introduction", "purpose": "Technical overview and objectives"},
                    {"section": "Prerequisites", "purpose": "Required knowledge/tools"},
                    {"section": "Technical Concepts", "purpose": "Explain underlying concepts"},
                    {"section": "Implementation", "purpose": "Code examples and explanations"},
                    {"section": "Testing/Validation", "purpose": "How to verify it works"},
                    {"section": "Performance Considerations", "purpose": "Optimization tips"},
                    {"section": "Conclusion", "purpose": "Summary and further resources"}
                ],
                instructions="""Include code snippets with syntax highlighting markers. Explain technical concepts clearly.
                Provide links to documentation. Include performance metrics where relevant. Consider edge cases.""",
                example_topics=["Code tutorials", "Architecture designs", "API documentation", "Technical deep-dives"],
                recommended_length="1500-2500 words",
                seo_tips=["Include technology names", "Use code formatting", "Add technical keywords"]
            ),

            BlogStyle.COMPARISON: BlogTemplate(
                name="Comparison Post",
                style=BlogStyle.COMPARISON,
                structure=[
                    {"section": "Introduction", "purpose": "What's being compared and why"},
                    {"section": "Criteria", "purpose": "Evaluation factors"},
                    {"section": "Option 1 Analysis", "purpose": "Detailed look at first option"},
                    {"section": "Option 2 Analysis", "purpose": "Detailed look at second option"},
                    {"section": "Side-by-Side Comparison", "purpose": "Direct comparison table/list"},
                    {"section": "Verdict", "purpose": "Recommendations based on use cases"},
                    {"section": "Conclusion", "purpose": "Final thoughts and advice"}
                ],
                instructions="""Be objective and fair in comparisons. Use tables or charts for easy comparison.
                Consider different use cases. Include pricing information if relevant. Provide clear recommendations.""",
                example_topics=["Product comparisons", "Service reviews", "Technology choices", "Platform analysis"],
                recommended_length="1200-1800 words",
                seo_tips=["Use 'vs' in title", "Create comparison tables", "Include both product names in meta"]
            ),

            BlogStyle.NEWS: BlogTemplate(
                name="News Article",
                style=BlogStyle.NEWS,
                structure=[
                    {"section": "Lead", "purpose": "Who, what, when, where, why in first paragraph"},
                    {"section": "Details", "purpose": "Expand on the lead with more information"},
                    {"section": "Background", "purpose": "Context and history"},
                    {"section": "Quotes/Sources", "purpose": "Expert opinions and statements"},
                    {"section": "Impact", "purpose": "What this means for readers"},
                    {"section": "What's Next", "purpose": "Future developments"}
                ],
                instructions="""Write in inverted pyramid style (most important first). Use active voice. Include quotes
                from experts or stakeholders. Remain objective and factual. Include relevant dates and timelines.""",
                example_topics=["Product launches", "Industry updates", "Company announcements", "Market changes"],
                recommended_length="600-1000 words",
                seo_tips=["Include date in URL", "Use news keywords", "Update with fresh information"]
            ),

            BlogStyle.PERSUASIVE: BlogTemplate(
                name="Persuasive Blog Post",
                style=BlogStyle.PERSUASIVE,
                structure=[
                    {"section": "Attention Grabber", "purpose": "Hook with problem or bold statement"},
                    {"section": "Problem Definition", "purpose": "Clearly define the issue"},
                    {"section": "Solution Presentation", "purpose": "Introduce your solution"},
                    {"section": "Benefits", "purpose": "Detailed benefits of the solution"},
                    {"section": "Social Proof", "purpose": "Testimonials, case studies, statistics"},
                    {"section": "Address Objections", "purpose": "Counter common concerns"},
                    {"section": "Call to Action", "purpose": "Clear next steps for reader"}
                ],
                instructions="""Use emotional triggers appropriately. Include social proof and credibility markers.
                Create urgency without being pushy. Focus on benefits over features. Use power words effectively.""",
                example_topics=["Product benefits", "Service advantages", "Change advocacy", "Best practices adoption"],
                recommended_length="1000-1500 words",
                seo_tips=["Use action words", "Include testimonials", "Create compelling meta description"]
            ),

            BlogStyle.NARRATIVE: BlogTemplate(
                name="Narrative Blog Post",
                style=BlogStyle.NARRATIVE,
                structure=[
                    {"section": "Hook", "purpose": "Engaging opening to draw readers in"},
                    {"section": "Setup", "purpose": "Set the scene and introduce characters/situation"},
                    {"section": "Rising Action", "purpose": "Build tension or interest"},
                    {"section": "Climax", "purpose": "Key moment or revelation"},
                    {"section": "Resolution", "purpose": "How things concluded"},
                    {"section": "Lessons Learned", "purpose": "Key takeaways from the story"}
                ],
                instructions="""Tell a compelling story with a clear arc. Use vivid descriptions and sensory details.
                Include dialogue if appropriate. Connect the story to broader themes or lessons. Make it relatable.""",
                example_topics=["Personal experiences", "Company journey", "Customer stories", "Behind-the-scenes"],
                recommended_length="1200-2000 words",
                seo_tips=["Use storytelling keywords", "Include emotional words", "Create intriguing title"]
            )
        }

    def get_template(self, style: BlogStyle) -> Optional[BlogTemplate]:
        """Get template for a specific blog style"""
        return self.templates.get(style)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                "style": style.value,
                "name": template.name,
                "recommended_length": template.recommended_length,
                "example_topics": template.example_topics
            }
            for style, template in self.templates.items()
        ]

    def get_template_structure(self, style: BlogStyle) -> List[Dict[str, str]]:
        """Get the structure for a specific template"""
        template = self.get_template(style)
        return template.structure if template else []

    def get_seo_tips(self, style: BlogStyle) -> List[str]:
        """Get SEO tips for a specific blog style"""
        template = self.get_template(style)
        return template.seo_tips if template else []