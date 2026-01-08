"""
PRD to Jira Breakdown Agent

Converts Product Requirements Documents (PRD) or Confluence content into
structured Jira epics, user stories, and acceptance criteria.

Designed for Product Managers using Claude Desktop - no coding required.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class PRDToJiraAgentConfig:
    """Configuration for the PRD to Jira Breakdown Agent."""
    
    name: str = "PRD to Jira Breakdown Agent"
    description: str = (
        "Converts PRD or Confluence text into structured Jira work items "
        "including epics, user stories with acceptance criteria in Gherkin format, "
        "dependencies, and risk assessments."
    )
    category: str = "Product Management"
    usage_metadata: str = "Claude Desktop Friendly"
    
    system_prompt: str = """You are a Senior Product Manager with expertise in Agile methodologies and Jira best practices. Your role is to convert Product Requirements Documents (PRDs) or Confluence content into well-structured Jira work items.

## Your Responsibilities

1. **Analyze the PRD/Confluence content** to identify:
   - Major features or initiatives (these become Epics)
   - Specific user-facing functionality (these become User Stories)
   - Technical requirements and constraints
   - Dependencies between work items
   - Potential risks and blockers

2. **Create Epics** that:
   - Have clear, business-focused titles
   - Include a summary describing the business value
   - Group related user stories logically

3. **Write User Stories** following the format:
   - Title: Clear, action-oriented summary
   - Description: "As a [user type], I want [goal] so that [benefit]"
   - Acceptance Criteria: Written in Gherkin format (Given/When/Then)
   - Story Points: Suggested estimate (use ? if unclear)

4. **Identify Dependencies** including:
   - Technical dependencies (APIs, services, infrastructure)
   - Cross-team dependencies
   - External dependencies (third parties, vendors)
   - Sequential dependencies between stories

5. **Assess Risks** including:
   - Technical risks
   - Timeline risks
   - Resource risks
   - Business risks

## Output Format

Structure your response as Jira-ready markdown that can be directly copied into Jira or used as a reference for ticket creation.

## Guidelines

- Use clear, non-technical language where possible
- Avoid jargon unless it's standard in the organization
- Do NOT invent specific Jira IDs, dates, or sprint numbers
- Use placeholders like [EPIC-XXX] or [STORY-XXX] for IDs
- Keep acceptance criteria testable and specific
- Flag any ambiguities in the original PRD that need clarification
"""

    input_description: str = """Paste your PRD or Confluence content below. This can include:
- Feature descriptions
- Business requirements
- Technical specifications
- User flows
- Mockup descriptions
- Any product documentation

The more detail you provide, the more comprehensive the Jira breakdown will be."""

    output_description: str = """The agent will produce:
1. **Epics**: High-level initiatives with business context
2. **User Stories**: Detailed work items with acceptance criteria in Gherkin format
3. **Dependencies**: Technical and cross-team dependencies identified
4. **Risks**: Potential blockers and mitigation suggestions

All output is formatted as Jira-ready markdown that you can copy directly into your Jira instance."""

    example_input: str = """# Product Requirements: Customer Wishlist Feature

## Overview
We need to implement a wishlist feature that allows customers to save products they're interested in for later purchase. This feature should increase conversion rates by allowing customers to bookmark items without committing to purchase.

## User Needs
- Customers want to save products they like but aren't ready to buy
- Customers want to easily find their saved items later
- Customers want to share their wishlist with friends and family

## Functional Requirements
1. Add to Wishlist button on product pages
2. Wishlist page showing all saved items
3. Remove items from wishlist
4. Move items from wishlist to cart
5. Share wishlist via link or email

## Technical Considerations
- Must integrate with existing user authentication
- Should sync across devices for logged-in users
- Guest users can have a session-based wishlist
- Need to handle out-of-stock items in wishlist"""

    example_output: str = """# Jira Breakdown: Customer Wishlist Feature

---

## Epic: [EPIC-XXX] Customer Wishlist

