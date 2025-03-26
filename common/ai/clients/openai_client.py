from openai import AsyncOpenAI

class AsyncOpenAIClient:
    def __init__(self):
        self.client=AsyncOpenAI()

    async def create_completion(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        tools: list = None,
        tool_choice: str = "auto"
    ):
        """
        Create a chat completion using the asynchronous OpenAI API.

        Args:
            model (str): The model ID to use.
            messages (list): A list of message dicts in the OpenAI chat format.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum tokens in the completion.
            top_p (float): Nucleus sampling parameter.
            frequency_penalty (float): Frequency penalty.
            presence_penalty (float): Presence penalty.
            tools (list, optional): List of tool definitions (if using OpenAI functions).
            tool_choice (str): How to choose the tool call (default "auto").

        Returns:
            The response from the OpenAI API.
        """
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            tools=tools,
            tool_choice=tool_choice
        )
        return response