from typing import Any, Callable


class ToolRegistry:
    """Registry of tools the LLM can call.

    'Tool use' (aka 'function calling') lets the LLM invoke your backend code.
    Instead of just generating text, the LLM can say:
    "I need to call create_vendor with these arguments."

    This registry:
    1. Stores tool definitions (name, description, parameters)
    2. Maps tool names to actual Python functions
    3. Executes tools when the LLM requests them

    In C# terms: think of it like a controller registry where each tool
    is an endpoint the LLM can call.
    """

    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}
        self._handlers: dict[str, Callable] = {}

    def register(self, name: str, description: str, parameters: dict, handler: Callable):
        """Register a tool that the LLM can call.

        Args:
            name: Tool name the LLM will reference (e.g., "create_vendor")
            description: What the tool does — the LLM reads this to decide when to use it
            parameters: JSON Schema describing the expected arguments
            handler: The actual Python function to run when the LLM calls this tool
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "input_schema": parameters,
        }
        self._handlers[name] = handler

    def get_tool_definitions(self) -> list[dict]:
        """Return tool definitions in the format the Anthropic API expects.

        This list gets passed to the API so the LLM knows what tools are available.
        """
        return list(self._tools.values())

    def execute(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name with the given arguments.

        Called when the LLM decides to use a tool — we look up the matching
        Python function and call it.
        """
        if name not in self._handlers:
            available = ", ".join(sorted(self._handlers.keys()))
            raise ValueError(f"Unknown tool '{name}'. Available: {available}")

        return self._handlers[name](**arguments)

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""
        return sorted(self._tools.keys())