**Summary**: Enable customers to save products for later purchase, improving engagement and conversion rates.

**Business Value**: Increases customer engagement by allowing product bookmarking, reduces cart abandonment, and enables social sharing for gift occasions.

---

## User Stories

### [STORY-XXX] Add to Wishlist Button

**Title**: Add to Wishlist Button on Product Pages

**Description**: 
As a customer browsing products, I want to add items to my wishlist so that I can save them for later consideration without adding to cart.

**Acceptance Criteria**:

```gherkin
Feature: Add to Wishlist

Scenario: Logged-in user adds product to wishlist
  Given I am logged in as a registered customer
  And I am viewing a product detail page
  When I click the "Add to Wishlist" button
  Then the product is added to my wishlist
  And I see a confirmation message "Added to Wishlist"
  And the button changes to "In Wishlist"

Scenario: Guest user adds product to wishlist
  Given I am browsing as a guest user
  And I am viewing a product detail page
  When I click the "Add to Wishlist" button
  Then the product is added to my session wishlist
  And I see a confirmation message "Added to Wishlist"

Scenario: Product already in wishlist
  Given I am viewing a product that is already in my wishlist
  Then I see "In Wishlist" instead of "Add to Wishlist"
  When I click "In Wishlist"
  Then I am prompted to remove or view wishlist
```

**Story Points**: 5

---

### [STORY-XXX] Wishlist Page

**Title**: View and Manage Wishlist Page

**Description**: 
As a customer with saved items, I want to view all my wishlist items on a dedicated page so that I can review and manage my saved products.

**Acceptance Criteria**:

```gherkin
Feature: Wishlist Page

Scenario: View wishlist with items
  Given I have products in my wishlist
  When I navigate to my wishlist page
  Then I see all my saved products displayed
  And each product shows image, name, price, and availability
  And I see options to remove or move to cart

Scenario: Empty wishlist
  Given I have no products in my wishlist
  When I navigate to my wishlist page
  Then I see a message "Your wishlist is empty"
  And I see a link to continue shopping

Scenario: Out-of-stock item in wishlist
  Given I have an out-of-stock product in my wishlist
  When I view my wishlist
  Then the item shows "Out of Stock" status
  And the "Add to Cart" button is disabled
  And I see an option to receive back-in-stock notification
```

**Story Points**: 8

---

### [STORY-XXX] Remove from Wishlist

**Title**: Remove Items from Wishlist

**Description**: 
As a customer managing my wishlist, I want to remove items I'm no longer interested in so that my wishlist stays relevant.

**Acceptance Criteria**:

```gherkin
Feature: Remove from Wishlist

Scenario: Remove item from wishlist page
  Given I am on my wishlist page
  And I have at least one item in my wishlist
  When I click the "Remove" button on an item
  Then the item is removed from my wishlist
  And I see a confirmation message "Item removed"
  And the wishlist updates without page reload

Scenario: Remove item from product page
  Given I am viewing a product that is in my wishlist
  When I click the "In Wishlist" button
  And I select "Remove from Wishlist"
  Then the product is removed from my wishlist
  And the button changes back to "Add to Wishlist"
```

**Story Points**: 3

---

### [STORY-XXX] Move to Cart

**Title**: Move Wishlist Items to Shopping Cart

**Description**: 
As a customer ready to purchase, I want to move items from my wishlist to my cart so that I can easily buy products I previously saved.

**Acceptance Criteria**:

```gherkin
Feature: Move to Cart

Scenario: Move single item to cart
  Given I am on my wishlist page
  And the item is in stock
  When I click "Add to Cart" on a wishlist item
  Then the item is added to my shopping cart
  And the item remains in my wishlist
  And I see a confirmation with link to cart

Scenario: Move out-of-stock item
  Given I am on my wishlist page
  And an item is out of stock
  Then the "Add to Cart" button is disabled
  And I see "Out of Stock" message
```

**Story Points**: 3

---

### [STORY-XXX] Share Wishlist

