"""
Data Scientist Agent

A dedicated agent for analyzing survey data related to customer delivery choices,
environmental impact influence, and generational differences.

Responsibilities:
- Read CSV or Excel input files
- Analyze customer delivery option choices (in-store, standard, express delivery)
- Analyze reasons behind delivery choices
- Analyze environmental impact influence on choices
- Analyze generational differences in delivery preferences
- Output results in markdown or Confluence format
"""

import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("pnd_agents.data_scientist")


@dataclass
class DeliveryChoiceAnalysis:
    """Analysis of delivery option choices."""

    total_responses: int = 0
    choice_distribution: Dict[str, int] = field(default_factory=dict)
    choice_percentages: Dict[str, float] = field(default_factory=dict)
    reasons_by_choice: Dict[str, List[str]] = field(default_factory=dict)
    top_reasons_by_choice: Dict[str, List[Tuple[str, int]]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "totalResponses": self.total_responses,
            "choiceDistribution": self.choice_distribution,
            "choicePercentages": self.choice_percentages,
            "reasonsByChoice": self.reasons_by_choice,
            "topReasonsByChoice": {
                k: [{"reason": r, "count": c} for r, c in v]
                for k, v in self.top_reasons_by_choice.items()
            },
        }


@dataclass
class EnvironmentalImpactAnalysis:
    """Analysis of environmental impact influence on delivery choices."""

    average_importance_score: float = 0.0
    importance_distribution: Dict[str, int] = field(default_factory=dict)
    importance_by_delivery_choice: Dict[str, float] = field(default_factory=dict)
    environmental_factor_selection: Dict[str, int] = field(default_factory=dict)
    correlation_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "averageImportanceScore": self.average_importance_score,
            "importanceDistribution": self.importance_distribution,
            "importanceByDeliveryChoice": self.importance_by_delivery_choice,
            "environmentalFactorSelection": self.environmental_factor_selection,
            "correlationSummary": self.correlation_summary,
        }


@dataclass
class GenerationalAnalysis:
    """Analysis of generational differences in delivery choices."""

    generations: List[str] = field(default_factory=list)
    choice_by_generation: Dict[str, Dict[str, int]] = field(default_factory=dict)
    choice_percentages_by_generation: Dict[str, Dict[str, float]] = field(default_factory=dict)
    environmental_importance_by_generation: Dict[str, float] = field(default_factory=dict)
    key_findings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generations": self.generations,
            "choiceByGeneration": self.choice_by_generation,
            "choicePercentagesByGeneration": self.choice_percentages_by_generation,
            "environmentalImportanceByGeneration": self.environmental_importance_by_generation,
            "keyFindings": self.key_findings,
        }


@dataclass
class SurveyAnalysisResult:
    """Complete survey analysis result."""

    status: str
    delivery_choice_analysis: Optional[DeliveryChoiceAnalysis] = None
    environmental_impact_analysis: Optional[EnvironmentalImpactAnalysis] = None
    generational_analysis: Optional[GenerationalAnalysis] = None
    summary: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "deliveryChoiceAnalysis": (
                self.delivery_choice_analysis.to_dict() if self.delivery_choice_analysis else None
            ),
            "environmentalImpactAnalysis": (
                self.environmental_impact_analysis.to_dict()
                if self.environmental_impact_analysis
                else None
            ),
            "generationalAnalysis": (
                self.generational_analysis.to_dict() if self.generational_analysis else None
            ),
            "summary": self.summary,
            "error": self.error,
        }


