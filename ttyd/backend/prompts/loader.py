from pathlib import Path

PROMPT_DIR = Path(__file__).parent


class PromptLoader:
    def __init__(self):
        self.cache = {}
        self.timestamps = {}

    def load(self, name: str) -> str:
        file = PROMPT_DIR / f"{name}.md"

        if not file.exists():
            raise ValueError(f"Prompt {name} not found")

        modified = file.stat().st_mtime

        # reload automático se mudou
        if name not in self.cache or self.timestamps.get(name) != modified:
            self.cache[name] = file.read_text()
            self.timestamps[name] = modified

        return self.cache[name]


prompt_loader = PromptLoader()
