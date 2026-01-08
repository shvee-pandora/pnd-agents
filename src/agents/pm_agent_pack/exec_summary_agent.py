"""
Stakeholder Update / Executive Summary Agent

Converts sprint data, Jira summaries, or project updates into executive-friendly
communications suitable for Directors and VPs.

Designed for Product Managers using Claude Desktop - no coding required.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class ExecSummaryAgentConfig:
    """Configuration for the Executive Summary Agent."""
    
    name: str = "Stakeholder Update / Exec Summary Agent"
    description: str = (
        "Converts sprint data or Jira summaries into executive-friendly updates "
        "with 1-page summaries, risks & mitigations, and decisions required. "
        "Designed for Director/VP audiences."
    )
    category: str = "Product Management"
    usage_metadata: str = "Claude Desktop Friendly"
    
    system_prompt: str = """You are a Senior Product Manager with expertise in executive communication. Your role is to transform technical sprint data, Jira summaries, or project updates into clear, concise executive summaries suitable for Directors and VPs.

## Your Responsibilities

1. **Synthesize Information** to create:
   - A clear executive summary (1 page or less)
   - Key accomplishments and progress highlights
   - Risks with mitigation strategies
   - Decisions that require leadership input
   - Next steps and upcoming milestones

2. **Write for Executives** by:
   - Leading with business impact, not technical details
   - Using clear, jargon-free language
   - Keeping the summary scannable (bullets, headers)
   - Highlighting what matters to leadership
   - Being direct about blockers and needs

3. **Structure the Update** with:
   - **TL;DR**: 2-3 sentence summary at the top
   - **Progress**: What was accomplished
   - **Metrics**: Key numbers that matter
   - **Risks**: Issues and mitigation plans
   - **Decisions Needed**: Clear asks with options
   - **Next Steps**: What's coming up

4. **Apply Executive Communication Best Practices**:
   - Start with the conclusion/recommendation
   - Use the "So What?" test for every point
   - Quantify impact where possible
   - Be honest about challenges
   - Provide options, not just problems

## Output Format

Structure your response as a professional executive update that can be:
- Sent directly via email to leadership
- Presented in a steering committee meeting
- Posted to Slack/Teams for stakeholder visibility

## Guidelines

- Keep the total length to 1 page (approximately 400-500 words)
- Use business language, not technical jargon
- Do NOT include specific dates unless provided in the input
- Do NOT invent metrics or numbers - use placeholders if needed
- Focus on outcomes and impact, not activities
- Make decisions/asks crystal clear with deadlines if known
- Use RAG status (Red/Amber/Green) for quick visual scanning
"""

    input_description: str = """Paste your sprint data, Jira summary, or project update below. This can include:
- Sprint completion reports
- Jira board exports or summaries
- Weekly/monthly status updates
- Project milestone updates
- Team velocity data
- Bug/issue summaries
- Release notes or changelogs

Include any context about your audience (e.g., "This is for our VP of Engineering weekly update")."""

    output_description: str = """The agent will produce:
1. **TL;DR**: Quick 2-3 sentence summary
2. **Progress Highlights**: Key accomplishments with business impact
3. **Metrics Dashboard**: Key numbers in an easy-to-scan format
4. **Risks & Mitigations**: Issues with RAG status and action plans
5. **Decisions Required**: Clear asks with options and recommendations
6. **Next Steps**: Upcoming milestones and focus areas

All output is formatted for direct use in executive communications."""

    example_input: str = """Sprint 47 Summary - Checkout Team

Completed Stories:
- CHKOUT-1234: Implement Apple Pay integration (8 points)
- CHKOUT-1235: Fix cart abandonment tracking bug (3 points)
- CHKOUT-1236: Add gift message field to checkout (5 points)
- CHKOUT-1237: Performance optimization for payment page (5 points)

Carried Over:
- CHKOUT-1238: PayPal Express checkout (8 points) - blocked by PayPal API access
- CHKOUT-1239: Guest checkout flow redesign (13 points) - design not finalized

Sprint Metrics:
- Velocity: 21 points (target was 30)
- Bug count: 3 new, 5 resolved
- Code coverage: 78% (down from 82%)

Team Notes:
- Lost 2 days to production incident on Tuesday
- New developer Sarah started, still ramping up
- PayPal integration blocked - waiting on finance approval for API credentials
- Design team delayed on guest checkout mockups

Upcoming:
- Black Friday prep starts next sprint
- Need decision on whether to prioritize PayPal or guest checkout
- Performance testing scheduled for next week"""

    example_output: str = """# Checkout Team Update - Sprint 47

---

## TL;DR

Sprint delivered Apple Pay and key bug fixes but fell short of velocity target due to a production incident and external blockers. **Decision needed**: Prioritize PayPal integration vs. guest checkout redesign for Black Friday readiness.

---

## Overall Status: AMBER

| Area | Status | Trend |
|------|--------|-------|
| Delivery | AMBER | Improving |
| Quality | GREEN | Stable |
| Risk | AMBER | New blocker |

---

## Progress Highlights

**Delivered This Sprint:**
- **Apple Pay Integration** - Now live, enabling faster mobile checkout (expected 15% conversion lift on iOS)
- **Cart Abandonment Fix** - Resolved tracking bug affecting analytics accuracy
- **Gift Messaging** - Customers can now add gift messages, ready for holiday season
- **Payment Page Performance** - 40% faster load time on payment step

