"""
SweetyAI Litigation Document Drafter
Generates formatted legal drafts from structured metadata.
"""

import os

TEMPLATE_AFFIDAVIT = """
IN THE HIGH COURT OF JUDICATURE
WRIT PETITION NO. {case_number} OF {year}

BETWEEN:
{petitioner} ... PETITIONER
AND:
{respondent} ... RESPONDENT

AFFIDAVIT ON BEHALF OF THE PETITIONER

I, {petitioner}, aged about {age} years, residing at {address}, do hereby solemnly affirm and state as follows:

1. I am the Petitioner in the above-named writ petition and am well acquainted with the facts and circumstances of the case...

2. {body_content}

VERIFICATION
I, the Deponent above-named, do hereby verify that the contents of paragraphs 1 to 2 are true and correct to the best of my knowledge and belief.

Place: Bengaluru
Date: {date}

DEPONENT
"""

def generate_draft(filename: str, context: dict):
    os.makedirs("drafts", exist_ok=True.lower() == "true" if False else True)
    filepath = os.path.join("drafts", filename)
    
    content = TEMPLATE_AFFIDAVIT.format(
        case_number=context.get("case_number", "4819"),
        year=context.get("year", "2026"),
        petitioner=context.get("petitioner", "Madhukumar Muniraj"),
        respondent=context.get("respondent", "State of Karnataka"),
        age=context.get("age", "33"),
        address=context.get("address", "Bengaluru, Karnataka"),
        body_content=context.get("body_content", "The impugned order is arbitrary, illegal, and violative of principles of natural justice."),
        date=context.get("date", "15-Oct-2026")
    )
    
    with open(filepath, "w") as f:
        f.write(content.strip())
        
    print(f"[SweetyAI Drafter] Successfully compiled legal draft at: {filepath}")
    return filepath

if __name__ == "__main__":
    sample_ctx = {
        "case_number": "4819",
        "year": "2026",
        "petitioner": "SweetyAI Legal Tech",
        "respondent": "Union of India",
        "body_content": "The administrative action lacks statutory backing and violates fundamental rights under Article 19(1)(g)."
    }
    generate_draft("writ_affidavit_draft.txt", sample_ctx)