class DataScientistAgent:
    """
    Agent for analyzing survey data related to customer delivery choices.

    This agent:
    1. Reads CSV or Excel input files
    2. Analyzes delivery option choices and reasons
    3. Analyzes environmental impact influence
    4. Analyzes generational differences
    5. Outputs results in markdown or Confluence format
    """

    DELIVERY_CHOICE_COLUMN = "Answer"
    REASON_COLUMN = "Answer"
    ENVIRONMENTAL_IMPORTANCE_COLUMN = "Answer"
    AGE_COLUMN = "Age"
    AUDIENCE_COLUMN = "Audience"

    GENERATION_MAPPING = {
        "18 - 24": "Gen Z",
        "25 - 34": "Millennials",
        "35 - 44": "Millennials",
        "45 - 54": "Gen X",
        "55 - 64": "Gen X",
        "50 - 64": "Gen X",
        "65+": "Baby Boomers",
    }

    def __init__(self) -> None:
        """Initialize the Data Scientist Agent."""
        logger.info("DataScientistAgent initialized")

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the data scientist agent as part of a workflow.

        Args:
            context: Workflow context with:
                - task_description: Description of analysis to perform
                - input_data: Dictionary with:
                    - file_path: Path to CSV or Excel file
                    - confluence_link: Optional Confluence page URL for output

        Returns:
            Workflow-compatible result with analysis data
        """
        logger.info("DataScientistAgent.run called")

        input_data = context.get("input_data", {})

        try:
            file_path = input_data.get("file_path", "")
            confluence_link = input_data.get("confluence_link")

            if not file_path:
                return {
                    "status": "error",
                    "data": {},
                    "error": "No file_path provided in input_data",
                }

            result = self.analyze_survey(file_path)

            if confluence_link:
                output = self.generate_confluence_output(result, confluence_link)
            else:
                output = self.generate_markdown_output(result)

            return {
                "status": result.status,
                "data": result.to_dict(),
                "output": output,
                "error": result.error,
            }
        except Exception as e:
            logger.error(f"DataScientistAgent.run failed: {e}")
            return {
                "status": "error",
                "data": {},
                "error": str(e),
            }

    def analyze_survey(self, file_path: str) -> SurveyAnalysisResult:
        """
        Analyze survey data from a CSV or Excel file.

        Args:
            file_path: Path to the survey data file

        Returns:
            SurveyAnalysisResult with complete analysis
        """
        logger.info(f"Analyzing survey data from: {file_path}")

        try:
            data = self._read_data_file(file_path)

            if not data:
                return SurveyAnalysisResult(
                    status="error",
                    error="No data found in file or file could not be parsed",
                )

            delivery_analysis = self._analyze_delivery_choices(data)
            environmental_analysis = self._analyze_environmental_impact(data)
            generational_analysis = self._analyze_generational_differences(data)

            summary = self._generate_summary(
                delivery_analysis, environmental_analysis, generational_analysis
            )

            return SurveyAnalysisResult(
                status="success",
                delivery_choice_analysis=delivery_analysis,
                environmental_impact_analysis=environmental_analysis,
                generational_analysis=generational_analysis,
                summary=summary,
            )

        except Exception as e:
            logger.error(f"Error analyzing survey: {e}")
            return SurveyAnalysisResult(
                status="error",
                error=str(e),
            )

    def _read_data_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read data from CSV or Excel file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = path.suffix.lower()

        if extension == ".csv":
            return self._read_csv(file_path)
        elif extension in [".xlsx", ".xls"]:
            return self._read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def _read_csv(self, file_path: str) -> List[Dict[str, Any]]:
        """Read CSV file and return list of dictionaries."""
        data = []

        with open(file_path, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()

        if len(lines) < 4:
            return data

        header_line = lines[2]
        headers = self._parse_csv_line(header_line)

        for line in lines[3:]:
            if not line.strip():
                continue

            values = self._parse_csv_line(line)

            row = {}
            for i, header in enumerate(headers):
                if i < len(values):
                    row[header] = values[i]
                else:
                    row[header] = ""

            if row.get("Status") == "Complete":
                data.append(row)

        return data

    def _parse_csv_line(self, line: str) -> List[str]:
        """Parse a CSV line handling quoted fields."""
        result = []
        current = ""
        in_quotes = False

        for char in line:
            if char == '"':
                in_quotes = not in_quotes
            elif char == "," and not in_quotes:
                result.append(current.strip())
                current = ""
            else:
                current += char

        result.append(current.strip().rstrip("\n").rstrip("\r"))
        return result

    def _read_excel(self, file_path: str) -> List[Dict[str, Any]]:
        """Read Excel file and return list of dictionaries."""
        try:
            import openpyxl

            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active

            rows = list(ws.iter_rows(values_only=True))
            if len(rows) < 4:
                return []

            headers = list(rows[2])
            data = []

            for row in rows[3:]:
                row_dict = {}
                for i, header in enumerate(headers):
                    if header and i < len(row):
                        row_dict[str(header)] = row[i] if row[i] is not None else ""

                if row_dict.get("Status") == "Complete":
                    data.append(row_dict)

            return data

        except ImportError:
            logger.warning("openpyxl not installed, trying csv fallback")
            return self._read_csv(file_path.replace(".xlsx", ".csv"))

    def _find_column_index(self, headers: List[str], patterns: List[str]) -> int:
        """Find column index matching any of the patterns."""
        for i, header in enumerate(headers):
            header_lower = header.lower() if header else ""
            for pattern in patterns:
                if pattern.lower() in header_lower:
                    return i
        return -1

    def _analyze_delivery_choices(self, data: List[Dict[str, Any]]) -> DeliveryChoiceAnalysis:
        """Analyze delivery option choices and reasons."""
        analysis = DeliveryChoiceAnalysis()

        delivery_choices: List[str] = []
        reasons_by_choice: Dict[str, List[str]] = defaultdict(list)

        delivery_col = None
        for key in data[0].keys() if data else []:
            key_lower = key.lower()
            if "which delivery method" in key_lower or (
                key_lower == "answer" and delivery_col is None
            ):
                if "q2" in key_lower or "delivery method" in key_lower:
                    delivery_col = key

        if not delivery_col:
            for key in data[0].keys() if data else []:
                if key.startswith("Answer") and "delivery" not in key.lower():
                    continue
                if "Q2" in key or "delivery method" in key.lower():
                    delivery_col = key
                    break

        for row in data:
            choice = None
            reason = None

            for key, value in row.items():
                if value and isinstance(value, str):
                    value_lower = value.lower()
                    if any(
                        opt in value_lower
                        for opt in ["express delivery", "standard delivery", "in-store pickup"]
                    ):
                        choice = value.strip()
                    if delivery_col and key == delivery_col:
                        choice = value.strip()

            for key, value in row.items():
                key_lower = key.lower() if key else ""
                if "why did you choose" in key_lower or "q3" in key_lower:
                    if value and isinstance(value, str) and value.strip():
                        reason = value.strip()
                        break

            if choice:
                delivery_choices.append(choice)
                if reason:
                    reasons_by_choice[choice].append(reason)

        analysis.total_responses = len(delivery_choices)

        choice_counts = Counter(delivery_choices)
        analysis.choice_distribution = dict(choice_counts)

        if analysis.total_responses > 0:
            analysis.choice_percentages = {
                choice: round(count / analysis.total_responses * 100, 1)
                for choice, count in choice_counts.items()
            }

        analysis.reasons_by_choice = dict(reasons_by_choice)

        for choice, reasons in reasons_by_choice.items():
            reason_counts = Counter(reasons)
            analysis.top_reasons_by_choice[choice] = reason_counts.most_common(5)

        return analysis

    def _analyze_environmental_impact(
        self, data: List[Dict[str, Any]]
    ) -> EnvironmentalImpactAnalysis:
        """Analyze environmental impact influence on delivery choices."""
        analysis = EnvironmentalImpactAnalysis()

        importance_scores: List[int] = []
        importance_by_choice: Dict[str, List[int]] = defaultdict(list)
        environmental_factor_count = 0
        total_factor_responses = 0

        for row in data:
            importance_score = None
            delivery_choice = None
            selected_environmental = False

            for key, value in row.items():
                key_lower = key.lower() if key else ""

                if "environmental impact" in key_lower or "q4" in key_lower:
                    if value and str(value).strip():
                        try:
                            score = int(str(value).strip())
                            if 1 <= score <= 10:
                                importance_score = score
                        except ValueError:
                            pass

                if value and isinstance(value, str):
                    value_lower = value.lower()
                    if any(
                        opt in value_lower
                        for opt in ["express delivery", "standard delivery", "in-store pickup"]
                    ):
                        delivery_choice = value.strip()

                if "environmentally friendly" in key_lower or (
                    "q5" in key_lower and "environmental" in key_lower
                ):
                    if value and str(value).strip() and str(value).strip() != "�":
                        selected_environmental = True

                if key_lower == "it is more environmentally friendly":
                    if value and str(value).strip() and str(value).strip() != "�":
                        selected_environmental = True

            if importance_score is not None:
                importance_scores.append(importance_score)
                if delivery_choice:
                    importance_by_choice[delivery_choice].append(importance_score)

            for key, value in row.items():
                if "q5" in key.lower() if key else False:
                    if value and str(value).strip() and str(value).strip() != "�":
                        total_factor_responses += 1
                        break

            if selected_environmental:
                environmental_factor_count += 1

        if importance_scores:
            analysis.average_importance_score = round(
                sum(importance_scores) / len(importance_scores), 2
            )

            score_distribution: Dict[str, int] = {
                "Low (1-3)": 0,
                "Medium (4-6)": 0,
                "High (7-10)": 0,
            }
            for score in importance_scores:
                if score <= 3:
                    score_distribution["Low (1-3)"] += 1
                elif score <= 6:
                    score_distribution["Medium (4-6)"] += 1
                else:
                    score_distribution["High (7-10)"] += 1
            analysis.importance_distribution = score_distribution

        for choice, scores in importance_by_choice.items():
            if scores:
                analysis.importance_by_delivery_choice[choice] = round(
                    sum(scores) / len(scores), 2
                )

        analysis.environmental_factor_selection = {
            "selected_environmental_factor": environmental_factor_count,
            "total_responses": total_factor_responses if total_factor_responses > 0 else len(data),
        }

        in_store_avg = analysis.importance_by_delivery_choice.get("In-store pickup", 0)
        express_avg = analysis.importance_by_delivery_choice.get("Express delivery", 0)
        standard_avg = analysis.importance_by_delivery_choice.get("Standard delivery", 0)

        if in_store_avg > express_avg and in_store_avg > standard_avg:
            analysis.correlation_summary = (
                "Customers who choose in-store pickup tend to rate environmental impact "
                f"as more important (avg: {in_store_avg}) compared to those choosing "
                f"express ({express_avg}) or standard delivery ({standard_avg})."
            )
        elif in_store_avg > 0:
            analysis.correlation_summary = (
                "Environmental importance scores are relatively similar across delivery choices, "
                "suggesting environmental concerns may not be the primary driver of delivery choice."
            )
        else:
            analysis.correlation_summary = "Insufficient data to determine correlation."

        return analysis

    def _analyze_generational_differences(
        self, data: List[Dict[str, Any]]
    ) -> GenerationalAnalysis:
        """Analyze generational differences in delivery choices."""
        analysis = GenerationalAnalysis()

        choice_by_gen: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        importance_by_gen: Dict[str, List[int]] = defaultdict(list)

        for row in data:
            age_range = None
            audience = None
            delivery_choice = None
            importance_score = None

            for key, value in row.items():
                if not value or not isinstance(value, str):
                    continue

                key_lower = key.lower() if key else ""
                value_str = str(value).strip()

                if key_lower == "age" or key == "Age":
                    age_range = value_str

                if key_lower == "audience" or key == "Audience":
                    audience = value_str

                value_lower = value_str.lower()
                if any(
                    opt in value_lower
                    for opt in ["express delivery", "standard delivery", "in-store pickup"]
                ):
                    delivery_choice = value_str

                if "environmental impact" in key_lower or "q4" in key_lower:
                    try:
                        score = int(value_str)
                        if 1 <= score <= 10:
                            importance_score = score
                    except ValueError:
                        pass

            generation = None
            if age_range and age_range in self.GENERATION_MAPPING:
                generation = self.GENERATION_MAPPING[age_range]
            elif audience:
                audience_lower = audience.lower()
                if "genz" in audience_lower or "gen z" in audience_lower:
                    generation = "Gen Z"
                elif "30-39" in audience or "millennials" in audience_lower:
                    generation = "Millennials"
                elif "40-49" in audience or "50-64" in audience:
                    generation = "Gen X"

            if generation and delivery_choice:
                choice_by_gen[generation][delivery_choice] += 1

            if generation and importance_score is not None:
                importance_by_gen[generation].append(importance_score)

        analysis.generations = sorted(choice_by_gen.keys())
        analysis.choice_by_generation = {gen: dict(choices) for gen, choices in choice_by_gen.items()}

        for gen, choices in choice_by_gen.items():
            total = sum(choices.values())
            if total > 0:
                analysis.choice_percentages_by_generation[gen] = {
                    choice: round(count / total * 100, 1) for choice, count in choices.items()
                }

        for gen, scores in importance_by_gen.items():
            if scores:
                analysis.environmental_importance_by_generation[gen] = round(
                    sum(scores) / len(scores), 2
                )

        findings = []

        gen_z_instore = analysis.choice_percentages_by_generation.get("Gen Z", {}).get(
            "In-store pickup", 0
        )
        gen_x_instore = analysis.choice_percentages_by_generation.get("Gen X", {}).get(
            "In-store pickup", 0
        )
        if gen_z_instore > gen_x_instore:
            findings.append(
                f"Gen Z shows higher preference for in-store pickup ({gen_z_instore}%) "
                f"compared to Gen X ({gen_x_instore}%)."
            )

        gen_z_env = analysis.environmental_importance_by_generation.get("Gen Z", 0)
        gen_x_env = analysis.environmental_importance_by_generation.get("Gen X", 0)

        if gen_z_env > gen_x_env:
            findings.append(
                f"Gen Z rates environmental impact as more important (avg: {gen_z_env}) "
                f"compared to Gen X (avg: {gen_x_env})."
            )

        gen_z_express = analysis.choice_percentages_by_generation.get("Gen Z", {}).get(
            "Express delivery", 0
        )
        gen_x_express = analysis.choice_percentages_by_generation.get("Gen X", {}).get(
            "Express delivery", 0
        )

        if gen_z_express > gen_x_express:
            findings.append(
                f"Gen Z also shows higher preference for express delivery ({gen_z_express}%) "
                f"compared to Gen X ({gen_x_express}%), suggesting convenience is also important."
            )

        if not findings:
            findings.append(
                "No significant generational differences observed in the data. "
                "Delivery preferences appear relatively consistent across age groups."
            )

        analysis.key_findings = findings

        return analysis

    def _generate_summary(
        self,
        delivery: DeliveryChoiceAnalysis,
        environmental: EnvironmentalImpactAnalysis,
        generational: GenerationalAnalysis,
    ) -> str:
        """Generate executive summary of the analysis."""
        summary_parts = []

        summary_parts.append(
            f"Analysis of {delivery.total_responses} survey responses on delivery preferences."
        )

        if delivery.choice_percentages:
            top_choice = max(delivery.choice_percentages, key=delivery.choice_percentages.get)
            summary_parts.append(
                f"The most popular delivery option is '{top_choice}' "
                f"({delivery.choice_percentages[top_choice]}% of respondents)."
            )

        summary_parts.append(
            f"Average environmental importance score: {environmental.average_importance_score}/10."
        )

        if generational.key_findings:
            summary_parts.append(generational.key_findings[0])

        return " ".join(summary_parts)

    def generate_markdown_output(self, result: SurveyAnalysisResult) -> str:
        """Generate markdown formatted output."""
        if result.status == "error":
            return f"# Analysis Error\n\n{result.error}"

        md = []
        md.append("# Sustainability Impact on Delivery Options - Survey Analysis")
        md.append(f"\n*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        md.append("## Executive Summary\n")
        md.append(result.summary)
        md.append("")

        if result.delivery_choice_analysis:
            delivery = result.delivery_choice_analysis
            md.append("## 1. Customer Delivery Option Choices\n")
            md.append(f"**Total Responses:** {delivery.total_responses}\n")

            md.append("### Choice Distribution\n")
            md.append("| Delivery Option | Count | Percentage |")
            md.append("|-----------------|-------|------------|")
            for choice, count in sorted(
                delivery.choice_distribution.items(), key=lambda x: x[1], reverse=True
            ):
                pct = delivery.choice_percentages.get(choice, 0)
                md.append(f"| {choice} | {count} | {pct}% |")
            md.append("")

            md.append("### Reasons Behind Choices\n")
            for choice, reasons in delivery.top_reasons_by_choice.items():
                md.append(f"**{choice}:**\n")
                for reason, count in reasons[:5]:
                    md.append(f"- {reason} ({count} responses)")
                md.append("")

        if result.environmental_impact_analysis:
            env = result.environmental_impact_analysis
            md.append("## 2. Environmental Impact Influence\n")

            md.append(
                f"**Average Importance Score:** {env.average_importance_score}/10 "
                "(1=Not important, 10=Very important)\n"
            )

            md.append("### Importance Score Distribution\n")
            md.append("| Category | Count |")
            md.append("|----------|-------|")
            for category, count in env.importance_distribution.items():
                md.append(f"| {category} | {count} |")
            md.append("")

            md.append("### Environmental Importance by Delivery Choice\n")
            md.append("| Delivery Option | Avg. Environmental Importance |")
            md.append("|-----------------|------------------------------|")
            for choice, avg in sorted(
                env.importance_by_delivery_choice.items(), key=lambda x: x[1], reverse=True
            ):
                md.append(f"| {choice} | {avg} |")
            md.append("")

            md.append("### Correlation Analysis\n")
            md.append(env.correlation_summary)
            md.append("")

            env_selected = env.environmental_factor_selection.get(
                "selected_environmental_factor", 0
            )
            total_resp = env.environmental_factor_selection.get("total_responses", 1)
            env_pct = round(env_selected / total_resp * 100, 1) if total_resp > 0 else 0
            md.append(
                f"**{env_pct}%** of respondents selected 'environmentally friendly' "
                "as a factor encouraging in-store pickup.\n"
            )

        if result.generational_analysis:
            gen = result.generational_analysis
            md.append("## 3. Generational Differences in Delivery Choices\n")

            md.append("### Delivery Preferences by Generation\n")
            if gen.choice_percentages_by_generation:
                all_choices = set()
                for choices in gen.choice_percentages_by_generation.values():
                    all_choices.update(choices.keys())
                all_choices_list = sorted(all_choices)

                header = "| Generation | " + " | ".join(all_choices_list) + " |"
                separator = "|------------|" + "|".join(["------"] * len(all_choices_list)) + "|"
                md.append(header)
                md.append(separator)

                for generation in sorted(gen.choice_percentages_by_generation.keys()):
                    choices = gen.choice_percentages_by_generation[generation]
                    row = f"| {generation} |"
                    for choice in all_choices_list:
                        pct = choices.get(choice, 0)
                        row += f" {pct}% |"
                    md.append(row)
                md.append("")

            md.append("### Environmental Importance by Generation\n")
            md.append("| Generation | Avg. Environmental Importance |")
            md.append("|------------|------------------------------|")
            for generation, avg in sorted(
                gen.environmental_importance_by_generation.items(), key=lambda x: x[1], reverse=True
            ):
                md.append(f"| {generation} | {avg} |")
            md.append("")

            md.append("### Key Findings\n")
            for finding in gen.key_findings:
                md.append(f"- {finding}")
            md.append("")

        md.append("## Conclusions\n")
        md.append(
            "Based on the analysis, the following conclusions can be drawn about "
            "sustainability's impact on customer delivery choices:\n"
        )

        if result.environmental_impact_analysis:
            avg_score = result.environmental_impact_analysis.average_importance_score
            if avg_score >= 7:
                md.append(
                    "1. **High Environmental Awareness:** Customers show strong concern "
                    f"for environmental impact (avg score: {avg_score}/10)."
                )
            elif avg_score >= 4:
                md.append(
                    "1. **Moderate Environmental Awareness:** Customers show moderate concern "
                    f"for environmental impact (avg score: {avg_score}/10)."
                )
            else:
                md.append(
                    "1. **Low Environmental Awareness:** Environmental impact is not a primary "
                    f"concern for most customers (avg score: {avg_score}/10)."
                )

        if result.delivery_choice_analysis:
            in_store_pct = result.delivery_choice_analysis.choice_percentages.get(
                "In-store pickup", 0
            )
            if in_store_pct >= 30:
                md.append(
                    f"2. **Strong In-Store Pickup Adoption:** {in_store_pct}% of customers "
                    "prefer in-store pickup, which is the most sustainable option."
                )
            else:
                md.append(
                    f"2. **In-Store Pickup Opportunity:** Only {in_store_pct}% currently choose "
                    "in-store pickup. There may be opportunity to increase adoption through "
                    "sustainability messaging."
                )

        if result.generational_analysis and result.generational_analysis.key_findings:
            md.append(f"3. **Generational Insights:** {result.generational_analysis.key_findings[0]}")

        return "\n".join(md)

    def generate_confluence_output(
        self, result: SurveyAnalysisResult, confluence_link: str
    ) -> str:
        """Generate Confluence-formatted output."""
        if result.status == "error":
            return f"h1. Analysis Error\n\n{result.error}"

        conf = []
        conf.append("h1. Sustainability Impact on Delivery Options - Survey Analysis")
        conf.append(f"\n_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

        conf.append("h2. Executive Summary\n")
        conf.append(result.summary)
        conf.append("")

        if result.delivery_choice_analysis:
            delivery = result.delivery_choice_analysis
            conf.append("h2. 1. Customer Delivery Option Choices\n")
            conf.append(f"*Total Responses:* {delivery.total_responses}\n")

            conf.append("h3. Choice Distribution\n")
            conf.append("||Delivery Option||Count||Percentage||")
            for choice, count in sorted(
                delivery.choice_distribution.items(), key=lambda x: x[1], reverse=True
            ):
                pct = delivery.choice_percentages.get(choice, 0)
                conf.append(f"|{choice}|{count}|{pct}%|")
            conf.append("")

            conf.append("h3. Reasons Behind Choices\n")
            for choice, reasons in delivery.top_reasons_by_choice.items():
                conf.append(f"*{choice}:*\n")
                for reason, count in reasons[:5]:
                    conf.append(f"* {reason} ({count} responses)")
                conf.append("")

        if result.environmental_impact_analysis:
            env = result.environmental_impact_analysis
            conf.append("h2. 2. Environmental Impact Influence\n")

            conf.append(
                f"*Average Importance Score:* {env.average_importance_score}/10 "
                "(1=Not important, 10=Very important)\n"
            )

            conf.append("h3. Importance Score Distribution\n")
            conf.append("||Category||Count||")
            for category, count in env.importance_distribution.items():
                conf.append(f"|{category}|{count}|")
            conf.append("")

            conf.append("h3. Environmental Importance by Delivery Choice\n")
            conf.append("||Delivery Option||Avg. Environmental Importance||")
            for choice, avg in sorted(
                env.importance_by_delivery_choice.items(), key=lambda x: x[1], reverse=True
            ):
                conf.append(f"|{choice}|{avg}|")
            conf.append("")

            conf.append("h3. Correlation Analysis\n")
            conf.append(env.correlation_summary)
            conf.append("")

        if result.generational_analysis:
            gen = result.generational_analysis
            conf.append("h2. 3. Generational Differences in Delivery Choices\n")

            conf.append("h3. Delivery Preferences by Generation\n")
            if gen.choice_percentages_by_generation:
                all_choices = set()
                for choices in gen.choice_percentages_by_generation.values():
                    all_choices.update(choices.keys())
                all_choices_list = sorted(all_choices)

                header = "||Generation||" + "||".join(all_choices_list) + "||"
                conf.append(header)

                for generation in sorted(gen.choice_percentages_by_generation.keys()):
                    choices = gen.choice_percentages_by_generation[generation]
                    row = f"|{generation}|"
                    for choice in all_choices_list:
                        pct = choices.get(choice, 0)
                        row += f"{pct}%|"
                    conf.append(row)
                conf.append("")

            conf.append("h3. Key Findings\n")
            for finding in gen.key_findings:
                conf.append(f"* {finding}")
            conf.append("")

        conf.append("h2. Conclusions\n")
        conf.append(
            "Based on the analysis, the following conclusions can be drawn about "
            "sustainability's impact on customer delivery choices:\n"
        )

        if result.environmental_impact_analysis:
            avg_score = result.environmental_impact_analysis.average_importance_score
            if avg_score >= 7:
                conf.append(
                    f"# *High Environmental Awareness:* Customers show strong concern "
                    f"for environmental impact (avg score: {avg_score}/10)."
                )
            elif avg_score >= 4:
                conf.append(
                    f"# *Moderate Environmental Awareness:* Customers show moderate concern "
                    f"for environmental impact (avg score: {avg_score}/10)."
                )
            else:
                conf.append(
                    f"# *Low Environmental Awareness:* Environmental impact is not a primary "
                    f"concern for most customers (avg score: {avg_score}/10)."
                )

        return "\n".join(conf)


def run(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to run the Data Scientist Agent.

    Args:
        context: Workflow context

    Returns:
        Workflow-compatible result
    """
    agent = DataScientistAgent()
    return agent.run(context)


def analyze_survey_data(
    file_path: str,
    confluence_link: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyze survey data and return results.

    Convenience function for independent usage.

    Args:
        file_path: Path to CSV or Excel file
        confluence_link: Optional Confluence page URL for output format

    Returns:
        Analysis result dictionary with markdown or Confluence output
    """
    agent = DataScientistAgent()
    result = agent.analyze_survey(file_path)

    if confluence_link:
        output = agent.generate_confluence_output(result, confluence_link)
    else:
        output = agent.generate_markdown_output(result)

    return {
        "status": result.status,
        "data": result.to_dict(),
        "output": output,
        "error": result.error,
    }
