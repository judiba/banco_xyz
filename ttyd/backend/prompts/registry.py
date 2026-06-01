from pathlib import Path

PROMPT_REGISTRY = {}

PROMPT_DIR = Path(__file__).parent


def load_prompts():
    for file in PROMPT_DIR.glob("*.md"):
        name = file.stem.split(".")[0]

        PROMPT_REGISTRY[name] = file.read_text()


load_prompts()


def get_prompt(name: str) -> str:
    if name not in PROMPT_REGISTRY:
        raise ValueError(f"Prompt '{name}' not registered")

    return PROMPT_REGISTRY[name]
