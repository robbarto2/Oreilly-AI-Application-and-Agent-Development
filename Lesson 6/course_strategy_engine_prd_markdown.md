# AI-Powered Course Strategy Engine
## Product Requirements Document (PRD)

---

# 1. Product Vision

The Course Strategy Engine is an AI-native strategic curriculum design platform built for experienced technical educators.

The system helps identify, prioritize, and develop high-value future courses in:

- Artificial Intelligence
- Agentic AI
- Data Science
- AI Infrastructure
- Enterprise AI
- AI Security
- Developer Tooling
- AI Operations

The platform continuously monitors the AI ecosystem while understanding previously created course material, books, labs, GitHub repositories, conference talks, and strategic proposals.

The goal is to answer:

- What should we teach next?
- Which AI topics are accelerating fastest?
- What gaps exist in our catalog?
- Which trends align with our expertise?
- Which ideas have enterprise demand?
- Which adjacent topics naturally extend our current material?

The product is not merely a recommendation engine.

It is an:

# AI Curriculum Strategy Copilot

The system combines:

- conversational AI
- agentic workflows
- research agents
- long-term memory
- recommendation systems
- strategic reasoning
- structured outputs
- interactive workspace UX

---

# 2. Product Goals

## Primary Goals

- Identify emerging AI course opportunities early
- Continuously monitor AI trends and ecosystems
- Understand existing educational material deeply
- Recommend future course investments
- Explain WHY recommendations are strategically strong
- Generate draft course outlines and learning paths
- Support brainstorming and strategic planning workflows
- Build reusable agentic AI infrastructure

---

## Secondary Goals

- Experiment with OpenClaw
- Explore multi-agent orchestration
- Build long-term memory systems
- Implement research agents
- Explore structured reasoning workflows
- Build a strong conversational AI UX
- Create reusable educational intelligence tooling

---

# 3. Core Product Philosophy

The system should behave like:

- a research analyst
- a curriculum strategist
- an AI architect
- a brainstorming partner
- a competitive intelligence system

The product should feel:

- conversational
- evidence-based
- interactive
- strategic
- highly visual
- reasoning-oriented

The chatbot is the PRIMARY interface.

The system should generate:

- recommendations
- course ideas
- outlines
- strategic analyses
- roadmap proposals
- curriculum graphs
- trend reports
- interactive artifacts

---

# 4. Core UX Vision

## Primary Interaction Model

The product is fundamentally:

# A conversational strategic workspace

Users interact with the system through natural language.

Example prompts:

```text
What advanced enterprise AI courses should we build next?
```

```text
What gaps exist in our current catalog?
```

```text
Brainstorm follow-on courses from our MCP material.
```

```text
Compare our content against current O'Reilly offerings.
```

```text
What AI topics are accelerating fastest in the enterprise?
```

---

# 5. UX Architecture

```text
Chat Interface
    ↓
Orchestrator Agent
    ↓
Specialized Agents
    ↓
Structured Outputs
    ↓
Interactive Workspace / Canvas
```

---

# 6. Core UX Components

## A. Conversational Chat Interface

The main interface for:

- brainstorming
- research
- recommendations
- course design
- strategic planning
- curriculum analysis

Features:

- streaming responses
- citations
- reasoning traces
- expandable evidence
- agent progress updates
- long-context conversations

---

## B. Interactive Workspace / Canvas

Users can pin generated artifacts onto a visual workspace.

Examples:

- course proposals
- trend analyses
- outlines
- architecture diagrams
- curriculum trees
- strategy maps
- recommendation cards

This should feel similar to:

- Miro
- AI Canvas
- Notion AI
- React Flow based systems

---

## C. Structured Artifact Cards

The chatbot should generate structured cards rather than only plain text.

Examples:

### Trend Card

```json
{
  "topic": "MCP Security",
  "momentum": "high",
  "enterprise_interest": "high",
  "competition": "low"
}
```

---

### Course Proposal Card

