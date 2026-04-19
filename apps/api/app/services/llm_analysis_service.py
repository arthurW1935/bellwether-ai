from typing import Any

from app.clients.llm import LLMClientError, llm_client
from app.schemas.brief import Delta
from app.schemas.common import AlertType, Severity
from app.schemas.watchlist import Company


ALERT_ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {
        "alert_type": {
            "type": "string",
            "enum": [
                "talent_poaching",
                "competitive",
                "roadmap",
                "health",
                "reopen",
                "routine",
            ],
        },
        "severity": {"type": "string", "enum": ["P0", "P1", "P2"]},
        "explanation": {"type": "string"},
        "recommended_action": {"type": "string"},
    },
    "required": ["alert_type", "severity", "explanation", "recommended_action"],
    "additionalProperties": False,
}

BRIEF_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
    },
    "required": ["summary"],
    "additionalProperties": False,
}

ALERT_ANALYSIS_INSTRUCTIONS = """You are Bellwether, an AI associate for VC partners.
Given a company, its cohort, and a detected delta, classify the delta and write the partner-facing alert.
Return JSON only.
Rules:
- invested cohort means portfolio risk/value context
- watching cohort means reopen/opportunity context
- Use one alert_type from the allowed enum
- Use one severity from P0, P1, P2
- explanation should be 2-3 sentences
- recommended_action should be a single sentence"""

BRIEF_SUMMARY_INSTRUCTIONS = """You are Bellwether, an AI associate for VC partners.
Write a concise executive summary of the current alert set.
Return JSON only.
Rules:
- 3 to 4 sentences
- mention partner-level risk/opportunity first
- refer to cohorts when helpful
- keep it crisp and useful for a VC partner"""


class LLMAnalysisService:
    def llm_model_name(self) -> str | None:
        if not llm_client.is_configured:
            return None
        return llm_client.model

    def analyze_delta(self, company: Company, delta: Delta) -> dict[str, Any] | None:
        if not llm_client.is_configured:
            return None

        prompt = (
            f"Company: {company.name}\n"
            f"Cohort: {company.cohort}\n"
            f"Headcount: {company.headcount}\n"
            f"Last funding: {company.last_funding}\n"
            f"Delta kind: {delta.kind}\n"
            f"Delta description: {delta.description}\n"
            f"Delta before: {delta.before}\n"
            f"Delta after: {delta.after}\n"
        )

        try:
            result = llm_client.create_structured_output(
                instructions=ALERT_ANALYSIS_INSTRUCTIONS,
                user_input=prompt,
                schema_name="bellwether_alert_analysis",
                schema=ALERT_ANALYSIS_SCHEMA,
            )
        except LLMClientError:
            return None

        return result

    def summarize_alerts(self, alerts: list[dict[str, Any]]) -> str | None:
        if not llm_client.is_configured:
            return None

        prompt = "\n".join(
            [
                (
                    f"Company: {alert['company_name']}\n"
                    f"Cohort: {alert['cohort']}\n"
                    f"Type: {alert['alert_type']}\n"
                    f"Severity: {alert['severity']}\n"
                    f"Explanation: {alert['explanation']}\n"
                )
                for alert in alerts
            ]
        )

        try:
            result = llm_client.create_structured_output(
                instructions=BRIEF_SUMMARY_INSTRUCTIONS,
                user_input=prompt,
                schema_name="bellwether_brief_summary",
                schema=BRIEF_SUMMARY_SCHEMA,
            )
        except LLMClientError:
            return None

        summary = result.get("summary")
        if not isinstance(summary, str) or not summary.strip():
            return None
        return summary.strip()


llm_analysis_service = LLMAnalysisService()
