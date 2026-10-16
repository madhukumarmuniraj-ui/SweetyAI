"""
SweetyAI - Error Recovery & Checkpoint System
Automatic checkpoint/restore, retry logic, state preservation, rollback capabilities
"""

import os
import json
import pickle
import hashlib
import time
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from functools import wraps


# =============================================================================
# CHECKPOINT SYSTEM
# =============================================================================

class CheckpointStatus(Enum):
    """Checkpoint status states."""
    CREATED = "created"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Checkpoint:
    """Represents a task checkpoint."""
    checkpoint_id: str
    task_id: str
    task_name: str
    state: Dict[str, Any]
    status: CheckpointStatus
    timestamp: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Checkpoint':
        """Create from dictionary."""
        data['status'] = CheckpointStatus(data['status'])
        return cls(**data)


class CheckpointManager:
    """Manage task checkpoints for recovery."""

    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        self.checkpoints: Dict[str, Checkpoint] = {}
        self.lock = threading.Lock()

        # Load existing checkpoints
        self._load_checkpoints()

    def _generate_checkpoint_id(self, task_id: str) -> str:
        """Generate unique checkpoint ID."""
        timestamp = datetime.now().isoformat()
        hash_input = f"{task_id}_{timestamp}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]

    def create_checkpoint(
        self,
        task_id: str,
        task_name: str,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a checkpoint for a task.

        Args:
            task_id: Unique task identifier
            task_name: Human-readable task name
            state: Current task state to save
            metadata: Additional metadata

        Returns:
            Checkpoint ID
        """
        checkpoint_id = self._generate_checkpoint_id(task_id)

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            task_id=task_id,
            task_name=task_name,
            state=state,
            status=CheckpointStatus.CREATED,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )

        with self.lock:
            self.checkpoints[checkpoint_id] = checkpoint
            self._save_checkpoint(checkpoint)

        return checkpoint_id

    def update_checkpoint(
        self,
        checkpoint_id: str,
        state: Optional[Dict[str, Any]] = None,
        status: Optional[CheckpointStatus] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update an existing checkpoint."""
        with self.lock:
            if checkpoint_id not in self.checkpoints:
                return False

            checkpoint = self.checkpoints[checkpoint_id]

            if state is not None:
                checkpoint.state.update(state)

            if status is not None:
                checkpoint.status = status

            if metadata is not None:
                checkpoint.metadata.update(metadata)

            checkpoint.timestamp = datetime.now().isoformat()
            self._save_checkpoint(checkpoint)

        return True

    def get_checkpoint(self, checkpoint_id: str) -> Optional[Checkpoint]:
        """Retrieve a checkpoint."""
        with self.lock:
            return self.checkpoints.get(checkpoint_id)

    def get_task_checkpoints(self, task_id: str) -> List[Checkpoint]:
        """Get all checkpoints for a task."""
        with self.lock:
            return [
                cp for cp in self.checkpoints.values()
                if cp.task_id == task_id
            ]

    def get_latest_checkpoint(self, task_id: str) -> Optional[Checkpoint]:
        """Get the most recent checkpoint for a task."""
        checkpoints = self.get_task_checkpoints(task_id)
        if not checkpoints:
            return None

        return max(checkpoints, key=lambda cp: cp.timestamp)

    def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint."""
        with self.lock:
            if checkpoint_id not in self.checkpoints:
                return False

            checkpoint = self.checkpoints.pop(checkpoint_id)
            checkpoint_file = self.checkpoint_dir / f"{checkpoint_id}.json"

            if checkpoint_file.exists():
                checkpoint_file.unlink()

        return True

    def cleanup_old_checkpoints(self, days: int = 7):
        """Delete checkpoints older than specified days."""
        cutoff_date = datetime.now() - timedelta(days=days)

        with self.lock:
            to_delete = []

            for checkpoint_id, checkpoint in self.checkpoints.items():
                checkpoint_time = datetime.fromisoformat(checkpoint.timestamp)
                if checkpoint_time < cutoff_date:
                    to_delete.append(checkpoint_id)

            for checkpoint_id in to_delete:
                self.delete_checkpoint(checkpoint_id)

        return len(to_delete)

    def _save_checkpoint(self, checkpoint: Checkpoint):
        """Save checkpoint to disk."""
        checkpoint_file = self.checkpoint_dir / f"{checkpoint.checkpoint_id}.json"

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint.to_dict(), f, indent=2)

    def _load_checkpoints(self):
        """Load checkpoints from disk."""
        for checkpoint_file in self.checkpoint_dir.glob("*.json"):
            try:
                with open(checkpoint_file, 'r') as f:
                    data = json.load(f)
                    checkpoint = Checkpoint.from_dict(data)
                    self.checkpoints[checkpoint.checkpoint_id] = checkpoint
            except Exception as e:
                print(f"Error loading checkpoint {checkpoint_file}: {e}")


# =============================================================================
# STATE MANAGER
# =============================================================================

class StateManager:
    """Manage application state for recovery."""

    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.current_states: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()

    def save_state(
        self,
        entity_id: str,
        state: Dict[str, Any],
        use_pickle: bool = False
    ) -> str:
        """
        Save state to disk.

        Args:
            entity_id: Unique identifier for entity
            state: State dictionary to save
            use_pickle: Use pickle for complex objects

        Returns:
            Path to saved state file
        """
        with self.lock:
            self.current_states[entity_id] = state

        state_file = self.state_dir / f"{entity_id}.{'pkl' if use_pickle else 'json'}"

        if use_pickle:
            with open(state_file, 'wb') as f:
                pickle.dump(state, f)
        else:
            with open(state_file, 'w') as f:
                json.dump(state, f, indent=2)

        return str(state_file)

    def load_state(
        self,
        entity_id: str,
        use_pickle: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Load state from disk."""
        state_file = self.state_dir / f"{entity_id}.{'pkl' if use_pickle else 'json'}"

        if not state_file.exists():
            return None

        try:
            if use_pickle:
                with open(state_file, 'rb') as f:
                    state = pickle.load(f)
            else:
                with open(state_file, 'r') as f:
                    state = json.load(f)

            with self.lock:
                self.current_states[entity_id] = state

            return state

        except Exception as e:
            print(f"Error loading state for {entity_id}: {e}")
            return None

    def get_current_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get current in-memory state."""
        with self.lock:
            return self.current_states.get(entity_id)

    def delete_state(self, entity_id: str) -> bool:
        """Delete state."""
        with self.lock:
            self.current_states.pop(entity_id, None)

        for ext in ['json', 'pkl']:
            state_file = self.state_dir / f"{entity_id}.{ext}"
            if state_file.exists():
                state_file.unlink()
                return True

        return False


# =============================================================================
# RECOVERY MANAGER
# =============================================================================

class RecoveryManager:
    """Manage error recovery and task restoration."""

    def __init__(
        self,
        checkpoint_manager: CheckpointManager,
        state_manager: StateManager,
        max_retries: int = 3
    ):
        self.checkpoint_manager = checkpoint_manager
        self.state_manager = state_manager
        self.max_retries = max_retries

        self.recovery_attempts: Dict[str, int] = {}
        self.lock = threading.Lock()

    def recover_from_checkpoint(
        self,
        checkpoint_id: str,
        recovery_fn: Callable[[Dict[str, Any]], Any]
    ) -> Any:
        """
        Recover and retry task from checkpoint.

        Args:
            checkpoint_id: Checkpoint to recover from
            recovery_fn: Function to execute with recovered state

        Returns:
            Result of recovery function
        """
        checkpoint = self.checkpoint_manager.get_checkpoint(checkpoint_id)

        if not checkpoint:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        # Check retry limit
        with self.lock:
            attempts = self.recovery_attempts.get(checkpoint_id, 0)
            if attempts >= self.max_retries:
                raise RuntimeError(f"Max retries ({self.max_retries}) exceeded for {checkpoint_id}")

            self.recovery_attempts[checkpoint_id] = attempts + 1

        # Update checkpoint status
        self.checkpoint_manager.update_checkpoint(
            checkpoint_id,
            status=CheckpointStatus.IN_PROGRESS,
            metadata={'recovery_attempt': attempts + 1}
        )

        try:
            # Execute recovery function with saved state
            result = recovery_fn(checkpoint.state)

            # Mark as completed
            self.checkpoint_manager.update_checkpoint(
                checkpoint_id,
                status=CheckpointStatus.COMPLETED
            )

            # Clear retry count
            with self.lock:
                self.recovery_attempts.pop(checkpoint_id, None)

            return result

        except Exception as e:
            # Mark as failed
            self.checkpoint_manager.update_checkpoint(
                checkpoint_id,
                status=CheckpointStatus.FAILED,
                metadata={'error': str(e)}
            )

            raise

    def auto_recover_task(
        self,
        task_id: str,
        task_fn: Callable[[Dict[str, Any]], Any]
    ) -> Any:
        """Automatically recover from latest checkpoint for task."""
        checkpoint = self.checkpoint_manager.get_latest_checkpoint(task_id)

        if not checkpoint:
            raise ValueError(f"No checkpoint found for task: {task_id}")

        return self.recover_from_checkpoint(checkpoint.checkpoint_id, task_fn)

    def rollback_to_checkpoint(
        self,
        checkpoint_id: str,
        rollback_fn: Optional[Callable[[Dict[str, Any]], None]] = None
    ) -> bool:
        """
        Rollback state to a checkpoint.

        Args:
            checkpoint_id: Checkpoint to rollback to
            rollback_fn: Optional function to execute rollback logic
        """
        checkpoint = self.checkpoint_manager.get_checkpoint(checkpoint_id)

        if not checkpoint:
            return False

        try:
            # Restore state
            self.state_manager.save_state(checkpoint.task_id, checkpoint.state)

            # Execute custom rollback logic
            if rollback_fn:
                rollback_fn(checkpoint.state)

            # Update checkpoint status
            self.checkpoint_manager.update_checkpoint(
                checkpoint_id,
                status=CheckpointStatus.ROLLED_BACK
            )

            return True

        except Exception as e:
            print(f"Error during rollback: {e}")
            return False


# =============================================================================
# RESILIENT TASK WRAPPER
# =============================================================================

class ResilientTask:
    """Wrapper for tasks with automatic checkpointing and recovery."""

    def __init__(
        self,
        task_id: str,
        task_name: str,
        checkpoint_manager: CheckpointManager,
        state_manager: StateManager,
        recovery_manager: RecoveryManager
    ):
        self.task_id = task_id
        self.task_name = task_name
        self.checkpoint_manager = checkpoint_manager
        self.state_manager = state_manager
        self.recovery_manager = recovery_manager

        self.current_checkpoint_id: Optional[str] = None

    def execute_with_checkpoints(
        self,
        task_fn: Callable,
        initial_state: Dict[str, Any],
        checkpoint_interval: int = 5
    ) -> Any:
        """
        Execute task with automatic checkpointing.

        Args:
            task_fn: Task function to execute
            initial_state: Initial task state
            checkpoint_interval: Create checkpoint every N operations
        """
        # Create initial checkpoint
        self.current_checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_id=self.task_id,
            task_name=self.task_name,
            state=initial_state
        )

        try:
            # Execute task
            result = task_fn(initial_state)

            # Mark as completed
            self.checkpoint_manager.update_checkpoint(
                self.current_checkpoint_id,
                status=CheckpointStatus.COMPLETED
            )

            return result

        except Exception as e:
            # Mark as failed
            self.checkpoint_manager.update_checkpoint(
                self.current_checkpoint_id,
                status=CheckpointStatus.FAILED,
                metadata={'error': str(e)}
            )

            # Attempt recovery
            print(f"Task failed, attempting recovery: {e}")
            return self.recovery_manager.recover_from_checkpoint(
                self.current_checkpoint_id,
                task_fn
            )

    def create_intermediate_checkpoint(self, current_state: Dict[str, Any]):
        """Create intermediate checkpoint during long-running task."""
        if self.current_checkpoint_id:
            self.checkpoint_manager.update_checkpoint(
                self.current_checkpoint_id,
                state=current_state
            )


# =============================================================================
# DECORATORS FOR AUTOMATIC RECOVERY
# =============================================================================

def with_checkpoints(
    task_id: str,
    checkpoint_manager: CheckpointManager = None
):
    """Decorator to add automatic checkpointing to functions."""
    if checkpoint_manager is None:
        checkpoint_manager = CheckpointManager()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Capture function state
            state = {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            }

            # Create checkpoint
            checkpoint_id = checkpoint_manager.create_checkpoint(
                task_id=task_id,
                task_name=func.__name__,
                state=state
            )

            try:
                result = func(*args, **kwargs)

                # Mark as completed
                checkpoint_manager.update_checkpoint(
                    checkpoint_id,
                    status=CheckpointStatus.COMPLETED
                )

                return result

            except Exception as e:
                # Mark as failed
                checkpoint_manager.update_checkpoint(
                    checkpoint_id,
                    status=CheckpointStatus.FAILED,
                    metadata={'error': str(e)}
                )
                raise

        return wrapper
    return decorator


def auto_retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator for automatic retry with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)

                except Exception as e:
                    last_exception = e

                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)
                        print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                        time.sleep(wait_time)
                    else:
                        print(f"All {max_attempts} attempts failed")

            raise last_exception

        return wrapper
    return decorator


# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

# Create global recovery system
checkpoint_manager = CheckpointManager()
state_manager = StateManager()
recovery_manager = RecoveryManager(checkpoint_manager, state_manager)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def create_checkpoint(task_id: str, task_name: str, state: Dict[str, Any]) -> str:
    """Create a checkpoint."""
    return checkpoint_manager.create_checkpoint(task_id, task_name, state)


def recover_from_checkpoint(checkpoint_id: str, recovery_fn: Callable) -> Any:
    """Recover from a checkpoint."""
    return recovery_manager.recover_from_checkpoint(checkpoint_id, recovery_fn)


def save_task_state(task_id: str, state: Dict[str, Any]) -> str:
    """Save task state."""
    return state_manager.save_state(task_id, state)


def load_task_state(task_id: str) -> Optional[Dict[str, Any]]:
    """Load task state."""
    return state_manager.load_state(task_id)


def get_latest_checkpoint(task_id: str) -> Optional[Checkpoint]:
    """Get latest checkpoint for task."""
    return checkpoint_manager.get_latest_checkpoint(task_id)


def cleanup_old_checkpoints(days: int = 7) -> int:
    """Clean up old checkpoints."""
    return checkpoint_manager.cleanup_old_checkpoints(days)


__all__ = [
    'CheckpointStatus',
    'Checkpoint',
    'CheckpointManager',
    'StateManager',
    'RecoveryManager',
    'ResilientTask',
    'with_checkpoints',
    'auto_retry',
    'checkpoint_manager',
    'state_manager',
    'recovery_manager',
    'create_checkpoint',
    'recover_from_checkpoint',
    'save_task_state',
    'load_task_state',
    'get_latest_checkpoint',
    'cleanup_old_checkpoints'
]
