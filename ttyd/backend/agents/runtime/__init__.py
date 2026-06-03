# backend/agents/runtime/
# ======================
# This package provides the core runtime for the RAG-based assistant.
#
# Key components:
# - context.py: Manages conversation state (history, documents, metadata)
# - llm_async.py: Asynchronous interface to Bedrock LLMs (Nova Pro, etc.)
# - agent.py: Base agent abstraction
# - orchestrator.py: Main orchestrator that combines tools and LLM
# - executor.py: Entry point for running the assistant
