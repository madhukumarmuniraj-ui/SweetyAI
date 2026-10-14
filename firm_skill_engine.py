import os
import json

SKILLS_DIR = "firm_skills"


def create_firm_skill(skill_name, description, sops_and_voice):
    os.makedirs(SKILLS_DIR, exist_ok=True)
    slug = skill_name.lower().replace(" ", "_")
    skill_path = os.path.join(SKILLS_DIR, f"{slug}.json")

    skill_data = {
        "skill_name": skill_name,
        "description": description,
        "sops_and_writing_voice": sops_and_voice,
    }

    with open(skill_path, "w", encoding="utf-8") as f:
        json.dump(skill_data, f, indent=2)

    print(f"\n=== SweetyAI Custom Firm Skill Registered ===")
    print(f"Skill Name   : {skill_name}")
    print(f"Description  : {description}")
    print(f"Saved Path   : {skill_path}")
    print("================================================\n")


def list_firm_skills():
    os.makedirs(SKILLS_DIR, exist_ok=True)
    files = [f for f in os.listdir(SKILLS_DIR) if f.endswith(".json")]
    print(f"\n=== Registered Firm SOPs & Custom AI Skills ({len(files)}) ===")
    for fname in files:
        fpath = os.path.join(SKILLS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                d = json.load(f)
            print(f" - [{d['skill_name']}] : {d['description']}")
        except Exception:
            pass
    print("===========================================================\n")
