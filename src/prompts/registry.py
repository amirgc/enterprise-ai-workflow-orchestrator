from pathlib import Path


TEMPLATES_DIR = Path(__file__).parent / "templates"


class PromptRegistry:
    """Loads prompt templates from disk and fills in placeholders.

    Why a registry instead of hardcoded strings?
    1. Templates are version-tracked files — you can diff changes in git
    2. Non-engineers (product, legal) can review/edit prompts without touching code
    3. You can A/B test prompt versions (classify_v1 vs classify_v2)

    """

    def __init__(self):
        """Load all .txt templates from the templates directory into memory.

        Creates a dict like: {"classify_v1": "Classify the following...", ...}
        The key is the filename without .txt extension.
        """
        self.templates: dict[str, str] = {}

        for template_file in TEMPLATES_DIR.glob("*.txt"):
            name = template_file.stem  # "classify_v1.txt" -> "classify_v1"
            self.templates[name] = template_file.read_text(encoding="utf-8")

    def get(self, name: str, **kwargs) -> str:
        """Get a prompt template and fill in placeholders.

        Args:
            name: Template name without extension (e.g., "classify_v1")
            **kwargs: Values to fill in. e.g., request_text="Onboard ABC..."

        Returns:
            The completed prompt string with placeholders replaced.

        Example:
            registry.get("classify_v1", request_text="Onboard ABC Supplies")
            # Returns the template with {request_text} replaced
        """
        if name not in self.templates:
            available = ", ".join(sorted(self.templates.keys()))
            raise ValueError(f"Unknown template '{name}'. Available: {available}")

        return self.templates[name].format(**kwargs)

    def list_templates(self) -> list[str]:
        """Return names of all loaded templates."""
        return sorted(self.templates.keys())
