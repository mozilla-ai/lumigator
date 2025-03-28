import copy

from pydantic import BaseModel


class PromptFormat(BaseModel):
    system: str
    assistant: str
    trailing_assistant: str
    user: str

    system_in_user: bool = False
    is_generation: bool = False

    # @field_validator("system")
    # def check_system(cls, value):
    #     assert value and ("{instruction}" in value), "system must be a string containing '{instruction}'"
    #     return value
    #
    # @field_validator("assistant")
    # def check_assistant(cls, value):
    #     assert value and "{instruction}" in value, "assistant must be a string containing '{instruction}'"
    #     return value
    #
    # @field_validator("user")
    # def check_user(cls, value):
    #     assert value and ("{instruction}" in value), "user must be a string containing '{instruction}'"
    #     return value
    #
    # @field_validator("system_in_user")
    # def check_system_in_user(cls, value):
    #     # `system_in_user` is restricted to be True.
    #     # Re-evaluate the code and add unit tests when relaxing this.
    #     # assert value
    #     return value
    #
    # @field_validator("default_system_message")
    # def check_default_system_message(cls, value):
    #     # User should explicitly give a system message if so preferred.
    #     # assert value == ""
    #     return value
    #
    # @field_validator("trailing_assistant")
    # def check_trailing_assistant(cls, value):
    #     # `trailing_assistant` is restricted to be "".
    #     # Re-evaluate the code and add unit tests when relaxing this.
    #     assert value == ""
    #     return value

    def generate_prompt_turns(self, messages: list[dict]) -> list[dict]:
        """Return formatted system/user/assistant messages."""
        messages = copy.deepcopy(messages)

        system_message = None
        if messages[0]["role"] == "system":
            system_message = messages.pop(0)
            if system_message["content"] is None:
                system_message["content"] = ""

        if not all([msg["role"] == "user" for msg in messages[::2]]) and all(
            [msg["role"] == "assistant" for msg in messages[1::2]]
        ):
            raise ValueError(
                "Only supports 'system', 'user' and 'assistant' roles, "
                "starting with 'system', then 'user' and alternating between 'user' and 'assistant'."
            )

        if any([msg["content"] is None for msg in messages]):
            raise ValueError("Both user and assistant messages cannot be None.")

        # only applies at train/eval but not in generation
        if not self.is_generation and not messages[-1]["role"] == "assistant":
            raise ValueError(f"Last message must be from assistant, got {messages[-1]['role']}")

        if system_message is not None and system_message["content"] and not self.system_in_user:
            messages.insert(0, system_message)

        prompt = []
        for message in messages:
            message_content = message["content"]
            message_content = message_content.strip()
            if message["role"] == "system":
                prompt.append(
                    {
                        "role": "system",
                        "content": self.system.format(instruction=message_content),
                    }
                )
            elif message["role"] == "user":
                if self.system_in_user:
                    prompt.append(
                        {
                            "role": "user",
                            "content": self.user.format(
                                instruction=message_content,
                                system=(
                                    self.system.format(instruction=system_message["content"]) if system_message else ""
                                ),
                            ),
                        }
                    )
                    system_message = None
                else:
                    prompt.append(
                        {
                            "role": "user",
                            "content": self.user.format(instruction=message_content),
                        }
                    )
            elif message["role"] == "assistant":
                prompt.append(
                    {
                        "role": "assistant",
                        "content": self.assistant.format(instruction=message_content),
                    }
                )

        if self.trailing_assistant:
            prompt.append({"role": "assistant", "content": self.trailing_assistant})
        return prompt

    def generate_prompt(self, messages: list[dict]) -> str:
        """Concatenate the 'content' of all formatted prompts."""
        prompt = self.generate_prompt_turns(messages)
        return "".join(turn["content"] for turn in prompt)
