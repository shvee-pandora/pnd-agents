# Data Scientist Agent

## Problem Statement

Retail businesses increasingly need to understand how sustainability concerns influence customer purchasing decisions, particularly around delivery options. When customers shop online, they face choices between in-store pickup, standard delivery, and express delivery, each with different environmental footprints.

Understanding the relationship between environmental awareness and delivery preferences is critical for:

- Optimizing delivery operations to align with customer values
- Developing targeted sustainability messaging
- Identifying generational trends in eco-conscious shopping behavior
- Making data-driven decisions about promoting greener delivery options

However, analyzing survey data to extract these insights typically requires manual data processing, statistical analysis, and report generation, which is time-consuming and prone to inconsistency.

## What This Agent Solves

The Data Scientist Agent automates the analysis of customer survey data related to delivery choices and sustainability. It provides:

**1. Delivery Choice Analysis**
- Distribution of customer preferences across delivery options (in-store pickup, standard delivery, express delivery)
- Extraction and categorization of reasons behind each delivery choice
- Identification of the most common factors influencing decisions

**2. Environmental Impact Analysis**
- Measurement of how important environmental concerns are to customers (1-10 scale)
- Correlation between environmental awareness and delivery choice
- Identification of which delivery option attracts the most environmentally conscious customers

**3. Generational Analysis**
- Comparison of delivery preferences across Gen Z, Millennials, and Gen X
- Analysis of environmental importance scores by generation
- Key findings highlighting significant generational differences

**4. Automated Report Generation**
- Markdown format for documentation and sharing
- Confluence wiki format for team collaboration
- Executive summary with key insights

## How to Use

### Basic Usage

```python
from agents.data_scientist_agent import analyze_survey_data

# Analyze a CSV file and get markdown output
result = analyze_survey_data("/path/to/survey_data.csv")

# Print the markdown report
print(result["output"])

# Access structured data
print(result["data"]["deliveryChoiceAnalysis"])
print(result["data"]["environmentalImpactAnalysis"])
print(result["data"]["generationalAnalysis"])
```

### With Confluence Output

```python
from agents.data_scientist_agent import analyze_survey_data

# Provide a Confluence link to get Confluence-formatted output
result = analyze_survey_data(
    file_path="/path/to/survey_data.csv",
    confluence_link="https://your-confluence.atlassian.net/wiki/spaces/TEAM/pages/123456"
)

print(result["output"])  # Confluence wiki markup
```

### Using the Agent Class Directly

```python
from agents.data_scientist_agent import DataScientistAgent

agent = DataScientistAgent()

# Analyze survey data
result = agent.analyze_survey("/path/to/survey_data.csv")

# Generate markdown report
markdown_report = agent.generate_markdown_output(result)

# Or generate Confluence report
confluence_report = agent.generate_confluence_output(result, "https://confluence-link")
```

### Workflow Integration

The agent can be used as part of a larger workflow:

```python
from agents.data_scientist_agent import DataScientistAgent

agent = DataScientistAgent()

context = {
    "task_description": "Analyze sustainability survey data",
    "input_data": {
        "file_path": "/path/to/survey_data.csv",
        "confluence_link": None  # Optional
    }
}

result = agent.run(context)
print(result["status"])  # "success" or "error"
print(result["output"])  # The formatted report
```

## Supported File Formats

- **CSV** (.csv) - Comma-separated values with headers on row 3
- **Excel** (.xlsx, .xls) - Requires openpyxl package for Excel support

## Expected Survey Data Structure

The agent expects survey data with the following columns:

| Column | Description |
|--------|-------------|
| Status | "Complete" for valid responses |
| Age | Age range (e.g., "18 - 24", "25 - 34") |
| Audience | Customer segment (e.g., "SP GenZ Customers") |
| Q2/Delivery Method | Selected delivery option |
| Q3/Why did you choose | Reason for delivery choice |
| Q4/Environmental Impact | Importance score (1-10) |
| Q5/Factors | Factors encouraging in-store pickup |

## Output Structure

The agent returns a dictionary with:

```python
{
    "status": "success",  # or "error"
    "data": {
        "deliveryChoiceAnalysis": {
            "totalResponses": 206,
            "choiceDistribution": {"In-store pickup": 85, "Standard delivery": 72, ...},
            "choicePercentages": {"In-store pickup": 41.3, ...},
            "topReasonsByChoice": {...}
        },
        "environmentalImpactAnalysis": {
            "averageImportanceScore": 5.2,
            "importanceDistribution": {"Low (1-3)": 45, "Medium (4-6)": 89, "High (7-10)": 72},
            "importanceByDeliveryChoice": {"In-store pickup": 6.1, ...},
            "correlationSummary": "..."
        },
        "generationalAnalysis": {
            "generations": ["Gen Z", "Millennials", "Gen X"],
            "choicePercentagesByGeneration": {...},
            "environmentalImportanceByGeneration": {...},
            "keyFindings": [...]
        },
        "summary": "Executive summary text..."
    },
    "output": "# Markdown or Confluence formatted report...",
    "error": null
}
```

## Example Report Output

The agent generates comprehensive reports including:

- Executive summary with key metrics
- Delivery choice distribution tables
- Top reasons for each delivery option
- Environmental importance score analysis
- Generational comparison tables
- Key findings and conclusions
