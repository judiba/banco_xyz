class FakeLLM:
    async def stream(self, system_prompt, user_input):
        text = f"{system_prompt}\n{user_input}"

        for word in text.split():
            yield word + " "
