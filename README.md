# Structured Prompt Generator (Streamlit)

A bilingual prompt-building workspace for creating high-quality structured prompts with better UX and stronger guardrails.

## Quick Start

1. (Recommended) Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
4. (Optional) Run regression tests:
   ```bash
   python3 -m unittest discover -s tests
   ```

## What's Improved

- **Refactored architecture**
  - `app.py` now uses clear rendering helpers and session-state utilities.
  - `utils.py` handles normalization, scoring, validation, and prompt generation.
- **Better UX workflow**
  - Prompt workspace sidebar with real-time quality score.
  - Starter presets (EN/ZH) to quickly bootstrap real use cases.
  - Prompt insights tab with warnings and actionable suggestions.
  - Export both generated prompt (`.txt`) and full form state (`.json`).
- **Higher-quality prompt output**
  - Stable action normalization from list or multiline text.
  - Browse action URL validation.
  - Cleaner prompt rendering without accidental indentation.
- **Repository hygiene**
  - Added `.gitignore`.
  - Removed tracked `__pycache__` artifacts.
  - Added unit tests for critical prompt logic.

## Project Structure

- `app.py` — Streamlit UI and interaction flow
- `utils.py` — prompt generation, validation, presets, normalization
- `tests/test_utils.py` — regression tests
- `prompt_engineering_generator.tsx` — React prototype component
- `requirements.txt` — Python dependencies

## Feature Highlights

- Bilingual interface (English / 中文)
- Section-based prompt builder (Role / Task / Action / Context / Output)
- Dynamic multi-action editing (Search / Lookup / Browse)
- Prompt quality score and missing-required-field check
- Prompt preview with download and JSON export
