from dataclasses import dataclass
from enum import Enum
from typing import Any


class PermissionLevel(str, Enum):
    SAFE = "safe"
    APPROVAL = "approval"
    DANGEROUS = "dangerous"


class PermissionStatus(str, Enum):
    ALLOWED = "allowed"
    ASK = "ask"
    DENIED = "denied"


@dataclass(frozen=True)
class PermissionDecision:
    status: PermissionStatus
    level: PermissionLevel
    tool: str
    reason: str


class PermissionManager:
    SAFE_TOOLS = {
        "calculator",
        "list_files",
        "read_file",
        "web_search",
        "search_searxng",
        "read_webpage",
        "save_memory",
        "search_project",
        "search_legal_database",
        "get_current_time",
        "list_knowledge_documents",
        "search_local_files",
        "read_clipboard_text",
        "get_system_info",
        "open_workspace_folder",
    }

    APPROVAL_TOOLS = {
        "write_file",
        "append_file",
        "delete_memory",
        "create_file",
        "rename_file",
        "move_file",
        "send_email",
        "install_package",
        "modify_config",
        "write_clipboard_text",
        "open_application",
        "generate_legal_document",
    }

    DANGEROUS_TOOLS = {
        "delete_file",
        "run_command",
        "format_drive",
        "change_system_settings",
        "modify_security_settings",
        "financial_transaction",
    }

    def check(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> PermissionDecision:
        if tool_name in self.SAFE_TOOLS:
            return PermissionDecision(
                PermissionStatus.ALLOWED,
                PermissionLevel.SAFE,
                tool_name,
                "Tool is classified as safe.",
            )

        if tool_name in self.APPROVAL_TOOLS:
            return PermissionDecision(
                PermissionStatus.ASK,
                PermissionLevel.APPROVAL,
                tool_name,
                "This action changes data or performs an external side effect.",
            )

        if tool_name in self.DANGEROUS_TOOLS:
            return PermissionDecision(
                PermissionStatus.ASK,
                PermissionLevel.DANGEROUS,
                tool_name,
                "This action can cause destructive or high-impact changes.",
            )

        return PermissionDecision(
            PermissionStatus.DENIED,
            PermissionLevel.DANGEROUS,
            tool_name,
            "Tool is not classified by the permission policy.",
        )

    def format_request(
        self,
        decision: PermissionDecision,
        arguments: dict[str, Any] | None = None,
    ) -> str:
        return (
            "Permission required before I can continue.\n\n"
            f"Tool: {decision.tool}\n"
            f"Risk level: {decision.level.value}\n"
            f"Reason: {decision.reason}\n"
            f"Arguments: {arguments or {}}\n\n"
            "No action has been executed."
        )

    def format_denied(self, decision: PermissionDecision) -> str:
        return (
            f"I blocked the tool '{decision.tool}' because it is not approved "
            "by the current permission policy. No action was executed."
        )
