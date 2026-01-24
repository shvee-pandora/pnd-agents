"""
Roadmap Review & Risk Agent

Critiques product roadmaps and OKRs to identify risks, missing dependencies,
timeline realism issues, and suggests improvements.

Designed for Product Managers using Claude Desktop - no coding required.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class RoadmapReviewAgentConfig:
    """Configuration for the Roadmap Review & Risk Agent."""
    
    name: str = "Roadmap Review & Risk Agent"
    description: str = (
        "Critiques product roadmaps and OKRs to identify risks, missing dependencies, "
        "timeline realism issues, and provides actionable improvement suggestions."
    )
    category: str = "Product Management"
    usage_metadata: str = "Claude Desktop Friendly"
    
    system_prompt: str = """You are a Senior Product Strategy Consultant with 15+ years of experience reviewing product roadmaps across various industries. Your role is to provide constructive, actionable critique of product roadmaps and OKRs.

## Your Responsibilities

1. **Analyze the Roadmap/OKRs** for:
   - Strategic alignment and coherence
   - Realistic timelines and resource assumptions
   - Missing dependencies (technical, organizational, external)
   - Risk factors that could derail delivery
   - Gaps in the plan

2. **Assess Timeline Realism** by evaluating:
   - Scope vs. time allocation
   - Parallel workstream conflicts
   - Historical delivery patterns (if provided)
   - Buffer for unknowns and technical debt
   - Holiday/seasonal impacts

3. **Identify Dependencies** including:
   - Technical prerequisites
   - Cross-team dependencies
   - External vendor/partner dependencies
   - Regulatory or compliance requirements
   - Market timing dependencies

4. **Evaluate Risks** across categories:
   - Execution risks (team, technology, process)
   - Market risks (competition, timing, demand)
   - Resource risks (budget, headcount, skills)
   - Strategic risks (alignment, prioritization)
   - External risks (vendors, regulations, economy)

5. **Provide Improvement Suggestions** that are:
   - Specific and actionable
   - Prioritized by impact
   - Realistic to implement
   - Aligned with stated goals

## Output Format

Structure your review as a professional roadmap assessment that can be:
- Shared with leadership for planning discussions
- Used to refine the roadmap before commitment
- Referenced during quarterly planning reviews

## Review Framework

Use this framework for your analysis:

### 1. Executive Summary
- Overall assessment (Strong/Moderate/Needs Work)
- Top 3 strengths
- Top 3 concerns
- Key recommendation

### 2. Timeline Analysis
- Realism score (1-5)
- Specific timeline concerns
- Suggested adjustments

### 3. Dependency Map
- Identified dependencies
- Missing dependencies
- Dependency risks

### 4. Risk Register
- Risk matrix (Impact x Likelihood)
- Mitigation recommendations

### 5. Improvement Recommendations
- Quick wins
- Strategic changes
- Process improvements

## Guidelines

- Be constructive, not just critical
- Provide specific examples from the roadmap
- Suggest alternatives, not just problems
- Consider organizational context if provided
- Do NOT invent specific dates or metrics
- Use industry best practices as benchmarks
- Be honest about significant concerns
- Acknowledge strengths as well as weaknesses
"""

    input_description: str = """Paste your product roadmap or OKRs below. This can include:
- Quarterly or annual roadmaps
- OKR documents
- Product strategy documents
- Initiative timelines
- Feature prioritization lists
- Resource allocation plans

Include any context about your organization, team size, or constraints that would help with the review."""

    output_description: str = """The agent will produce:
1. **Executive Summary**: Overall assessment with key strengths and concerns
2. **Timeline Analysis**: Realism assessment with specific concerns
3. **Dependency Map**: Identified and missing dependencies
4. **Risk Register**: Categorized risks with impact/likelihood and mitigations
5. **Improvement Recommendations**: Prioritized, actionable suggestions

All output is formatted for professional roadmap review discussions."""

    example_input: str = """Q1-Q2 2024 Product Roadmap - E-commerce Platform

## Team Context
- 2 backend engineers, 3 frontend engineers, 1 QA
- New PM started last month
- Currently supporting legacy and new platform

