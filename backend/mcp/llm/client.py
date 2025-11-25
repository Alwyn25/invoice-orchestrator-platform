import logging

class LLMClient:
    """A stub for the LLM client."""

    def query(self, prompt: str, context: dict) -> dict:
        """
        Queries the LLM with a prompt and context.
        This is a stub and returns a dummy response.
        """
        logging.info(f"Querying LLM with prompt: {prompt}")
        return {
            "response_text": f"This is a dummy response to the prompt: '{prompt}'",
            "metadata": {
                "model_name": "stub-model-v1",
                "prompt_tokens": len(prompt.split()),
                "response_tokens": 10,
            },
        }

llm_client = LLMClient()
