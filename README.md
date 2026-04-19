# 🧠 The Logic Inquisitor

> **Don't get the answer. Get the insight.**

A production-grade **Multi-Agent AI ecosystem** that transforms programming education from passive answer-consumption into active Socratic investigation — built for the Agenticthon Hackathon using 100% free tools.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://logic-inquisitor.streamlit.app)
&nbsp;
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Gemini](https://img.shields.io/badge/Google_Gemini-1.5_Flash-orange)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2.x-green)
![License](https://img.shields.io/badge/License-MIT-purple)
![Cost](https://img.shields.io/badge/Cost-$0.00-brightgreen)

---

## The Problem

Most developers today paste broken code into AI tools and receive full solutions.
The result: **learned helplessness** — developers who can use AI but cannot think independently.

CS50's Duck Debugger is a step forward, but it is a single-agent, single-turn, unstructured system with no pattern recognition, no Socratic scaffolding, and no architectural intelligence.

**The Logic Inquisitor never gives you the answer.**

---

## The Solution

Five specialized AI agents, orchestrated by LangGraph, work in sequence to:

1. **Detect** your language and context with sub-second precision (The Linguist)
2. **Classify** your bug type from a 14-type taxonomy with severity scoring (The Pathologist)
3. **Guide** you through a Socratic 3-tier hint ladder toward self-discovery (The Socrates)
4. **Remember** your session patterns and build your learning profile (The Archivist)
5. **Synthesize** all outputs into the Three-Output Contract (The Inquisitor)

---

## Architecture

```
User Input (code / error log / logic problem)
                     │
                     ▼
        ┌────────────────────────┐
        │     THE INQUISITOR     │
        │   (LangGraph Master)   │
        └───────────┬────────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │      THE LINGUIST     │  ← Language & context detection
        │   gemini-1.5-flash    │  ← < 800ms target
        └───────────┬───────────┘
                    │
                    ▼
        ┌───────────────────────┐
        │    THE PATHOLOGIST    │  ← Bug taxonomy classification
        │   gemini-1.5-flash    │  ← 14-type bug taxonomy
        └─────────┬─────┬───────┘
                  │     │ (parallel)
          ┌───────┘     └──────────┐
          ▼                        ▼
┌──────────────────┐    ┌──────────────────────┐
│   THE SOCRATES   │    │    THE ARCHIVIST      │
│  3-tier hints    │    │  Session memory       │
│  never reveals   │    │  Pattern recognition  │
│  the answer      │    │  (activates at 3+)    │
└──────────────────┘    └──────────────────────┘
          │                        │
          └──────────┬─────────────┘
                     ▼
         THREE-OUTPUT CONTRACT
    ┌──────────────────────────────┐
    │  1. Detected Context         │  ← Language, confidence, signals
    │  2. Problem Topology         │  ← Bug type, severity, complexity
    │  3. Socratic Guidance        │  ← Tier-locked hints, concept link
    └──────────────────────────────┘
```

---

## The Three-Output Contract

Every interaction produces **exactly three outputs** — no more, no less:

| Output | Contents |
|--------|----------|
| **Detected Context** | Language + confidence score + framework + input type + quality signals |
| **Problem Topology** | Bug type (14-type taxonomy) + category + complexity tier + severity matrix |
| **Socratic Guidance** | 3-tier hint ladder + concept documentation link |

---

## The Socratic Hint Ladder

```
TIER I   ● Conceptual Nudge    (always shown first)
           "What does your program assume about this data
            that might not always be true?"

TIER II  ○ Structural Pointer  (unlocked on first "I'm stuck")
           "Consider the moment your loop decides it has
            finished — what exactly is it checking?"

TIER III ○ Minimal Unlock      (nuclear option — third escalation only)
           "What happens to your boundary check when the
            index equals the exact size of the collection?"
```

The answer is **never** revealed. The developer must earn the insight.

---

## Bug Taxonomy (14 Types)

`null_dereference` · `off_by_one` · `infinite_loop` · `stack_overflow` ·
`race_condition` · `memory_leak` · `type_mismatch` · `scope_error` ·
`logic_inversion` · `missing_base_case` · `unhandled_exception` ·
`state_mutation` · `async_misuse` · `algorithm_complexity`

---

## Tech Stack

| Layer | Technology | Version | Cost |
|-------|-----------|---------|------|
| Language | Python | 3.11.x | Free |
| LLM API | Google Gemini 1.5 Flash | latest | **Free** (1M tokens/day) |
| Agent Orchestration | LangGraph | 0.2.14 | Free |
| Type Safety | Pydantic | 2.7.4 | Free |
| UI Framework | Streamlit | 1.36.0 | Free |
| Session Memory | FAISS | 1.8.0 | Free |
| Deployment | Streamlit Community Cloud | — | **Free** |
| **Total cost** | | | **$0.00** |

---

## Differentiation vs CS50 Duck

| Feature | CS50 Duck | The Logic Inquisitor |
|---------|-----------|---------------------|
| Architecture | Single agent | 5 specialized agents (LangGraph) |
| Output structure | Freeform chat | Enforced Three-Output Contract |
| Hint system | Unstructured | Tier-locked Socratic ladder |
| Bug classification | None | 14-type taxonomy + severity matrix |
| Session memory | None | Pattern tracking + learning profile |
| Language detection | Prompt assumption | Dedicated Linguist agent |
| Cost | Free (CS50 only) | Free (anyone) |

---

## Quick Start

### Prerequisites
- Python 3.11 ([download](https://www.python.org/downloads/release/python-3119/))
- Git ([download](https://git-scm.com/download/win))
- Free Gemini API key ([get one](https://aistudio.google.com/app/apikey))

### Local Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/logic-inquisitor.git
cd logic-inquisitor

# 2. Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run the app
streamlit run app.py
```

Open your browser to **http://localhost:8501**

### Deploy Free (Streamlit Community Cloud)

1. Push code to GitHub (public repo)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub → New app → select repo → main file: `app.py`
4. Add secret: `GEMINI_API_KEY = "your_key_here"`
5. Deploy → live in 2 minutes

**Live URL:** https://logic-inquisitor.streamlit.app

---

## Project Structure

```
logic-inquisitor/
├── app.py                     ← Streamlit entry point (all UI)
├── requirements.txt           ← Exact package versions
├── .env.example               ← Environment template
├── .gitignore
├── README.md
├── LICENSE
│
├── agents/
│   ├── orchestrator.py        ← Agent 1: LangGraph pipeline
│   ├── linguist.py            ← Agent 2: Language detection
│   ├── pathologist.py         ← Agent 3: Bug classification
│   ├── socrates.py            ← Agent 4: Hint ladder + escalation
│   └── archivist.py           ← Agent 5: Session memory
│
├── models/
│   └── schemas.py             ← All Pydantic models
│
├── prompts/
│   └── agent_prompts.py       ← System prompts for all 5 agents
│
├── utils/
│   ├── gemini_client.py       ← Gemini API + tenacity retry
│   ├── json_parser.py         ← Safe LLM response parsing
│   └── session.py             ← Streamlit session helpers
│
├── demo/
│   └── examples.py            ← 4 pre-loaded judge examples
│
└── assets/
    └── style.css              ← Academic Terminal dark theme
```

---

## Demo Examples

Pre-loaded for judges — no typing required:

| Example | Language | Bug Type |
|---------|----------|----------|
| Array Boundary Bug | C | `off_by_one` |
| NullPointerException | Java | `null_dereference` |
| Fibonacci Recursion | Python | `missing_base_case` |
| Kadane's Algorithm | Logic Problem | `algorithm_complexity` |

---

## Pitch Points

- **Multi-agent specialization** — each agent has one domain of mastery, not a monolith
- **Enforced contract** — Three-Output Contract on every single interaction, guaranteed
- **Socratic by design** — the system is architecturally incapable of giving the answer
- **Pattern memory** — The Archivist builds a learning profile across submissions
- **Agenticthon-native** — uses the exact stack recommended by the Skills Program (Gemini + LangGraph + Pydantic)
- **100% free** — democratizes AI-powered education tooling

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built for the Agenticthon Hackathon 2025 · Powered by Google Gemini 1.5 Flash + LangGraph · Cost: $0.00*
