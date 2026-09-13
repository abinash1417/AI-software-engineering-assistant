import json
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from tenacity import retry, wait_exponential, stop_after_attempt

from config import Config
from models import ReviewState, CodeSubmission


class ReviewPipeline:
    """Orchestrates a 4-agent code review workflow:
    Analyzer -> Bug Detective -> Test Generator -> Review Summarizer.
    """

    def __init__(self):
        self._model = ChatGroq(model=Config.MODEL_NAME, temperature=Config.MODEL_TEMPERATURE)
        self._graph = self._build_graph()

    
    @retry(wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT),
           stop=stop_after_attempt(Config.RETRY_MAX_ATTEMPTS))
    def _analyzer_node(self, state: ReviewState) -> dict:
        response = self._model.invoke([
            ("system", "You are a senior software engineer analyzing code structure. "
                       "Briefly describe: what this code does, its overall structure, and its apparent purpose. "
                       "Keep it to 3-4 sentences."),
            ("human", f"Language: {state['language']}\n\nCode:\n{state['code']}")
        ])
        return {"analysis": response.content}

    @retry(wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT),
           stop=stop_after_attempt(Config.RETRY_MAX_ATTEMPTS))
    def _bug_detective_node(self, state: ReviewState) -> dict:
        response = self._model.invoke([
            ("system", "You are a meticulous code reviewer focused on finding bugs, edge cases, "
                       "poor error handling, and bad practices. List issues as bullet points. "
                       "If the code is genuinely clean, say so honestly rather than inventing problems."),
            ("human", f"Language: {state['language']}\nContext: {state['analysis']}\n\nCode:\n{state['code']}")
        ])
        return {"issues": response.content}

    @retry(wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT),
           stop=stop_after_attempt(Config.RETRY_MAX_ATTEMPTS))
    def _test_generator_node(self, state: ReviewState) -> dict:
        response = self._model.invoke([
            ("system", f"You are a test engineer. Write 2-4 unit tests for the given {state['language']} code, "
                       "covering normal cases and at least one edge case. Return ONLY the test code, "
                       "with brief comments explaining what each test checks."),
            ("human", f"Code:\n{state['code']}")
        ])
        return {"tests": response.content}

    @retry(wait=wait_exponential(multiplier=1, min=Config.RETRY_MIN_WAIT, max=Config.RETRY_MAX_WAIT),
           stop=stop_after_attempt(Config.RETRY_MAX_ATTEMPTS))
    def _summary_node(self, state: ReviewState) -> dict:
        response = self._model.invoke([
            ("system", """You are a strict but fair engineering lead producing a code health report.
Based on the analysis and issues found, respond ONLY with valid JSON in this exact format:
{
  "overall_score": number from 1-10,
  "readability": number from 1-10,
  "error_handling": number from 1-10,
  "best_practices": number from 1-10,
  "summary": "2-3 sentence honest summary of the code's overall quality"
}
No text outside the JSON."""),
            ("human", f"Analysis: {state['analysis']}\n\nIssues found:\n{state['issues']}")
        ])
        return {"report_raw": response.content}

    # Graph 
    
    def _build_graph(self):
        builder = StateGraph(ReviewState)
        builder.add_node("analyzer", self._analyzer_node)
        builder.add_node("bug_detective", self._bug_detective_node)
        builder.add_node("test_generator", self._test_generator_node)
        builder.add_node("summarizer", self._summary_node)

        builder.add_edge(START, "analyzer")
        builder.add_edge("analyzer", "bug_detective")
        builder.add_edge("bug_detective", "test_generator")
        builder.add_edge("test_generator", "summarizer")
        builder.add_edge("summarizer", END)

        return builder.compile()

    
    # Public Interface
    
    def run(self, submission: CodeSubmission) -> ReviewState:
        if not submission.is_valid():
            raise ValueError("No code provided to review.")

        result = self._graph.invoke({
            "code": submission.code,
            "language": submission.language,
            "analysis": "",
            "issues": "",
            "tests": "",
            "report_raw": "",
            "report": {}
        })

        result["report"] = self._parse_report(result["report_raw"])
        return result

    @staticmethod
    def _parse_report(raw_text: str) -> dict:
        """Parse the summarizer's JSON output, with a safe fallback if parsing fails."""
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            return {
                "overall_score": None,
                "readability": None,
                "error_handling": None,
                "best_practices": None,
                "summary": "Could not parse a structured report. Raw output: " + raw_text[:300]
            }