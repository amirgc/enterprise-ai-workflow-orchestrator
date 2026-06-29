import time
from dataclasses import dataclass, field
from datetime import datetime, timezone


# Cost per million tokens (approximate, varies by model)
COST_PER_MILLION = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


@dataclass
class LLMCallMetrics:
    """Metrics for a single LLM API call."""
    step: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost_usd: float
    timestamp: str


@dataclass
class PipelineMetrics:
    """Aggregated metrics across all LLM calls in a pipeline run.

    Collects per-call metrics and provides summary stats.
    In production, you'd send these to Datadog, Grafana, etc.
    """
    calls: list[LLMCallMetrics] = field(default_factory=list)

    def record_call(self, step: str, model: str, input_tokens: int,
                    output_tokens: int, latency_ms: float):
        """Record metrics for one LLM call.

        Args:
            step: Pipeline step name (e.g., "classify", "extract")
            model: Model used (e.g., "claude-sonnet-4-20250514")
            input_tokens: Tokens sent to the LLM
            output_tokens: Tokens received from the LLM
            latency_ms: How long the call took in milliseconds
        """
        cost = self._calculate_cost(model, input_tokens, output_tokens)

        metric = LLMCallMetrics(
            step=step,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 2),
            cost_usd=round(cost, 6),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self.calls.append(metric)

    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate USD cost based on token counts and model pricing.

        If the model isn't in our pricing table, returns 0.
        """
        pricing = COST_PER_MILLION.get(model)
        if not pricing:
            return 0.0

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def summary(self) -> dict:
        """Return a summary of all calls in this pipeline run."""
        if not self.calls:
            return {"total_calls": 0}

        return {
            "total_calls": len(self.calls),
            "total_input_tokens": sum(c.input_tokens for c in self.calls),
            "total_output_tokens": sum(c.output_tokens for c in self.calls),
            "total_cost_usd": round(sum(c.cost_usd for c in self.calls), 6),
            "total_latency_ms": round(sum(c.latency_ms for c in self.calls), 2),
            "avg_latency_ms": round(
                sum(c.latency_ms for c in self.calls) / len(self.calls), 2
            ),
            "steps": [c.step for c in self.calls],
        }

    def print_report(self):
        """Print a human-readable report to the terminal."""
        s = self.summary()
        if s["total_calls"] == 0:
            print("No LLM calls recorded.")
            return

        print("\n" + "=" * 50)
        print("  PIPELINE METRICS")
        print("=" * 50)
        print(f"  Total calls:     {s['total_calls']}")
        print(f"  Input tokens:    {s['total_input_tokens']:,}")
        print(f"  Output tokens:   {s['total_output_tokens']:,}")
        print(f"  Total cost:      ${s['total_cost_usd']:.4f}")
        print(f"  Total latency:   {s['total_latency_ms']:.0f}ms")
        print(f"  Avg latency:     {s['avg_latency_ms']:.0f}ms")
        print("-" * 50)

        for call in self.calls:
            print(f"  [{call.step}] {call.model} — "
                  f"{call.input_tokens}+{call.output_tokens} tokens, "
                  f"{call.latency_ms:.0f}ms, ${call.cost_usd:.4f}")

        print("=" * 50)


class Timer:
    """Context manager to measure elapsed time in milliseconds.

    Usage:
        with Timer() as t:
            # do something slow
        print(t.elapsed_ms)  # e.g., 342.5

    In C# terms: like a Stopwatch wrapped in a using block.
    """

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed_ms = (time.perf_counter() - self.start) * 1000
