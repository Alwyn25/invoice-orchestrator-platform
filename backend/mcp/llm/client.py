class LLMClient:
    """A fake LLM client that returns a deterministic dummy response."""

    def query(self, prompt: str, model: str = "fake-model", options: dict | None = None) -> dict:
        """
        Simulates querying an LLM.

        Args:
            prompt: The input prompt for the LLM.
            model: The model to use (ignored in this fake client).
            options: Additional options for the LLM call (ignored).

        Returns:
            A dictionary containing a fake LLM response.
        """
        return {
            "text": f"FAKE_LLM_RESPONSE for: {prompt[:50]}",
            "confidence": 0.99,
            "raw_response": "{}",
        }