```json
{
  "course_title": "Enterprise Agentic AI Security",
  "audience": "senior architects",
  "duration": "4 hours",
  "labs": [
    "MCP policy enforcement",
    "Prompt injection defense"
  ]
}
```

---

# 7. Core User Workflow

```text
External Sources
    ↓
Research Agents
    ↓
Trend Extraction
    ↓
Knowledge Graph / Memory
    ↓
Gap Analysis Engine
    ↓
Recommendation Engine
    ↓
Course Proposal Generator
    ↓
Interactive Workspace
```

---

# 8. Content Ingestion Strategy

The system must deeply understand existing educational material.

This is one of the most important architectural components.

The platform should build an:

# Internal Expertise Graph

The graph represents:

- what has already been taught
- how deeply topics are covered
- audience targeting
- implementation maturity
- strategic themes
- future proposals
- abandoned ideas
- adjacent opportunities

---

# 9. Content Sources

## Tier 1 Sources

| Source | Importance |
|---|---|
| PowerPoint decks | extremely high |
| Word proposals | extremely high |
| Books/manuscripts | extremely high |
| GitHub repos | extremely high |

---

## Tier 2 Sources

| Source | Importance |
|---|---|
| PDFs | high |
| Markdown notes | high |
| YouTube transcripts | medium |
| Conference abstracts | medium |

---

# 10. Supported File Types

## Initial MVP Support

- PPTX
- DOCX
- PDF
- Markdown
- GitHub repositories
- YouTube transcripts

---

# 11. Important Design Principle

DO NOT flatten documents into raw text blobs.

The system must preserve semantic structure.

Example:

```text
Document
    → Sections
        → Slides
            → Notes
                → Concepts
```

This hierarchy becomes critical for reasoning.

---

# 12. PowerPoint Ingestion Pipeline

```text
PPTX File
    ↓
Slide Extraction
    ↓
Text + Notes + Images
    ↓
Slide Classification
    ↓
Topic Extraction
    ↓
Embedding + Metadata
    ↓
Curriculum Graph
```

---

# 13. PowerPoint Data Extraction

Extract:

- slide titles
- bullet points
- speaker notes
- tables
- diagrams
- images
- architecture patterns
- section hierarchy

Speaker notes are especially valuable.

---

# 14. Word Proposal Ingestion

DOCX proposals contain:

- future ideas
- strategic thinking
- market positioning
- educational gaps
- abandoned concepts
- roadmap thinking

The system should distinguish:

| Type | Meaning |
|---|---|
| Published course | delivered material |
| Proposal | future opportunity |
| Experimental notes | exploratory work |
| Conference talk | lightweight coverage |

---

# 15. Recommended Metadata Schema

```json
{
  "content_id": "course_001",
  "title": "Building AI Agents with LangGraph",
  "type": "course",
  "source": "OReilly",
  "authors": ["Rob Barton", "Jerome Henry"],
  "topics": [
    "LangGraph",
    "MCP",
    "multi-agent systems"
  ],
  "difficulty": "advanced",
  "audience": "enterprise engineers",
  "duration_hours": 4,
  "frameworks": [
    "LangChain",
    "FastAPI",
    "Claude"
  ],
  "coverage_depth": {
    "LangGraph": 9,
    "MCP": 6,
    "RAG": 4
  }
}
```

---

# 16. Coverage Depth Model

The system should NOT merely know:

```text
Topic exists
```

It should know:

```text
How deeply is this topic covered?
```

Example:

| Topic | Depth |
|---|---|
| RAG | 9/10 |
| LangGraph | 8/10 |
| MCP | 5/10 |
| OpenClaw | 1/10 |

---

# 17. Coverage Depth Signals

Initial heuristics:

| Signal | Meaning |
|---|---|
| Slide count | breadth |
| Labs | implementation depth |
| Code volume | maturity |
| Repeated mentions | emphasis |
| Dedicated module | importance |
| Advanced terminology | sophistication |

---

# 18. External Trend Monitoring

The platform continuously monitors:

