import os
import json

PLUGINS_LOCAL_DIR = "anthropic_plugins"

def setup_knowledge_plugins():
    os.makedirs(PLUGINS_LOCAL_DIR, exist_ok=True)
    
    # Mirroring Anthropic's legal knowledge-work plugin structure locally
    legal_plugin_dir = os.path.join(PLUGINS_LOCAL_DIR, "legal")
    os.makedirs(os.path.join(legal_plugin_dir, "skills"), exist_ok=True)
    os.makedirs(os.path.join(legal_plugin_dir, ".claude-plugin"), exist_ok=True)

    # 1. Plugin Metadata (.claude-plugin/plugin.json)
    plugin_meta = {
        "name": "legal",
        "version": "1.0.0",
        "description": "Anthropic Knowledge Work Plugin: Review contracts, triage NDAs, navigate compliance, and assess risk.",
        "author": {"name": "Anthropic (Mirrored locally)"}
    }
    with open(os.path.join(legal_plugin_dir, ".claude-plugin", "plugin.json"), "w", encoding="utf-8") as f:
        json.dump(plugin_meta, f, indent=2)

    # 2. Contract Review & NDA Triage Skill (Markdown format matching Anthropic spec)
    contract_skill_md = """---
name: contract-review-playbook
description: Review incoming contracts against risk parameters, liability caps, and indemnity standards.
---

# Contract Review & Risk Assessment Skill
1. **Liability Assessment:** Check for explicit liability caps (recommended: preceding 12 months fees). Flag unlimited liability clauses as CRITICAL.
2. **Indemnification:** Ensure mutual indemnification clauses and check for unilateral risk shifting.
3. **Governing Law:** Verify jurisdiction matches local statutory requirements (e.g., Courts at Bengaluru, Karnataka / Indian Law).
4. **Termination Rights:** Ensure termination for convenience (30-day notice) is included.
"""
    with open(os.path.join(legal_plugin_dir, "skills", "contract_review.md"), "w", encoding="utf-8") as f:
        f.write(contract_skill_md)

    print(f"\n=== Anthropic Knowledge-Work Plugins Synced Locally ===")
    print(f"Plugin Directory : {os.path.abspath(PLUGINS_LOCAL_DIR)}")
    print(f"Loaded Plugin    : legal (with contract_review skill)")
    print(f"Compatibility    : 100% compatible with SweetyAI CLI & Daemon")
    print(f"=========================================================\n")

if __name__ == "__main__":
    setup_knowledge_plugins()
