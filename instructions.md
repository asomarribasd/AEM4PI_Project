---

# Project Idea and Implementation Instructions (English)

## Project Title

**AI Multi-Agent Lost Pet Intelligence System**

---

## Project Context

You are building an AI-powered feature for an existing **lost pets web platform**. The goal is to move beyond a passive listing system and demonstrate a **next-generation multi-agent AI system** that actively assists users by analyzing photos, text descriptions, and location data to improve lost pet recovery outcomes.

This project is designed as a **proof-of-concept multi-agent system** that demonstrates:

* Real user value
* Multi-agent collaboration
* Multimodal AI usage
* Production-ready engineering practices

---

## 1. Problem Statement (for proposal.md / README – 150+ words)

When a pet goes missing, time and information quality are critical. However, most lost-pet platforms rely entirely on users to manually create reports, resulting in:

* Incomplete or vague descriptions
* Low-quality or poorly explained photos
* Ambiguous locations
* Difficulty determining whether a reported sighting matches a lost pet

People who believe they have seen a lost pet often lack confidence in whether it is truly the same animal, leading to delayed or missed reunifications. Existing systems are **passive databases**, not intelligent assistants.

This problem cannot be solved with a single AI call because it requires:

* Multimodal analysis (images + text)
* Structured data validation
* Semantic similarity search across historical reports
* Explainable decision-making for non-technical users

The lack of intelligent matching and explanation results in lost opportunities during the most critical recovery window.

---

## 2. Target Users

* Pet owners reporting lost pets
* Members of the public reporting sightings
* (Optional future extension) Rescue organizations and shelters

---

## 3. Solution Overview (Multi-Agent Approach – 150+ words)

This project implements a **multi-agent AI system** that collaborates to enrich reports, detect possible matches, and provide actionable explanations to users.

Instead of a single general-purpose agent, the system uses **three specialized agents**, each optimized for a distinct responsibility:

1. **Visual & Text Extraction Agent**
   Responsible for processing multimodal inputs (pet images + user text) and extracting structured attributes.

2. **Match & Similarity Agent**
   Responsible for identifying potential matches using a Vector Store and semantic similarity search across existing lost pet and sighting reports.

3. **Decision & Explanation Agent**
   Responsible for interpreting similarity scores, deciding whether a match is meaningful, and generating a human-friendly explanation and recommended next steps.

These agents collaborate sequentially in a pipeline where each agent builds on the previous agent’s output. This design ensures specialization, traceability, and explainability—capabilities that are not achievable with a single-agent solution.

---

## 4. Multi-Agent Architecture (Required)

### Agent 1: Visual & Text Extractor Agent

**Responsibilities:**

* Accept pet images and textual descriptions
* Use Image-to-Text (Vision model) to extract visual attributes:

  * Species
  * Approximate size
  * Primary colors
  * Distinctive features (spots, collars, scars)
* Normalize and clean user text
* Output structured data validated using Pydantic

**Output Example (Pydantic model):**

```json
{
  "species": "dog",
  "size": "medium",
  "colors": ["white", "brown"],
  "distinctive_features": ["black spot on left ear"],
  "last_seen_location": {
    "province": "San José",
    "canton": "Escazú",
    "district": "San Rafael"
  }
}
```

---

### Agent 2: Match & Similarity Agent

**Responsibilities:**

* Embed structured pet descriptions
* Query a Vector Store (Chroma / FAISS)
* Compare against:

  * Lost pet reports
  * Sightings reported by other users
* Generate similarity scores
* Identify top candidate matches with explanations

**Output Example:**

```json
{
  "match_id": "PET-1023",
  "similarity_score": 0.82,
  "matching_reasons": [
    "same color pattern",
    "same canton",
    "distinctive ear marking"
  ]
}
```

---

### Agent 3: Decision & Explanation Agent

**Responsibilities:**

* Interpret similarity scores
* Decide whether to notify users
* Generate a clear explanation for non-technical users
* Suggest next steps (contact owner, verify name response, etc.)

**Example User Output:**

> “This pet matches in size, color, and a distinctive black spot on the left ear. The sighting occurred 1.2 km from the last reported location three days ago. We recommend contacting the report owner to confirm identity.”

---

## 5. Collaboration Pattern

* **Sequential pipeline**
* Agent 1 → Agent 2 → Agent 3
* Each agent consumes the validated output of the previous agent
* Data flow is explicit and traceable

---

## 6. Technology Stack (Minimum Requirements)

This project MUST integrate at least **two** of the following in a meaningful way:

* **LangChain** – agent orchestration and task delegation
* **Vector Store** (Chroma or FAISS) – similarity search
* **Image-to-Text** – pet image analysis
* **Pydantic** – strict input/output validation
* **Langfuse** (optional but recommended) – tracing, metrics, performance monitoring

---

## 7. Input / Output Requirements

### Input (Multimodal)

* Up to 5 pet images
* Free-text description
* Structured location (province, canton, district)

### Output

* Enriched structured pet profile
* Ranked list of possible matches
* Human-readable explanation
* Recommended actions

---

## 8. Success Criteria (5+ measurable outcomes)

* ≥85% correct match identification on test cases
* Reduction in incomplete reports
* Faster user decision-making
* Improved user confidence (qualitative feedback)
* Reduced false-positive matches

---

## 9. Repository Structure (MANDATORY)

```
/src
  /agents
    visual_extractor_agent.py
    similarity_agent.py
    decision_agent.py
  /models
    pet_models.py
    match_models.py
  /utils
    image_utils.py
    embedding_utils.py
  main.py

/docs
  proposal.md

/examples
  valid_case_1/
  valid_case_2/
  edge_case_1/
  invalid_case_1/
  invalid_case_2/

/README.md
/requirements.txt
/.env.example
/.gitignore
```

---

## 10. Implementation Constraints (VERY IMPORTANT)

* Minimum **2 specialized agents** (3 recommended)
* At least **8 well-named functions**
* Type hints throughout
* Pydantic models with validators
* Environment variables only (no hardcoded keys)
* Error handling for:

  * Invalid images
  * Missing fields
  * API failures
* Clear logging
* Runnable end-to-end from `main.py`

---

## 11. Deliverables Summary

The final repository must include:

* 2–3 page proposal (proposal.md or README section)
* Fully functional multi-agent system
* Separate agent implementations
* Sample inputs (5+ cases)
* Comprehensive README
* requirements.txt with pinned versions
* .env.example template

---

## 12. Why This Project Fits the Evaluation Rubric

* Solves a real, non-trivial problem
* Justifies multi-agent architecture
* Demonstrates multimodal AI
* Uses advanced tooling correctly
* Shows production-level engineering judgment


