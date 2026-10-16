from app.tools.master_registry import master_tool_router
import json
import torch

from app.agent.tools import create_tool_registry
from app.memory.memory import Memory
from app.security.permissions import (
    PermissionManager,
    PermissionStatus,
)


class Agent:

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer
        self.registry = create_tool_registry()
        self.memory = Memory()
        self.permissions = PermissionManager()

        memories = self.memory.get_all()

        if memories:
            memory_text = "\n".join(
                f"- {memory}"
                for memory in memories
            )
        else:
            memory_text = "(No stored memories.)"

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are SweetyAI, an expert local AI agent and legal tech assistant.\n"
                    "You have access to tools including file operations, project search, legal database lookups, and memory management.\n"
                    "Use a tool when it is necessary to complete the user's request.\n"
                    "When reviewing code or answering legal/study questions, provide precise, verified, and well-formatted responses.\n"
                    "IMPORTANT: Tool execution is controlled by the runtime permission manager. "
                    "Never claim a tool action succeeded unless a tool result confirms it.\n\n"
                    "IMPORTANT MEMORY:\n"
                    "The following information is stored in your persistent "
                    "memory database and is available to you.\n"
                    "When the user asks what you remember, answer using "
                    "these stored memories.\n\n"
                    "STORED MEMORIES:\n"
                    + memory_text
                ),
            }
        ]

    def generate(self):
        text = self.tokenizer.apply_chat_template(
            self.messages,
            tools=self.registry.get_schemas(),
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            [text],
            return_tensors="pt",
        ).to("cuda")

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1536,
                do_sample=False,
            )

        generated = outputs[0][
            inputs.input_ids.shape[1]:
        ]

        return self.tokenizer.decode(
            generated,
            skip_special_tokens=False,
        ).strip()

    def clean_response(self, response):
        if "</think>" in response:
            response = response.split(
                "</think>",
                1
            )[1]

        response = response.replace(
            "<|im_end|>",
            ""
        )
        response = response.replace(
            "<|im_start|>",
            ""
        )
        response = response.replace(
            "<|assistant|>",
            ""
        )

        return response.strip()

    def parse_tool_calls(self, response):
        calls = []

        if "<tool_call>" not in response:
            return calls

        parts = response.split(
            "<tool_call>"
        )[1:]

        for part in parts:
            if "</tool_call>" in part:
                part = part.split(
                    "</tool_call>",
                    1
                )[0]

            part = part.strip()

            try:
                call = json.loads(part)
                if "name" in call:
                    calls.append(call)
            except json.JSONDecodeError as error:
                print(
                    "[Agent] Could not parse tool call:",
                    error
                )

        return calls

    def execute_tool(self, tool_call):
        tool_name = tool_call.get("name", "")
        arguments = tool_call.get("arguments", {})

        print(f"\n[Agent] Requested tool: {tool_name}")
        print(f"[Agent] Arguments: {arguments}")

        decision = self.permissions.check(tool_name, arguments)

        print(
            f"[Permission] {decision.status.value} "
            f"({decision.level.value})"
        )

        if decision.status == PermissionStatus.DENIED:
            message = self.permissions.format_denied(decision)
            print(f"[Permission] BLOCKED: {message}\n")
            return message, False

        if decision.status == PermissionStatus.ASK:
            message = self.permissions.format_request(
                decision,
                arguments,
            )
            print(f"[Permission] APPROVAL REQUIRED:\n{message}\n")
            return message, False

        result = self.registry.execute(tool_name, arguments)

        print(f"[Tool result] {result}\n")
        return result, True

    def chat(self, user_message):
        self.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        max_steps = 8

        for step in range(max_steps):
            if len(self.messages) > 8:
                self.messages = [
                    self.messages[0]
                ] + self.messages[-7:]

            response = self.generate()
            tool_calls = self.parse_tool_calls(response)

            if not tool_calls:
                final_answer = self.clean_response(response)

                self.messages.append(
                    {
                        "role": "assistant",
                        "content": final_answer
                    }
                )

                return final_answer

            self.messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            for tool_call in tool_calls:
                result, executed = self.execute_tool(tool_call)

                if not executed:
                    self.messages.append(
                        {
                            "role": "assistant",
                            "content": result
                        }
                    )
                    return result

                tool_context = result
                max_tool_context_chars = 5000

                if len(tool_context) > max_tool_context_chars:
                    tool_context = (
                        tool_context[:max_tool_context_chars]
                        + "\n\n[Tool output truncated in model context.]"
                    )

                self.messages.append(
                    {
                        "role": "tool",
                        "content": tool_context
                    }
                )

        return (
            "I reached the maximum number of "
            "tool steps for this request."
        )
