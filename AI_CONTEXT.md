# AI AGENCY PROJECT CONTEXT
This document defines the architectural standards, tech stack, and security rules for the AI Agency project.[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
ANY AI Assistant (Cursor, Continue, Kilo, Copilot) MUST read this before generating code.

## 🚨 CRITICAL SECURITY RULES
1. **NEVER** commit `.env` files to Git.[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
2. **ALWAYS** check `.gitignore` before adding new file types.[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
3. Secrets (API Keys) must ONLY be loaded via `os.environ` from `python-dotenv`.[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]

## 🛠 TECH STACK & ENVIRONMENT[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
- **OS:** Windows 10/11 (Requires Signal Patch for CrewAI).
- **Python:** 3.11 (Strict requirement).
- **Framework:** CrewAI (Latest stable).[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
- **LLM Strategy:** Multi-Model Hybrid.
  - **Planner/Manager:** GPT-4o / DeepSeek-V3 (High Logic).
  - **Coder/Speed:** Groq (Llama-3.3-70b) / DeepSeek-V3 (Fast).
  - **Researcher:** Gemini-1.5-Flash (High Context/Free).

## 📂 DIRECTORY STRUCTURE
AI_Agency/
├── .env                # API Keys (Ignored by Git)
├── Agency_Brain/       # Global Knowledge Base (Markdown files)
│   ├── tech/           # Coding standards
│   └── marketing/      # Tone of Voice
└── Projects/           # Client Work
    └── {ClientName}/   # Specific Project
        ├── configs/    # Agent Prompts (.md)
        ├── output/     # Results
        └── run.py      # Entry point script[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]

## 💻 CODING STANDARDS (PYTHON)
1. **Windows Patch:** Every `run.py` MUST start with this block to prevent interrupt errors:
   ```python
   import sys
   if sys.platform.startswith('win'):
       import asyncio
       asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
   ```[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
2. **Path Handling:** Always use relative paths (`../../`) to access `.env` or `Agency_Brain`.[[1](https://www.google.com/url?sa=E&q=https%3A%2F%2Fgithub.com%2FBobrik27%2FAi_Agency)]
3. **Async Execution:** Prefer `async_execution=True` for parallel tasks.