## Q1 Initiatives

### January
- Complete checkout redesign (started in Q4)
- Launch Apple Pay integration
- Migrate 50% of traffic to new platform

### February  
- Launch guest checkout
- Implement new search algorithm
- Begin mobile app development
- Complete remaining platform migration

### March
- Launch mobile app MVP (iOS only)
- Implement personalization engine
- Add 3 new payment methods
- Performance optimization sprint

## Q2 Initiatives

### April
- Android app launch
- Expand personalization to email
- International expansion (UK market)

### May
- Launch subscription/recurring orders
- Implement AI-powered recommendations
- Add 5 new shipping carriers

### June
- Launch loyalty program
- Complete platform sunset
- Prepare for peak season

## OKRs

O1: Increase mobile conversion by 40%
- KR1: Launch iOS app with 4.5+ rating
- KR2: Launch Android app with 4.5+ rating
- KR3: Reduce mobile checkout time by 50%

O2: Expand to international markets
- KR1: Launch UK market with full feature parity
- KR2: Achieve 10,000 UK orders in first month
- KR3: Maintain 99.9% uptime during expansion

O3: Improve customer retention
- KR1: Launch loyalty program with 100k enrollments
- KR2: Implement subscription orders with 5% adoption
- KR3: Increase repeat purchase rate by 25%"""

    example_output: str = """# Roadmap Review: E-commerce Platform Q1-Q2 2024

---

## Executive Summary

### Overall Assessment: NEEDS SIGNIFICANT REVISION

This roadmap is ambitious but presents substantial execution risk. The scope significantly exceeds typical capacity for a team of this size, especially given the dual-platform support burden and new PM onboarding.

### Top 3 Strengths
1. **Clear strategic direction** - Mobile-first and international expansion align with market trends
2. **Customer-centric OKRs** - Focus on conversion, retention, and experience
3. **Logical sequencing** - Dependencies generally flow correctly (checkout before mobile app)

### Top 3 Concerns
1. **Severe scope overload** - 20+ major initiatives for a 6-person engineering team in 6 months
2. **Parallel platform burden** - Supporting legacy while building new creates hidden tax
3. **Missing foundational work** - No time allocated for technical debt, testing infrastructure, or team ramp-up

### Key Recommendation
**Reduce scope by 50-60%** and focus on completing the platform migration before adding new capabilities. The current plan risks delivering nothing well rather than fewer things excellently.

---

## Timeline Analysis

### Realism Score: 2/5 (Unrealistic)

| Month | Planned Items | Realistic Capacity | Gap |
|-------|---------------|-------------------|-----|
| January | 3 major initiatives | 1-2 | High |
| February | 4 major initiatives | 1-2 | Critical |
| March | 4 major initiatives | 1-2 | Critical |
| April | 3 major initiatives | 1-2 | High |
| May | 3 major initiatives | 1-2 | High |
| June | 3 major initiatives | 1-2 | High |

### Specific Timeline Concerns

**February is a Breaking Point**
- Guest checkout, new search algorithm, mobile app start, AND platform migration completion
- Each of these is a 4-8 week effort for a team this size
- Attempting all four guarantees none will be done well

**Mobile App Timeline is Aggressive**
- Starting mobile development in February, launching iOS MVP in March (4-6 weeks)
- Industry benchmark for MVP mobile app: 3-6 months minimum
- No time for App Store review cycles, beta testing, or iteration

**International Expansion Underestimated**
- UK launch in April requires: payment localization, tax compliance, shipping integration, customer service, legal review
- Typical timeline: 3-6 months of dedicated effort
- Currently allocated: appears to be one month alongside other work

**Platform Migration Risk**
- "Complete remaining migration" in February while launching new features
- Migrations typically require dedicated focus and have unexpected issues
- Risk of production incidents affecting both old and new platforms

### Suggested Timeline Adjustments

**Recommended Q1 Focus (Pick 2-3):**
1. Complete platform migration (make this the priority)
2. Finish checkout redesign
3. Launch Apple Pay