- GitHub
- YouTube
- Reddit
- Hacker News
- blogs
- conference agendas
- technical news
- O'Reilly catalog
- Coursera
- Udemy
- research papers

The system tracks:

- growth velocity
- sentiment
- enterprise adoption
- tooling momentum
- ecosystem maturity
- community engagement

---

# 19. Recommended Agent Architecture

## Orchestrator Agent

Responsibilities:

- route workflows
- coordinate agents
- manage memory
- aggregate outputs
- manage structured artifacts

Recommended:

- LangGraph
- OpenClaw

---

## Specialized Agents

### A. Trend Research Agent

Responsibilities:

- monitor GitHub
- analyze YouTube
- summarize Reddit
- detect emerging topics

Outputs:

```json
{
  "topic": "Model Context Protocol",
  "growth_score": 92,
  "sentiment": "positive",
  "velocity": "high"
}
```

---

### B. Competitive Intelligence Agent

Analyzes:

- O'Reilly
- Coursera
- Udemy
- YouTube educators
- conference ecosystems

Detects:

- saturation
- gaps
- pricing
- differentiation opportunities

---

### C. Internal Knowledge Agent

Responsibilities:

- retrieve existing material
- analyze coverage
- identify strengths
- infer expertise areas

---

### D. Gap Analysis Agent

Compares:

```text
external trends
VS
internal expertise
```

Outputs:

- missing topics
- underserved niches
- adjacency opportunities

---

### E. Recommendation Agent

Ranks opportunities.

Example scoring dimensions:

| Factor | Weight |
|---|---|
| Trend Growth | 25% |
| Enterprise Demand | 20% |
| Expertise Alignment | 20% |
| Competitive Saturation | 15% |
| Revenue Potential | 10% |
| Technical Novelty | 10% |

---

### F. Outline Generation Agent

Generates:

- course titles
- modules
- labs
- exercises
- demos
- prerequisite maps

---

### G. Memory / Knowledge Graph Agent

Stores:

- historical recommendations
- prior discussions
- successful ideas
- rejected ideas
- topic trajectories
- strategic evolution

---

# 20. Important Product Insight

The system should NOT simply ask:

```text
What is trending?
```

It should ask:

```text
What is trending AND uniquely aligned
with our expertise?
```

This is the strategic differentiator.

---

# 21. Recommendation Logic

Example strategic reasoning:

```text
Current strengths:
- LangGraph
- MCP
- Agentic workflows

Emerging adjacent topic:
- Agent memory systems

Recommendation:
Persistent Memory Architectures for AI Agents
```

---

# 22. Example Use Cases

## Weekly Trend Briefing

```text
Summarize the top emerging AI education opportunities this week.
```

---

## Gap Analysis

```text
What important topics are missing from our current catalog?
```

---

## Course Expansion

```text
What advanced follow-on course fits after our AI fundamentals course?
```

---

## Conference Intelligence

```text
Analyze RSA, Cisco Live, and NeurIPS agendas.
```

---

## Draft Course Generator

```text
Generate a 4-hour course on AI observability.
```

---

# 23. Structured Outputs

The system should prefer structured outputs wherever possible.

Example:

```json
{
  "course_title": "Enterprise Agentic AI Security",
  "opportunity_score": 91,
  "market_momentum": "high",
  "competition": "medium",
  "recommended_modules": [
    "MCP Security",
    "Agent Isolation",
    "Policy Enforcement"
  ]
}
```

Structured outputs are critical for:

- rendering cards
- filtering
- ranking
- future automation
- reproducibility

---

# 24. Recommended Technical Stack

## Frontend

Recommended:

- React
- Next.js
- Tailwind
- Zustand
- React Flow
- Framer Motion

---

## Backend

Recommended:

- FastAPI
- WebSockets
- LangGraph orchestration
- structured JSON responses

---

## Databases

| Need | Technology |
|---|---|
| Structured metadata | PostgreSQL |
| Semantic search | pgvector |
| Knowledge graph | Neo4j |
| Cache | Redis |
| Object storage | S3 |

---

