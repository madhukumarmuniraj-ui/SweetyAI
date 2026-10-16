import re

STATUTE_MAP = {
    # IPC to BNS
    "ipc_302": {"target": "BNS Section 103", "offence": "Punishment for Murder", "desc": "Death or imprisonment for life, and fine."},
    "ipc_307": {"target": "BNS Section 109", "offence": "Attempt to Murder", "desc": "Imprisonment up to 10 years and fine; if hurt is caused, up to life imprisonment."},
    "ipc_304": {"target": "BNS Section 105", "offence": "Culpable Homicide Not Amounting to Murder", "desc": "Imprisonment up to 10 years or life."},
    "ipc_376": {"target": "BNS Sections 63-64", "offence": "Rape", "desc": "Rigorous imprisonment not less than 10 years extending to life or death in aggravated cases."},
    "ipc_420": {"target": "BNS Section 318(4)", "offence": "Cheating and Dishonestly Inducing Delivery of Property", "desc": "Imprisonment up to 7 years and fine."},
    "ipc_498a": {"target": "BNS Section 85", "offence": "Cruelty by Husband or Relatives", "desc": "Imprisonment up to 3 years and fine."},
    "ipc_499": {"target": "BNS Section 356", "offence": "Defamation", "desc": "Simple imprisonment up to 2 years, or fine, or both (with community service introduced)."},
    "ipc_124a": {"target": "BNS Section 152", "offence": "Acts Endangering Sovereignty/Unity", "desc": "Replaced sedition; life imprisonment or imprisonment up to 7 years."},
    "ipc_304a": {"target": "BNS Section 106", "offence": "Causing Death by Negligence", "desc": "Imprisonment up to 5 years (up to 10 years for hit-and-run under 106(2))."},

    # CrPC to BNSS
    "crpc_41": {"target": "BNSS Section 35", "offence": "When Police may Arrest without Warrant", "desc": "Streamlined police arrest protocols and notice of appearance rules."},
    "crpc_154": {"target": "BNSS Section 173", "offence": "Information in Cognizable Cases (FIR)", "desc": "Enables e-FIR registration and electronic filing mechanisms."},
    "crpc_161": {"target": "BNSS Section 180", "offence": "Examination of Witnesses by Police", "desc": "Permits audio-video electronic recording of witness statements."},
    "crpc_438": {"target": "BNSS Section 482", "offence": "Anticipatory Bail", "desc": "Direction for grant of bail to person apprehending arrest."},
    "crpc_439": {"target": "BNSS Section 483", "offence": "Special Powers for Bail", "desc": "Bail considerations for undertrials and custody limits."},

    # Evidence Act to BSA
    "iea_27": {"target": "BSA Section 23", "offence": "Information Received from Accused in Custody", "desc": "Admissibility of information leading to the discovery of a fact while in police custody."},
    "iea_65b": {"target": "BSA Section 63", "offence": "Admissibility of Electronic Records", "desc": "Mandatory certificate requirements and digital record authentication parameters."}
}

def map_statute(query: str) -> str:
    """Map legacy criminal law sections to their modern 2023 Bharatiya Sanhita equivalents."""
    query_clean = query.lower()
    found_matches = []
    
    # Extract all distinct numbers mentioned in the query
    numbers = re.findall(r'\d+[a-zA-Z]*', query_clean)
    
    for key, data in STATUTE_MAP.items():
        key_num = key.split('_')[1]
        # Check if any extracted number matches the statute key or target
        matched = any(num == key_num or num in data["target"].lower() for num in numbers)
        if matched or query_clean in key or query_clean in data["offence"].lower():
            formatted = f"• **{data['offence']}**\n  - *Legacy Code:* {key.upper().replace('_', ' ')}\n  - *Modern Equivalent:* **{data['target']}**\n  - *Details:* {data['desc']}"
            if formatted not in found_matches:
                found_matches.append(formatted)

    if found_matches:
        return f"### Statute Mapping Results for '{query}':\n\n" + "\n\n".join(found_matches)
    else:
        return f"No direct mapping found for '{query}'. Try formatting like 'IPC 302' or 'CrPC 438'."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(map_statute(" ".join(sys.argv[1:])))