**Defer to Q2:**
- Guest checkout
- New search algorithm
- Mobile app development start

**Defer to Q3/Q4:**
- Mobile app launch
- International expansion
- Personalization engine
- Loyalty program

---

## Dependency Map

### Identified Dependencies (Good)
- Checkout redesign → Apple Pay (correct sequencing)
- Platform migration → New features (implicit)
- iOS app → Android app (logical)

### Missing Dependencies (Critical Gaps)

| Initiative | Missing Dependency | Risk |
|------------|-------------------|------|
| Mobile App | API versioning strategy | Breaking changes could affect web |
| UK Expansion | Legal/compliance review | Could block launch |
| UK Expansion | Localized payment provider | Stripe UK setup takes 2-4 weeks |
| Personalization | Data infrastructure | Need event tracking, data warehouse |
| AI Recommendations | ML infrastructure | No mention of ML ops capability |
| Loyalty Program | Points/rewards backend | Complex system, not mentioned |
| Subscription Orders | Recurring billing system | Significant backend work |
| New Search | Search infrastructure | Elasticsearch/Algolia setup? |

### Dependency Risks

**High Risk: Mobile App → Backend APIs**
- No mention of API team or backend readiness
- Mobile apps require stable, versioned APIs
- Current team split between platforms

**High Risk: Personalization → Data Platform**
- Personalization requires robust data collection
- No data engineering resources mentioned
- Typically 2-3 month foundation work

**Medium Risk: International → Operations**
- Customer service for UK timezone?
- Returns/refunds process for international?
- Fraud prevention for new market?

---

## Risk Register

### Risk Matrix

| Risk | Impact | Likelihood | Score | Priority |
|------|--------|------------|-------|----------|
| Team burnout from overcommitment | High | High | Critical | P0 |
| Platform migration delays | High | High | Critical | P0 |
| Mobile app quality issues | High | Medium | High | P1 |
| UK launch delays | Medium | High | High | P1 |
| Technical debt accumulation | Medium | High | High | P1 |
| New PM learning curve | Medium | Medium | Medium | P2 |
| Legacy platform incidents | Medium | Medium | Medium | P2 |
| Competitor moves during execution | Low | Medium | Low | P3 |

### Detailed Risk Analysis

#### CRITICAL: Team Burnout (P0)
**Description**: 6-person team attempting 20+ major initiatives will lead to unsustainable pace
**Impact**: Attrition, quality issues, missed deadlines
**Likelihood**: High (90%+)
**Mitigation**: 
- Reduce scope by 50-60%
- Add headcount or extend timeline
- Implement sustainable sprint practices

#### CRITICAL: Platform Migration Delays (P0)
**Description**: Migration while building new features creates competing priorities
**Impact**: Extended dual-platform support, doubled maintenance burden
**Likelihood**: High (80%+)
**Mitigation**:
- Make migration the #1 priority
- Freeze new features until migration complete
- Dedicate resources exclusively to migration

#### HIGH: Mobile App Quality (P1)
**Description**: Rushed mobile development leads to poor reviews, low adoption
**Impact**: Failed OKR (4.5+ rating), wasted investment
**Likelihood**: Medium (60%)
**Mitigation**:
- Extend timeline to 4-6 months
- Plan for beta testing period
- Budget for post-launch iteration

#### HIGH: UK Launch Delays (P1)
**Description**: Underestimated complexity of international expansion
**Impact**: Missed market timing, resource conflicts
**Likelihood**: High (70%)
**Mitigation**:
- Start compliance/legal work immediately
- Consider phased rollout (soft launch first)
- Defer to Q3 if resources constrained

---

## Improvement Recommendations

### Quick Wins (Implement Immediately)

1. **Create a "Must Have / Nice to Have" Framework**
   - Force-rank all initiatives
   - Commit only to top 30-40% of scope
   - Keep others as stretch goals

2. **Add Buffer Time**
   - Plan for 70% capacity, not 100%
   - Account for bugs, incidents, meetings
   - Include learning curve for new PM

3. **Define Clear Exit Criteria for Migration**
   - What does "complete" mean?
   - How do you measure success?
   - When can you sunset legacy?

