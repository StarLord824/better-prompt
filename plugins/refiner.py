# """
# PLUGIN INTERFACE SPECIFICATION
# ===============================
# Create plugins in a 'plugins/' directory following this structure:

# File: plugins/promptrefiner.py
# -------------------------------
# def process_prompt(input_text: str, metadata: dict) -> dict:
#     '''Enhance prompt using AI or custom logic.'''
#     # Your processing logic here
#     return {
#         "context": "...",
#         "instruction": "...",
#         "examples": "...",
#         "constraints": "..."
#     }

# The main app will safely import and handle errors if plugins are missing or fail.
# """

# Future Feature Scope
# no plugins are built for now, to meet the hackathon criteria
# adding plugin would have required import of External LLM, which would break the condition/contraints

# def process_prompt(input_text: str, metadata: dict) -> dict:
#     """Enhance prompt with AI-powered refinement."""
#     # Your logic here (can call LangChain, OpenAI, etc.)
#     return {
#         "context": "Enhanced context...",
#         "instruction": "Refined instruction...",
#         "examples": "Better examples...",
#         "constraints": "Clearer requirements..."
#     }

# """What Happens:

# ✅ Plugin exists and works → Loaded successfully
# ⚠️ Plugin missing → Shows warning, continues
# ❌ Plugin crashes → Catches error, uses default analyzer"""