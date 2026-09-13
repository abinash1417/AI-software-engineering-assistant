# 🛠️ AI Software Engineering Assistant

An automated code review pipeline that analyzes code, detects bugs and bad practices, generates unit tests, and produces a structured "Code Health Report" — similar in spirit to how tools like SonarQube or CodeRabbit work, built as a multi-agent LLM pipeline.

## What it does

Paste any code snippet and the assistant runs it through four specialized stages:

1. **Analyzer** — understands what the code does and its overall structure
2. **Bug Detective** — finds real bugs, edge cases, and poor practices (instructed to be honest — it won't invent issues in genuinely clean code)
3. **Test Generator** — writes unit tests covering normal and edge cases
4. **Summarizer** — produces a structured JSON score card: Overall Score, Readability, Error Handling, and Best Practices, each rated out of 10

## Why a multi-agent pipeline instead of one prompt

A single "review this code" prompt tends to produce shallow, generic feedback. Splitting the work into focused stages — each with a narrow job — produces sharper results: the Bug Detective isn't distracted by writing tests, the Test Generator isn't distracted by scoring. This mirrors how real code review actually works across a team, just automated.

## Architecture

```
User pastes code + selects language
       |
       v
Analyzer Agent (what does this code do?)
       |
       v
Bug Detective Agent (real issues, edge cases, bad practices)
       |
       v
Test Generator Agent (unit tests, normal + edge cases)
       |
       v
Summarizer Agent (structured JSON: scores + summary)
       |
       v
Code Health Report displayed in UI
```

## Tech Stack

- **LLM:** Groq (`openai/gpt-oss-120b`) via LangChain
- **Orchestration:** LangGraph (linear StateGraph pipeline)
- **Frontend:** Streamlit
- **Resilience:** `tenacity` for automatic retry on API rate limits
- **Structured output:** JSON-based scoring with graceful fallback if parsing fails

## Project Structure

```
ai-software-engineering-assistant/
├── app.py                # Streamlit UI
├── config.py              # Centralized settings
├── models.py               # CodeSubmission and ReviewState data structures
├── pipeline.py              # ReviewPipeline class - the 4-agent LangGraph workflow
├── static/
│   └── style.css              # UI styling
└── requirements.txt
```

## Running Locally

```bash
git clone https://github.com/abinash1417/ai-software-engineering-assistant.git
cd ai-software-engineering-assistant
python -m venv venv
venv\Scripts\activate   # or source venv/bin/activate on Mac/Linux
pip install -r requirements.txt
```

Create a `.env` file with:

```
GROQ_API_KEY=your_key_here
```

Then run:

```bash
streamlit run app.py
```

## Known Limitations

- Reviews are limited to single code snippets, not entire repositories or multi-file projects
- Generated tests are not automatically executed — running arbitrary submitted code is a genuine security risk this project deliberately avoids
- Groq's free tier rate limit (8,000 tokens/minute) may cause delays on very long code submissions

## What I'd Add Next

- Multi-file review support with cross-file dependency awareness
- Sandboxed test execution to actually run and validate generated tests
- Diff-based review mode (review only changed lines, like a real PR review)