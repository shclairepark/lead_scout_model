# Lead Scout Model

Lead Scout is an intelligent scoring and engagement engine designed to help SaaS founders and sales teams identify high-intent leads that align with their specific business context.

The system goes beyond generic scoring by analyzing the semantic fit between a sender's profile and a lead's background, combined with a temporal analysis of engagement signals.

## 🚀 Quick Start

### 1. Installation
Ensure you have Python 3.9+ and the required dependencies installed:
```bash
pip install torch numpy
```

### 2. Generate Test Data
Populate `data/leads.csv` with a dataset of 100+ public tech profiles and diverse signals:
```bash
python data/generate_leads.py
```

### 3. Run Ingestion Pipeline
Process the leads through the full engine to see scoring and automated engagement decisions:
```bash
PYTHONPATH=. python data/ingest_csv.py data/leads.csv
```

## 🔍 Core Functionality

### Data Ingestion & Enrichment
The model consumes lead data from CSV formats and automatically enriches profiles with industry heuristics and ICP (Ideal Customer Profile) alignment.

### Context-Aware Scoring
The engine evaluates leads based on:
- **Semantic Fit**: Measures how well a lead's industry and role align with the sender's specific value proposition.
- **Intent Analysis**: Weights real-time signals (demo requests, visits, social engagement) using an attention mechanism to prioritize high-value actions.
- **Recency Decay**: Automatically de-prioritizes older signals to ensure focus remains on active leads.

### Automated Engagement
Qualified leads (High Intent + High Fit) trigger automated "Conversation Starters"—personalized message drafts based on the specific signals detected.

## 🛠️ Development & Testing

### Running Tests
The project includes a comprehensive suite of 110+ unit and end-to-end tests.
```bash
pytest tests/ -v
```

### Signal Monitoring Demo
To simulate or view the signal collection logic in action:
```bash
PYTHONPATH=. python tests/run_signals.py --simulate
```

## 📁 Directory Structure
- `data/`: CSV datasets and data generation scripts.
- `src/`: Core engine implementation (Pipeline, Scoring, Context, Enrichment).
- `tests/`: Unit tests, E2E tests, and signal simulation scripts.
- `notebooks/`: Research and model prototyping.
