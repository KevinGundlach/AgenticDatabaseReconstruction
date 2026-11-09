# Agentic Database Reconstruction

The Agentic Database Reconstruction project is to serve as part of a masters thesis titled **Automated Ontology Construction For Explainable Feature Discovery In Alloy Corrosion Resistance.**

The overall goal of the thesis is to develop an agentic framework capable of autonomously building a structured dataset of alloy corrosion metrics and environmental parameters, then develop machine learning models and heuristics to identify the impact that each parameter has on an alloy's corrosion resistance, and on pitting potential in particular.

This project uses LLM agents to extract corrosion-experiment data from research papers. The focus is **pitting potential**: finding the reported results, recovering the experimental conditions, and comparing the extracted data with the manually curated Citrine corrosion-resistant alloy (CRA) database.

## Agent Skills

Each agent skill lives in [`.agents/skills/`](.agents/skills/) and saves a JSON file plus a short report.

| Skill | What it does | Inputs |
|---|---|---|
| **1. [Register observations](.agents/skills/register-observations/SKILL.md)** (`register-observations`) | Finds pitting-potential results in plots, tables, and text. Records their values, units, sample labels, and exact locations. Combines repeated presentations when the paper supports that they describe the same result. | Paper PDF |
| **2. [Match observations to CRA](.agents/skills/match-observations-cra-database/SKILL.md)** (`match-observations-cra-database`) | Links observations to CRA row numbers, allowing for differences in units. Keeps uncertain matches as candidates rather than forcing an assignment. | PDF, observation registry, paper-specific CRA CSV |
| **3. [Enrich observations](.agents/skills/enrich-observations/SKILL.md)** (`enrich-observations`) | Adds alloy composition and preparation, electrolyte details, temperature, and test procedure for each observation. Keeps the registered pitting potential unchanged. | PDF and observation registry |

**Matching and enrichment work separately from the same registry.** Registration and enrichment read only the paper; the matching agent is the only one that sees CRA data. This lets us compare the extracted experimental details with CRA without giving the enrichment agent the answers.

Observation IDs connect the outputs. Large registries can be split into smaller batches while keeping those IDs. Ambiguous associations, conflicting source values, and extraction problems are recorded in the JSON and reports.

## Project structure

- `.agents/skills/`: The three skills, with their schemas, models, and validators.
- `papers/`: Research papers as PDFs.
- `citrine_database/`: Original CRA workbook and CSV exports. The `by_reference/` subfolder contains one pitting-potential CSV per paper.
- `observation_registry/`: Extracted outcomes and their source locations.
- `matched_observations/`: Links between observations and CRA rows.
- `enriched_observations/`: Alloy, electrolyte, and test details for each observation.
- `models/`: Python models used by the analysis scripts.
- `utils/`: Data-processing and PostgreSQL helpers.
- `analysis.py`: Exploratory analysis and database loading.
- `process_observations.py`: Helpers for selecting and loading observations.

Paper numbers connect the source files: a PDF beginning with `49_` corresponds to `citrine_database/by_reference/pitting_potential_49.csv`. The CSV's `Reference` column identifies the paper, and `No.` identifies the CRA row.

The folders above contain the current saved results. When running matching or enrichment, specify these output folders explicitly; their skill defaults use different names.

## Current progress

The three skills have been run across the available corpus of **77 papers**. Registry and enrichment JSONs are saved for all 77; matching JSONs cover the **61 papers** with both a PDF and a paper-specific CRA CSV. Some outputs are empty or have unresolved issues, so the companion reports are part of the results.

The next step is to normalize the extracted context values and measure agreement with CRA. Ontology learning and predictive modelling are later stages of the thesis.

## Working with the repository

Python dependencies are listed in `pyproject.toml` and can be installed with `uv sync`. Invoke the skills through an agent with visual PDF-reading tools; their Python scripts prepare and validate data rather than run an LLM themselves. See each skill's instructions for usage and validation commands.

The database utilities support SQL exploration. **The current `analysis.py` entry point drops and recreates `agenticdb`**, and the exploratory scripts still contain older paths and paper filters that need checking before use.
