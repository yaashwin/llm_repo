# meeting_templates.py
from typing import Dict, Optional

class MeetingTemplates:
    """Templates for different types of meetings"""
    
    @staticmethod
    def get_template(meeting_type: str = "general") -> Dict[str, str]:
        """Get template based on meeting type"""
        
        templates = {
            "general": {
                "summary_prompt": """Create a professional meeting summary with:
1. Meeting Overview (date, participants, purpose)
2. Key Discussion Points (main topics, decisions, concerns)
3. Decisions and Outcomes
4. Action Items (table format)
5. Key Takeaways (3-5 points)""",
                
                "insights_prompt": """Identify:
1. Risks and concerns
2. Opportunities
3. Recurring themes
4. Follow-up recommendations""",
                
                "actions_prompt": """Extract action items with:
- Task description
- Responsible person
- Deadline
- Priority (High/Medium/Low)"""
            },
            
            "standup": {
                "summary_prompt": """Summarize this standup meeting:
1. Team Updates (what each person completed/is working on)
2. Blockers and Issues
3. Help Needed
4. Today's Priorities""",
                
                "insights_prompt": """Identify:
1. Team velocity trends
2. Recurring blockers
3. Resource needs
4. Process improvements""",
                
                "actions_prompt": """List:
- Blockers to resolve
- Help requests
- Commitments for today"""
            },
            
            "planning": {
                "summary_prompt": """Summarize this planning meeting:
1. Goals and Objectives
2. Timeline and Milestones
3. Resource Allocation
4. Risk Assessment
5. Success Metrics""",
                
                "insights_prompt": """Analyze:
1. Feasibility concerns
2. Resource gaps
3. Timeline risks
4. Success factors""",
                
                "actions_prompt": """Extract:
- Planning tasks
- Research items
- Approval needs
- Follow-up meetings"""
            },
            
            "retrospective": {
                "summary_prompt": """Summarize this retrospective:
1. What Went Well
2. What Could Be Improved
3. Action Items for Improvement
4. Team Sentiment""",
                
                "insights_prompt": """Identify:
1. Team morale indicators
2. Process bottlenecks
3. Success patterns
4. Improvement opportunities""",
                
                "actions_prompt": """List improvement actions:
- Process changes
- Tool updates
- Team agreements
- Experiments to try"""
            },
            
            "client": {
                "summary_prompt": """Summarize this client meeting:
1. Client Requirements/Feedback
2. Project Status Update
3. Issues and Concerns
4. Next Steps
5. Commitments Made""",
                
                "insights_prompt": """Analyze:
1. Client satisfaction level
2. Expectation gaps
3. Upsell opportunities
4. Relationship health""",
                
                "actions_prompt": """Extract:
- Client requests
- Deliverable commitments
- Follow-up items
- Internal actions"""
            }
        }
        
        return templates.get(meeting_type, templates["general"])