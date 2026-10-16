"""
SweetyAI - Security & HITL Approval System
RBAC, encryption, audit trails, human-in-the-loop approvals, sandboxed execution
"""

import os
import json
import time
import hashlib
import hmac
import uuid
import threading
from typing import Dict, Any, Optional, List, Callable, Set
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from functools import wraps

# Encryption
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    import base64
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("[Security] cryptography not available. Run: pip install cryptography")

# JWT
try:
    import jwt as pyjwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("[Security] PyJWT not available. Run: pip install pyjwt")


# =============================================================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# =============================================================================

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    ADMIN = "admin"
    APPROVE = "approve"
    SEND_EMAIL = "send_email"
    FILE_DELETE = "file_delete"
    CODE_EXECUTE = "code_execute"
    SYSTEM_CONFIG = "system_config"


@dataclass
class Role:
    name: str
    permissions: Set[Permission]
    description: str = ""

    def has_permission(self, perm: Permission) -> bool:
        return perm in self.permissions or Permission.ADMIN in self.permissions


@dataclass
class User:
    user_id: str
    username: str
    roles: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    is_active: bool = True


class RBACManager:
    """Role-Based Access Control manager."""

    # Built-in roles
    BUILT_IN_ROLES = {
        "admin": Role("admin", {Permission.ADMIN}, "Full system access"),
        "user": Role("user", {Permission.READ, Permission.WRITE, Permission.EXECUTE}, "Standard user"),
        "viewer": Role("viewer", {Permission.READ}, "Read-only access"),
        "operator": Role(
            "operator",
            {Permission.READ, Permission.WRITE, Permission.EXECUTE, Permission.APPROVE, Permission.SEND_EMAIL},
            "Can approve and send emails",
        ),
    }

    def __init__(self, config_path: str = "config/rbac.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.roles: Dict[str, Role] = dict(self.BUILT_IN_ROLES)
        self.users: Dict[str, User] = {}
        self._load_config()

    def add_role(self, name: str, permissions: Set[Permission], description: str = ""):
        self.roles[name] = Role(name, permissions, description)
        self._save_config()

    def add_user(self, username: str, roles: List[str]) -> User:
        user = User(user_id=uuid.uuid4().hex[:12], username=username, roles=roles)
        self.users[user.user_id] = user
        self._save_config()
        return user

    def check_permission(self, user_id: str, permission: Permission) -> bool:
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role and role.has_permission(permission):
                return True
        return False

    def get_user_permissions(self, user_id: str) -> Set[Permission]:
        user = self.users.get(user_id)
        if not user:
            return set()
        perms = set()
        for role_name in user.roles:
            role = self.roles.get(role_name)
            if role:
                perms |= role.permissions
        return perms

    def _save_config(self):
        data = {
            "roles": {
                n: {"permissions": [p.value for p in r.permissions], "description": r.description}
                for n, r in self.roles.items()
            },
            "users": {
                uid: {"username": u.username, "roles": u.roles, "is_active": u.is_active}
                for uid, u in self.users.items()
            },
        }
        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_config(self):
        if not self.config_path.exists():
            return
        try:
            with open(self.config_path) as f:
                data = json.load(f)
            for name, rdata in data.get("roles", {}).items():
                self.roles[name] = Role(name, {Permission(p) for p in rdata["permissions"]}, rdata.get("description", ""))
            for uid, udata in data.get("users", {}).items():
                self.users[uid] = User(uid, udata["username"], udata["roles"], is_active=udata.get("is_active", True))
        except Exception:
            pass


def require_permission(permission: Permission):
    """Decorator that enforces RBAC permission checks."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, user_id: str = None, **kwargs):
            if user_id and not rbac_manager.check_permission(user_id, permission):
                raise PermissionError(f"User {user_id} lacks permission: {permission.value}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# ENCRYPTION
# =============================================================================

class EncryptionManager:
    """Encrypt/decrypt sensitive data using Fernet symmetric encryption."""

    def __init__(self, key: Optional[str] = None, key_file: str = "config/.encryption_key"):
        if not CRYPTO_AVAILABLE:
            raise ImportError("cryptography not installed")

        self.key_file = Path(key_file)
        self.key_file.parent.mkdir(parents=True, exist_ok=True)

        if key:
            self.key = key.encode() if isinstance(key, str) else key
        else:
            self.key = self._load_or_generate_key()

        self.fernet = Fernet(self.key)

    def _load_or_generate_key(self) -> bytes:
        if self.key_file.exists():
            return self.key_file.read_bytes()
        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        return key

    def encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()

    def decrypt(self, encrypted_data: str) -> str:
        return self.fernet.decrypt(encrypted_data.encode()).decode()

    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        return self.encrypt(json.dumps(data))

    def decrypt_dict(self, encrypted: str) -> Dict[str, Any]:
        return json.loads(self.decrypt(encrypted))

    @staticmethod
    def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
        salt = salt or os.urandom(16)
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=480_000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt

    def hash_password(self, password: str) -> str:
        salt = os.urandom(16)
        key, _ = self.derive_key_from_password(password, salt)
        return f"{salt.hex()}:{key.decode()}"

    def verify_password(self, password: str, stored_hash: str) -> bool:
        salt_hex, expected = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        key, _ = self.derive_key_from_password(password, salt)
        return hmac.compare_digest(key.decode(), expected)


# =============================================================================
# AUDIT TRAIL
# =============================================================================

@dataclass
class AuditEntry:
    event_id: str
    timestamp: str
    user_id: str
    action: str
    resource: str
    details: Dict[str, Any]
    outcome: str  # "success" | "denied" | "error"


class AuditTrail:
    """Immutable audit log for compliance and forensics."""

    def __init__(self, log_dir: str = "logs/audit"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.Lock()

    def log(self, user_id: str, action: str, resource: str, details: Dict[str, Any] = None, outcome: str = "success"):
        entry = AuditEntry(
            event_id=uuid.uuid4().hex[:16],
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {},
            outcome=outcome,
        )
        self._write(entry)

    def query(self, user_id: str = None, action: str = None, since: datetime = None, limit: int = 100) -> List[Dict]:
        entries = self._read_all()
        if user_id:
            entries = [e for e in entries if e["user_id"] == user_id]
        if action:
            entries = [e for e in entries if e["action"] == action]
        if since:
            entries = [e for e in entries if e["timestamp"] >= since.isoformat()]
        return entries[-limit:]

    def _write(self, entry: AuditEntry):
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = self.log_dir / f"audit_{date_str}.jsonl"
        with self.lock:
            with open(log_file, "a") as f:
                f.write(json.dumps(asdict(entry)) + "\n")

    def _read_all(self) -> List[Dict]:
        entries = []
        for log_file in sorted(self.log_dir.glob("audit_*.jsonl")):
            with open(log_file) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        return entries


# =============================================================================
# HUMAN-IN-THE-LOOP (HITL) APPROVAL
# =============================================================================

class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    request_id: str
    action: str
    description: str
    details: Dict[str, Any]
    requester: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None
    ttl_seconds: int = 300


class HITLApprovalManager:
    """Human-in-the-loop approval gate for high-risk actions."""

    # Actions that always require approval
    HIGH_RISK_ACTIONS = {
        "send_email", "delete_file", "execute_code", "system_command",
        "database_write", "api_key_change", "deploy", "payment",
    }

    def __init__(self, audit_trail: AuditTrail):
        self.pending: Dict[str, ApprovalRequest] = {}
        self.history: List[ApprovalRequest] = []
        self.audit = audit_trail
        self.callbacks: Dict[str, Callable] = {}
        self.lock = threading.Lock()

    def request_approval(
        self,
        action: str,
        description: str,
        details: Dict[str, Any],
        requester: str = "system",
        ttl_seconds: int = 300,
        on_approved: Callable = None,
        on_rejected: Callable = None,
    ) -> str:
        req = ApprovalRequest(
            request_id=uuid.uuid4().hex[:12],
            action=action,
            description=description,
            details=details,
            requester=requester,
            ttl_seconds=ttl_seconds,
        )
        with self.lock:
            self.pending[req.request_id] = req
        if on_approved:
            self.callbacks[f"{req.request_id}_approved"] = on_approved
        if on_rejected:
            self.callbacks[f"{req.request_id}_rejected"] = on_rejected

        self.audit.log(requester, "approval_requested", action, details)
        return req.request_id

    def approve(self, request_id: str, approver: str = "user") -> str:
        with self.lock:
            req = self.pending.pop(request_id, None)
        if not req:
            return "Request not found or expired"

        req.status = ApprovalStatus.APPROVED
        req.resolved_at = datetime.now().isoformat()
        req.resolved_by = approver
        self.history.append(req)

        self.audit.log(approver, "approval_granted", req.action, req.details)

        cb = self.callbacks.pop(f"{request_id}_approved", None)
        if cb:
            cb(req.details)

        return f"Approved: {req.action}"

    def reject(self, request_id: str, approver: str = "user", reason: str = "") -> str:
        with self.lock:
            req = self.pending.pop(request_id, None)
        if not req:
            return "Request not found or expired"

        req.status = ApprovalStatus.REJECTED
        req.resolved_at = datetime.now().isoformat()
        req.resolved_by = approver
        self.history.append(req)

        self.audit.log(approver, "approval_rejected", req.action, {"reason": reason})

        cb = self.callbacks.pop(f"{request_id}_rejected", None)
        if cb:
            cb(req.details)

        return f"Rejected: {req.action}"

    def expire_stale(self):
        now = datetime.now()
        with self.lock:
            expired_ids = []
            for rid, req in self.pending.items():
                created = datetime.fromisoformat(req.created_at)
                if (now - created).total_seconds() > req.ttl_seconds:
                    req.status = ApprovalStatus.EXPIRED
                    expired_ids.append(rid)
                    self.history.append(req)
            for rid in expired_ids:
                del self.pending[rid]

    def get_pending(self) -> List[Dict[str, Any]]:
        self.expire_stale()
        return [asdict(r) for r in self.pending.values()]

    def is_high_risk(self, action: str) -> bool:
        return action in self.HIGH_RISK_ACTIONS


def require_approval(action: str, description: str = ""):
    """Decorator that gates a function behind HITL approval."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hitl_manager.is_high_risk(action):
                details = {"function": func.__name__, "args": str(args)[:200], "kwargs": str(kwargs)[:200]}
                request_id = hitl_manager.request_approval(
                    action=action,
                    description=description or f"Approve {func.__name__}?",
                    details=details,
                )
                raise PendingApprovalError(request_id, action)
            return func(*args, **kwargs)
        return wrapper
    return decorator


class PendingApprovalError(Exception):
    """Raised when an action needs human approval before proceeding."""
    def __init__(self, request_id: str, action: str):
        self.request_id = request_id
        self.action = action
        super().__init__(f"Action '{action}' requires approval (request_id={request_id})")


# =============================================================================
# SANDBOXED EXECUTION
# =============================================================================

class SandboxExecutor:
    """Execute untrusted code in a restricted environment."""

    BLOCKED_BUILTINS = {"exec", "eval", "__import__", "compile", "open", "exit", "quit"}
    BLOCKED_MODULES = {"os", "sys", "subprocess", "shutil", "socket", "ctypes"}

    def __init__(self, timeout: int = 10, max_memory_mb: int = 256):
        self.timeout = timeout
        self.max_memory_mb = max_memory_mb

    def execute(self, code: str, allowed_globals: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run code in a restricted namespace."""
        # Validate code
        violations = self._check_violations(code)
        if violations:
            return {"error": f"Blocked: {', '.join(violations)}", "output": None}

        safe_globals = {"__builtins__": self._safe_builtins()}
        if allowed_globals:
            safe_globals.update(allowed_globals)

        local_ns: Dict[str, Any] = {}
        result = {"output": None, "error": None, "variables": {}}

        def _run():
            try:
                compiled = compile(code, "<sandbox>", "exec")
                exec(compiled, safe_globals, local_ns)  # noqa: S102  — intentionally sandboxed
                result["variables"] = {k: v for k, v in local_ns.items() if not k.startswith("_")}
                result["output"] = local_ns.get("result", local_ns.get("output"))
            except Exception as e:
                result["error"] = f"{type(e).__name__}: {e}"

        thread = threading.Thread(target=_run)
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            result["error"] = f"Execution timed out after {self.timeout}s"

        return result

    def _check_violations(self, code: str) -> List[str]:
        violations = []
        for mod in self.BLOCKED_MODULES:
            if f"import {mod}" in code or f"from {mod}" in code:
                violations.append(f"blocked module: {mod}")
        for builtin in self.BLOCKED_BUILTINS:
            if f"{builtin}(" in code:
                violations.append(f"blocked builtin: {builtin}")
        return violations

    def _safe_builtins(self) -> Dict[str, Any]:
        import builtins
        safe = {}
        allowed = {
            "abs", "all", "any", "bool", "chr", "dict", "enumerate", "filter",
            "float", "frozenset", "hasattr", "hash", "int", "isinstance",
            "issubclass", "iter", "len", "list", "map", "max", "min", "next",
            "ord", "pow", "print", "range", "repr", "reversed", "round",
            "set", "slice", "sorted", "str", "sum", "tuple", "type", "zip",
        }
        for name in allowed:
            if hasattr(builtins, name):
                safe[name] = getattr(builtins, name)
        return safe


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

rbac_manager = RBACManager()
audit_trail = AuditTrail()
hitl_manager = HITLApprovalManager(audit_trail)
sandbox = SandboxExecutor()

# Set up encryption only when the library is available
encryption_manager: Optional[EncryptionManager] = None
if CRYPTO_AVAILABLE:
    try:
        encryption_manager = EncryptionManager()
    except Exception:
        pass


__all__ = [
    "Permission",
    "Role",
    "User",
    "RBACManager",
    "EncryptionManager",
    "AuditTrail",
    "AuditEntry",
    "HITLApprovalManager",
    "ApprovalRequest",
    "ApprovalStatus",
    "PendingApprovalError",
    "SandboxExecutor",
    "require_permission",
    "require_approval",
    "rbac_manager",
    "audit_trail",
    "hitl_manager",
    "encryption_manager",
    "sandbox",
]