**Title**: Share Wishlist with Others

**Description**: 
As a customer with a wishlist, I want to share my wishlist with friends and family so that they can see what gifts I would like.

**Acceptance Criteria**:

```gherkin
Feature: Share Wishlist

Scenario: Generate shareable link
  Given I am on my wishlist page
  And I have items in my wishlist
  When I click "Share Wishlist"
  Then I see options to copy link or share via email
  When I copy the link
  Then a unique shareable URL is copied to clipboard

Scenario: View shared wishlist
  Given someone has shared their wishlist link with me
  When I open the shared link
  Then I see the wishlist owner's saved items
  And I see product details and prices
  And I can add items to my own cart

Scenario: Share via email
  Given I am on my wishlist page
  When I click "Share via Email"
  Then I can enter recipient email addresses
  And I can add a personal message
  When I send the email
  Then recipients receive an email with wishlist link
```

**Story Points**: 8

---

## Dependencies

### Technical Dependencies
- **User Authentication Service**: Wishlist must integrate with existing auth to persist across sessions
- **Product Catalog API**: Need read access to product availability and pricing
- **Session Management**: Guest wishlist requires session storage implementation

### Cross-Team Dependencies
- **Frontend Team**: UI components for wishlist button and page
- **Backend Team**: API endpoints for wishlist CRUD operations
- **Email Team**: Email templates for wishlist sharing

### Sequential Dependencies
1. [STORY-XXX] Add to Wishlist must be completed before Wishlist Page
2. Wishlist Page must be completed before Share Wishlist
3. User authentication integration is a prerequisite for all stories

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Performance impact from wishlist queries | Medium | Medium | Implement caching for wishlist data; lazy load images |
| Guest wishlist data loss on session expiry | Low | High | Prompt guests to create account to save wishlist; extend session duration |
| Shared wishlist privacy concerns | Medium | Low | Add privacy settings; allow users to make wishlist private/public |
| Out-of-stock items causing user frustration | Medium | Medium | Implement back-in-stock notifications; show alternative products |

---

## Open Questions

1. Should there be a maximum number of items allowed in a wishlist?
2. How long should guest wishlists be retained?
3. Should we track wishlist analytics (most wishlisted items)?
4. Do we need wishlist categories or folders for organization?

---

*Generated by PRD to Jira Breakdown Agent - Review and adjust estimates based on team capacity*
"""


class PRDToJiraAgent:
    """
    Agent for converting PRD/Confluence content into Jira work items.
    
    This agent is designed for Product Managers using Claude Desktop.
    It produces Jira-ready markdown with epics, stories, acceptance criteria,
    dependencies, and risk assessments.
    """
    
    def __init__(self, config: Optional[PRDToJiraAgentConfig] = None):
        """Initialize the PRD to Jira Agent."""
        self.config = config or PRDToJiraAgentConfig()
    
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
    
    def run(self, prd_content: str) -> Dict[str, Any]:
        """
        Process PRD content and return structured guidance.
        
        Note: This agent is designed for Claude Desktop use. The actual
        conversion is performed by Claude using the system prompt.
        This method provides the structured prompt for the conversion.
        
        Args:
            prd_content: The PRD or Confluence content to convert
            
        Returns:
            Dictionary with prompt and metadata for Claude Desktop
        """
        return {
            "status": "ready",
            "system_prompt": self.config.system_prompt,
            "user_input": prd_content,
            "instructions": (
                "Copy the system prompt into Claude Desktop as a system message, "
                "then paste your PRD content as the user message. "
                "Claude will generate Jira-ready markdown output."
            ),
            "metadata": {
                "agent": self.config.name,
                "category": self.config.category,
            }
        }


def get_agent_config() -> PRDToJiraAgentConfig:
    """Return the agent configuration."""
    return PRDToJiraAgentConfig()


def get_agent() -> PRDToJiraAgent:
    """Return an instance of the PRD to Jira Agent."""
    return PRDToJiraAgent()
