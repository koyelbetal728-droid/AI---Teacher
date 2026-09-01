# __init__.py
"""
AI agents used by the AI Teacher.

Agents are responsible for specialized teaching tasks:

- Lesson planning
- Interactive teaching
- Answer evaluation
- Misconception detection
- Personalized recommendations

Each agent uses the shared LLM and RAG services instead of
communicating directly with the model provider.
"""