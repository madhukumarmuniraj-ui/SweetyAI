from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.recovery.checkpoint_system import CheckpointManager
from app.sandbox.diff_verifier import DiffResult, DiffVerifier

logger = logging.getLogger(__name__)


@dataclass
class PatchPreview:
    filepath: str
    original_content: str
    patched_content: str
    diff: DiffResult
    checksum_before: str
    checksum_after: str
    lines_changed: int
    is_new_file: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "filepath": self.filepath,
            "diff": self.diff.to_dict(),
            "checksum_before": self.checksum_before,
            "checksum_after": self.checksum_after,
            "lines_changed": self.lines_changed,
            "is_new_file": self.is_new_file,
        }


class DryRunPatcher:
    """
    Computes safe dry-run diff manifests before touching disk,
    provides visual diff preview metadata, and applies atomic writes with rollback checkpoints.
    """

    def __init__(self, checkpoint_mgr: Optional[CheckpointManager] = None):
        self.checkpoint_mgr = checkpoint_mgr or CheckpointManager()

    def _hash_str(self, s: str) -> str:
        return hashlib.sha256(s.encode("utf-8")).hexdigest()[:12]

    def preview_patch(self, filepath: str, new_content: str) -> PatchPreview:
        is_new = not os.path.exists(filepath)
        original_content = ""

        if not is_new:
            try:
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    original_content = f.read()
            except Exception as e:
                logger.warning(f"[DryRunPatcher] Could not read {filepath}: {e}")

        diff = DiffVerifier.compute_diff(
            original_content,
            new_content,
            filename=os.path.basename(filepath),
        )

        return PatchPreview(
            filepath=filepath,
            original_content=original_content,
            patched_content=new_content,
            diff=diff,
            checksum_before=self._hash_str(original_content),
            checksum_after=self._hash_str(new_content),
            lines_changed=diff.additions + diff.deletions,
            is_new_file=is_new,
        )

    def apply_patch(
        self,
        filepath: str,
        new_content: str,
        create_backup: bool = True,
    ) -> Dict[str, Any]:
        checkpoint_id = None
        orig_content = ""

        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                orig_content = f.read()

        if create_backup:
            checkpoint_id = self.checkpoint_mgr.create_checkpoint(
                task_id="patch_backup",
                task_name=f"Backup before patching {os.path.basename(filepath)}",
                state={"filepath": filepath, "original_content": orig_content},
                metadata={"filepath": filepath},
            )

        # Atomic write
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        temp_file = f"{filepath}.tmp"

        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            if os.path.exists(filepath):
                os.remove(filepath)
            os.rename(temp_file, filepath)

            logger.info(f"[DryRunPatcher] Safely patched {filepath} (Checkpoint: {checkpoint_id})")
            return {
                "ok": True,
                "filepath": filepath,
                "checkpoint_id": checkpoint_id,
                "checksum": self._hash_str(new_content),
                "message": f"File '{os.path.basename(filepath)}' patched successfully.",
            }
        except Exception as e:
            logger.error(f"[DryRunPatcher] Failed to write {filepath}: {e}")
            if os.path.exists(temp_file):
                os.remove(temp_file)
            return {
                "ok": False,
                "filepath": filepath,
                "error": str(e),
                "checkpoint_id": checkpoint_id,
            }