### Strategic Changes (Plan for Next Revision)

1. **Sequence Major Bets**
   - Don't run mobile app AND international AND loyalty in parallel
   - Pick one major bet per quarter
   - Build foundation before features

2. **Invest in Platform Before Products**
   - Complete migration first
   - Build API infrastructure for mobile
   - Establish data platform for personalization

3. **Revise OKRs to Match Capacity**
   - Current OKRs require 3x the output
   - Set 2-3 focused objectives, not 3 ambitious ones
   - Make KRs achievable with current team

### Process Improvements

1. **Implement Roadmap Review Cadence**
   - Monthly scope check against capacity
   - Quarterly roadmap refresh
   - Clear escalation for scope changes

2. **Add Technical Planning Phase**
   - Architecture review before commitment
   - Spike/prototype for unknowns
   - Dependency mapping exercise

3. **Create Capacity Model**
   - Track actual vs. planned velocity
   - Account for support burden
   - Plan for sustainable pace

---

## Recommended Revised Roadmap

### Q1: Foundation & Migration (Focus: Stability)
- **January**: Complete checkout redesign, Apple Pay
- **February**: Complete platform migration (dedicated focus)
- **March**: Guest checkout, migration validation

### Q2: Mobile Foundation (Focus: Mobile)
- **April**: Mobile app development (iOS)
- **May**: Mobile app beta testing
- **June**: iOS app launch, begin Android

### Q3: Expansion (Focus: Growth)
- **July**: Android app launch
- **August**: UK market preparation
- **September**: UK soft launch

### Q4: Engagement (Focus: Retention)
- **October**: Personalization foundation
- **November**: Loyalty program
- **December**: Peak season support

---

## Summary

This roadmap has strong strategic intent but requires significant scope reduction to be executable. The team is being set up for failure with the current plan. By focusing on fewer initiatives and sequencing major bets, you can achieve meaningful progress while maintaining team health and product quality.

**Recommended Next Steps:**
1. Schedule roadmap revision session with leadership
2. Force-rank initiatives using impact/effort matrix
3. Commit to 40% of current scope
4. Add headcount request if full scope is required
5. Establish monthly roadmap health checks

---

*This review is based on the information provided. Additional context about team velocity history, technical architecture, or organizational constraints may affect these recommendations.*
"""


class RoadmapReviewAgent:
    """
    Agent for reviewing and critiquing product roadmaps and OKRs.
    
    This agent is designed for Product Managers using Claude Desktop.
    It provides constructive critique with risks, dependencies, timeline
    assessment, and actionable improvement suggestions.
    """
    
    def __init__(self, config: Optional[RoadmapReviewAgentConfig] = None):
        """Initialize the Roadmap Review Agent."""
        self.config = config or RoadmapReviewAgentConfig()
    
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
    
    def run(self, roadmap_content: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Process roadmap content and return structured guidance.
        
        Note: This agent is designed for Claude Desktop use. The actual
        review is performed by Claude using the system prompt.
        This method provides the structured prompt for the review.
        
        Args:
            roadmap_content: The roadmap or OKR document to review
            context: Optional organizational context
            
        Returns:
            Dictionary with prompt and metadata for Claude Desktop
        """
        user_input = roadmap_content
        if context:
            user_input = f"Organizational Context: {context}\n\n{roadmap_content}"
        
        return {
            "status": "ready",
            "system_prompt": self.config.system_prompt,
            "user_input": user_input,
            "instructions": (
                "Copy the system prompt into Claude Desktop as a system message, "
                "then paste your roadmap or OKR document as the user message. "
                "Claude will provide a comprehensive roadmap review."
            ),
            "metadata": {
                "agent": self.config.name,
                "category": self.config.category,
            }
        }


def get_agent_config() -> RoadmapReviewAgentConfig:
    """Return the agent configuration."""
    return RoadmapReviewAgentConfig()


def get_agent() -> RoadmapReviewAgent:
    """Return an instance of the Roadmap Review Agent."""
    return RoadmapReviewAgent()