**Business Impact**: Apple Pay launch positions us well for holiday mobile traffic. Gift messaging addresses top customer request from NPS feedback.

---

## Key Metrics

| Metric | This Sprint | Target | Status |
|--------|-------------|--------|--------|
| Velocity | 21 pts | 30 pts | AMBER |
| Stories Completed | 4 of 6 | 6 | AMBER |
| Bugs Resolved | 5 | - | GREEN |
| Code Coverage | 78% | 80% | AMBER |

**Velocity Note**: 2-day production incident and new team member onboarding impacted capacity. Expect return to normal next sprint.

---

## Risks & Mitigations

| Risk | Impact | Status | Mitigation |
|------|--------|--------|------------|
| PayPal blocked by API credentials | High - Black Friday revenue | RED | Finance approval needed by [DATE] - escalation path identified |
| Guest checkout design delayed | Medium - Conversion impact | AMBER | Working with Design lead to prioritize; fallback plan available |
| Code coverage declining | Low - Technical debt | AMBER | Adding coverage requirements to PR checklist |

---

## Decisions Required

### 1. Black Friday Priority (Decision needed by [DATE])

**Context**: We can deliver either PayPal Express OR Guest Checkout redesign before Black Friday, not both.

**Options**:
| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| A: PayPal First | Higher AOV customers use PayPal; 12% of current transactions | Blocked until API access approved | Recommended if API access confirmed this week |
| B: Guest Checkout First | Addresses 23% cart abandonment from forced registration | Larger scope, design dependency | Fallback if PayPal remains blocked |

**Recommendation**: Prioritize PayPal if Finance can approve API credentials by [DATE]. Otherwise, pivot to Guest Checkout.

### 2. API Credential Approval

**Ask**: Expedite Finance approval for PayPal API production credentials.

**Impact of Delay**: Each week of delay reduces Black Friday PayPal revenue opportunity by approximately [X]%.

---

## Next Steps

**This Week:**
- Complete PayPal API integration (pending credential approval)
- Finalize guest checkout designs with UX team
- Begin Black Friday load testing

**Next Sprint Focus:**
- Black Friday readiness testing
- Either PayPal launch OR guest checkout (per decision above)
- Address code coverage gap

---

## Team Update

- **New Joiner**: Sarah (Frontend) started this sprint, completing onboarding
- **Capacity**: Back to full capacity next sprint (no PTO planned)

---

*Questions? Reach out to [PM Name] or join #checkout-team on Slack*
"""


class ExecSummaryAgent:
    """
    Agent for converting sprint/project data into executive summaries.
    
    This agent is designed for Product Managers using Claude Desktop.
    It produces executive-friendly updates suitable for Directors and VPs.
    """
    
    def __init__(self, config: Optional[ExecSummaryAgentConfig] = None):
        """Initialize the Executive Summary Agent."""
        self.config = config or ExecSummaryAgentConfig()
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for Claude Desktop."""
        return self.config.system_prompt
    
    def get_input_description(self) -> str:
        """Return the input description for users."""
        return self.config.input_description
    
    def get_output_description(self) -> str:
        """Return the output description for users."""
        return self.config.output_description
    
    def get_example_input(self) -> str:
        """Return an example input."""
        return self.config.example_input
    
    def get_example_output(self) -> str:
        """Return an example output."""
        return self.config.example_output
    
    def get_agent_metadata(self) -> Dict[str, Any]:
        """Return agent metadata for marketplace registration."""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "category": self.config.category,
            "usage_metadata": self.config.usage_metadata,
            "system_prompt": self.config.system_prompt,
            "input_description": self.config.input_description,
            "output_description": self.config.output_description,
            "example_input": self.config.example_input,
            "example_output": self.config.example_output,
        }
    
    def run(self, sprint_data: str, audience: Optional[str] = None) -> Dict[str, Any]:
        """
        Process sprint/project data and return structured guidance.
        
        Note: This agent is designed for Claude Desktop use. The actual
        conversion is performed by Claude using the system prompt.
        This method provides the structured prompt for the conversion.
        
        Args:
            sprint_data: The sprint data or project update to summarize
            audience: Optional audience context (e.g., "VP of Engineering")
            
        Returns:
            Dictionary with prompt and metadata for Claude Desktop
        """
        user_input = sprint_data
        if audience:
            user_input = f"Audience: {audience}\n\n{sprint_data}"
        
        return {
            "status": "ready",
            "system_prompt": self.config.system_prompt,
            "user_input": user_input,
            "instructions": (
                "Copy the system prompt into Claude Desktop as a system message, "
                "then paste your sprint data or project update as the user message. "
                "Claude will generate an executive-friendly summary."
            ),
            "metadata": {
                "agent": self.config.name,
                "category": self.config.category,
                "audience": audience or "Executive Leadership",
            }
        }


def get_agent_config() -> ExecSummaryAgentConfig:
    """Return the agent configuration."""
    return ExecSummaryAgentConfig()


def get_agent() -> ExecSummaryAgent:
    """Return an instance of the Executive Summary Agent."""
    return ExecSummaryAgent()
