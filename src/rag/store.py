from dataclasses import dataclass
from pathlib import Path


POLICIES_DIR = Path(__file__).parent / "policies"


@dataclass
class PolicyMatch:
    """A policy document that matched a search query."""
    title: str
    content: str
    relevance_score: float


class PolicyStore:
    """Loads policy documents and retrieves relevant ones by keyword search.

    RAG = Retrieval-Augmented Generation. Instead of hoping the LLM "knows"
    your company policies, you RETRIEVE the relevant docs and inject them
    into the prompt as context. The LLM then GENERATES a response grounded
    in your actual policies.

    This uses simple keyword matching. In production, you'd use embeddings
    and a vector database (like Pinecone or ChromaDB) for semantic search.
    """

    def __init__(self):
        """Load all .md policy files from the policies directory."""
        self.policies: dict[str, str] = {}

        for policy_file in POLICIES_DIR.glob("*.md"):
            title = policy_file.stem.replace("_", " ").title()
            self.policies[title] = policy_file.read_text(encoding="utf-8")

    def search(self, query: str, top_k: int = 2) -> list[PolicyMatch]:
        """Find policies relevant to the query using keyword matching.

        Scores each policy by how many query words appear in it.
        Returns the top_k highest-scoring policies.

        Args:
            query: Search text (e.g., "Net 90 payment international vendor")
            top_k: Maximum number of results to return.
        """
        query_words = query.lower().split()
        scored: list[PolicyMatch] = []

        for title, content in self.policies.items():
            content_lower = content.lower()
            hits = sum(1 for word in query_words if word in content_lower)
            if hits > 0:
                score = hits / len(query_words)
                scored.append(PolicyMatch(title=title, content=content, relevance_score=score))

        scored.sort(key=lambda m: m.relevance_score, reverse=True)
        return scored[:top_k]

    def format_context(self, matches: list[PolicyMatch]) -> str:
        """Format matched policies into a string to inject into an LLM prompt.

        This is the 'augmentation' part of RAG — we add retrieved documents
        to the prompt so the LLM can reference them.
        """
        if not matches:
            return "No relevant policies found."

        sections = []
        for match in matches:
            sections.append(f"--- {match.title} (relevance: {match.relevance_score:.0%}) ---\n{match.content}")

        return "\n\n".join(sections)