## Parsing Libraries

| Type | Tool |
|---|---|
| PPTX | python-pptx |
| DOCX | python-docx |
| PDFs | PyMuPDF |
| GitHub | GitPython |
| OCR | Tesseract |

---

# 25. Recommended Architecture

```text
                    ┌────────────────────┐
                    │ External Sources   │
                    │ GitHub/YouTube/etc │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Research Agents    │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Trend Extraction   │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Vector DB / Memory │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Gap Analysis Agent │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Recommendation     │
                    │ Engine             │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Outline Generator  │
                    └─────────┬──────────┘
                              ↓
                    ┌────────────────────┐
                    │ Chat + Workspace   │
                    └────────────────────┘
```

---

# 26. MVP Scope

## Initial MVP Features

### Chat Interface

Primary interaction model.

---

### Content Ingestion

Support:

- PPTX
- DOCX
- PDF
- Markdown
- GitHub repos

---

### Semantic Search

Embedding-based retrieval over:

- books
- slides
- labs
- proposals
- transcripts

---

### Trend Monitoring

Initially monitor:

- GitHub
- YouTube
- Reddit
- Hacker News

---

### Recommendation Engine

Generate:

- ranked ideas
- evidence
- opportunity scores
- gap analyses

---

### Draft Outline Generator

Generate:

- titles
- modules
- labs
- prerequisites

---

### Workspace / Canvas

Allow users to pin generated artifacts.

---

# 27. Future Enhancements

## Advanced Research Agents

- autonomous research sessions
- periodic trend monitoring
- long-horizon analysis
- persistent agent memory

---

## Multi-Agent Debate

Example:

```text
Trend Agent:
MCP security is accelerating.

Competitive Agent:
Competition is still low.

Enterprise Agent:
Enterprise demand is increasing rapidly.
```

---

## Curriculum Graph

```text
AI Fundamentals
   ↓
RAG
   ↓
Agentic AI
   ↓
Multi-Agent Systems
```

---

## Strategic Roadmapping

```text
If we invest heavily in agentic AI,
what should our 2-year roadmap be?
```

---

## Revenue Prediction

Estimate:

- market demand
- pricing
- audience size
- commercial viability

---

## Auto-Lab Generation

Generate:

- notebooks
- demos
- exercises
- datasets

---

## AI Video Analysis

Analyze:

- transcripts
- engagement
- audience sentiment
- topic acceleration

---

# 28. Development Phases

| Phase | Goal |
|---|---|
| Phase 1 | Content ingestion + embeddings |
| Phase 2 | External trend monitoring |
| Phase 3 | Recommendation engine |
| Phase 4 | Multi-agent orchestration |
| Phase 5 | Long-term memory |
| Phase 6 | Autonomous research workflows |

---

# 29. Important Design Principles

## Evidence-Based Recommendations

Every recommendation should cite:

- GitHub activity
- conference mentions
- Reddit growth
- YouTube momentum
- competitor analysis

---

## Explainability

Every recommendation must explain:

```text
WHY this course matters
WHY now
WHY we are uniquely positioned
```

---

## Human-In-The-Loop

The system is:

```text
An AI strategic copilot
NOT
A fully autonomous curriculum planner
```

---

## Artifact-Centric UX

The valuable outputs are:

- outlines
- strategy maps
- research summaries
- curriculum graphs
- proposals
- recommendation cards

NOT merely chat text.

---

# 30. Final Product Summary

The Course Strategy Engine is an AI-native strategic curriculum design platform that combines:

- conversational UX
- agentic AI workflows
- research agents
- long-term memory
- structured reasoning
- semantic retrieval
- recommendation systems
- interactive workspaces

The platform continuously analyzes:

- external AI ecosystems
- internal educational assets
- enterprise trends
- competitor positioning

to help experienced educators strategically decide:

# What courses to build next.

The system is designed to feel like:

- an AI research analyst
- a strategic curriculum planner
- a brainstorming partner
- an interactive knowledge workspace

for advanced AI education and enterprise technical training.

