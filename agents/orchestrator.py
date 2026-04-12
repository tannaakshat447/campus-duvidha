"""
Orchestrator — Master Agent
Coordinates the 5-agent pipeline sequentially, catches failures gracefully,
logs each agent's response + latency, and returns a single AgentResult.
"""

import json
import time
import traceback
from dataclasses import dataclass, asdict
from typing import Optional

from config import OPENAI_API_KEY
from database.models import insert_agent_log


@dataclass
class AgentResult:
    """Unified result from the full agent pipeline."""
    category: str = ""
    confidence: float = 0.0
    priority: str = ""
    priority_reason: str = ""
    summary: str = ""
    department: str = ""
    routing_reason: str = ""
    sentiment: str = ""
    flagged: bool = False
    used_fallback: bool = False

    def to_dict(self) -> dict:
        return asdict(self)


def _use_llm() -> bool:
    """Check if we should use the LLM agents or fall back to heuristics."""
    return bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-your-key-here")


def _run_agent(agent_fn, agent_name: str, problem_id: int, *args, **kwargs) -> dict:
    """
    Run a single agent function, measure latency, log result, handle errors.
    Returns the agent's output dict or raises if critical.
    """
    input_text = str(args[0]) if args else ""
    start = time.time()

    try:
        result = agent_fn(*args, **kwargs)
        latency_ms = (time.time() - start) * 1000

        insert_agent_log(
            problem_id=problem_id,
            agent_name=agent_name,
            input_text=input_text[:500],  # Truncate for DB
            output_json=json.dumps(result),
            latency_ms=round(latency_ms, 1),
        )

        return result

    except Exception as e:
        latency_ms = (time.time() - start) * 1000
        error_info = {"error": str(e), "traceback": traceback.format_exc()[:300]}

        insert_agent_log(
            problem_id=problem_id,
            agent_name=f"{agent_name} [FAILED]",
            input_text=input_text[:500],
            output_json=json.dumps(error_info),
            latency_ms=round(latency_ms, 1),
        )

        raise


def run_pipeline(complaint_text: str, problem_id: int) -> AgentResult:
    """
    Execute the full 5-agent pipeline on a complaint.
    Falls back to heuristics per-agent if LLM fails or no API key.
    """
    result = AgentResult()
    use_llm = _use_llm()

    if not use_llm:
        result.used_fallback = True

    # ── Agent 1: Classifier ─────────────────────────────────────────────
    try:
        if use_llm:
            from agents.classifier_agent import classify
            cls_result = _run_agent(classify, "Classifier Agent", problem_id, complaint_text)
        else:
            from agents.fallback import classify_fallback
            cls_result = _run_agent(classify_fallback, "Classifier Agent [Fallback]", problem_id, complaint_text)

        result.category = cls_result.get("category", "Needs Manual Review")
        result.confidence = cls_result.get("confidence", 0.0)

    except Exception:
        from agents.fallback import classify_fallback
        cls_result = _run_agent(classify_fallback, "Classifier Agent [Emergency Fallback]", problem_id, complaint_text)
        result.category = cls_result.get("category", "Needs Manual Review")
        result.confidence = cls_result.get("confidence", 0.0)
        result.used_fallback = True

    # ── Agent 2: Priority ───────────────────────────────────────────────
    try:
        if use_llm:
            from agents.priority_agent import assign_priority
            pri_result = _run_agent(
                assign_priority, "Priority Agent", problem_id,
                complaint_text, result.category,
            )
        else:
            from agents.fallback import priority_fallback
            pri_result = _run_agent(
                priority_fallback, "Priority Agent [Fallback]", problem_id,
                complaint_text, result.category,
            )

        result.priority = pri_result.get("priority", "Medium")
        result.priority_reason = pri_result.get("reason", "")

    except Exception:
        from agents.fallback import priority_fallback
        pri_result = _run_agent(
            priority_fallback, "Priority Agent [Emergency Fallback]", problem_id,
            complaint_text, result.category,
        )
        result.priority = pri_result.get("priority", "Medium")
        result.priority_reason = pri_result.get("reason", "")
        result.used_fallback = True

    # ── Agent 3: Summarizer ─────────────────────────────────────────────
    try:
        if use_llm:
            from agents.summarizer_agent import summarize
            sum_result = _run_agent(summarize, "Summarizer Agent", problem_id, complaint_text)
        else:
            from agents.fallback import summarize_fallback
            sum_result = _run_agent(summarize_fallback, "Summarizer Agent [Fallback]", problem_id, complaint_text)

        result.summary = sum_result.get("summary", complaint_text[:100])

    except Exception:
        from agents.fallback import summarize_fallback
        sum_result = _run_agent(summarize_fallback, "Summarizer Agent [Emergency Fallback]", problem_id, complaint_text)
        result.summary = sum_result.get("summary", complaint_text[:100])
        result.used_fallback = True

    # ── Agent 4: Router ─────────────────────────────────────────────────
    try:
        if use_llm:
            from agents.router_agent import route
            rte_result = _run_agent(
                route, "Router Agent", problem_id,
                result.category, result.priority, result.summary,
            )
        else:
            from agents.fallback import route_fallback
            rte_result = _run_agent(
                route_fallback, "Router Agent [Fallback]", problem_id,
                result.category,
            )

        result.department = rte_result.get("department", "Dean of Student Welfare")
        result.routing_reason = rte_result.get("routing_reason", "")

    except Exception:
        from agents.fallback import route_fallback
        rte_result = _run_agent(
            route_fallback, "Router Agent [Emergency Fallback]", problem_id,
            result.category,
        )
        result.department = rte_result.get("department", "Dean of Student Welfare")
        result.routing_reason = rte_result.get("routing_reason", "")
        result.used_fallback = True

    # ── Agent 5: Sentiment ──────────────────────────────────────────────
    try:
        if use_llm:
            from agents.sentiment_agent import analyze_sentiment
            sen_result = _run_agent(analyze_sentiment, "Sentiment Agent", problem_id, complaint_text)
        else:
            from agents.fallback import sentiment_fallback
            sen_result = _run_agent(sentiment_fallback, "Sentiment Agent [Fallback]", problem_id, complaint_text)

        result.sentiment = sen_result.get("sentiment", "Neutral")
        result.flagged = sen_result.get("flag", False)

    except Exception:
        from agents.fallback import sentiment_fallback
        sen_result = _run_agent(
            sentiment_fallback, "Sentiment Agent [Emergency Fallback]", problem_id, complaint_text,
        )
        result.sentiment = sen_result.get("sentiment", "Neutral")
        result.flagged = sen_result.get("flag", False)
        result.used_fallback = True

    return result
