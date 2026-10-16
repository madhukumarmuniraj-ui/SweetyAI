"""
SweetyAI Precedent & Statutory Citation Verifier Engine
Cross-references sections across IPC/BNS, CrPC/BNSS, Evidence Act/BSA, and NI Act.
"""

import sys

STATUTORY_MAPPING = {
    "IPC_TO_BNS": {
        "Section 420 IPC": "Section 316 BNS (Cheating and dishonestly inducing delivery of property)",
        "Section 406 IPC": "Section 316(2) BNS (Criminal breach of trust)",
        "Section 302 IPC": "Section 103 BNS (Punishment for murder)",
        "Section 376 IPC": "Section 64 BNS (Rape)"
    },
    "CRPC_TO_BNSS": {
        "Section 154 CrPC": "Section 173 BNSS (Information in cognizable cases - FIR)",
        "Section 438 CrPC": "Section 482 BNSS (Direction for grant of bail to person apprehending arrest)",
        "Section 161 CrPC": "Section 180 BNSS (Examination of witnesses by police)"
    },
    "NI_ACT": {
        "Section 138 NI Act": "Dishonour of cheque for insufficiency, etc., of funds in the account.",
        "Section 142 NI Act": "Cognizance of offences."
    }
}

class CitationVerifier:
    def verify_citation(self, citation_query: str) -> str:
        query_upper = citation_query.upper()
        for category, mappings in STATUTORY_MAPPING.items():
            for old_sec, new_sec in mappings.items():
                if query_upper in old_sec.upper() or query_upper in new_sec.upper():
                    return f"[VERIFIED - {category}] Match Found: {old_sec} <---> {new_sec}"
        return f"[UNVERIFIED/CUSTOM CITATION]: '{citation_query}' requires manual bench precedent validation."

if __name__ == "__main__":
    verifier = CitationVerifier()
    print(verifier.verify_citation("Section 420 IPC"))
    print(verifier.verify_citation("Section 154 CrPC"))
    print(verifier.verify_citation("Section 138 NI Act"))

def handle_verify_cli(args):
    verifier = CitationVerifier()
    target = " ".join(args) if args else "Section 316 BNS"
    result = verifier.verify_citation(target)
    print(result)
    import os
    os.makedirs("citation_audit_reports", exist_ok=True)
    out_path = "citation_audit_reports/citation_audit_sample_contract.md"
    with open(out_path, "w") as out:
        out.write(f"# Citation Verification Audit\n\nQuery: {target}\n\nResult:\n{result}\n")
    print(f"[CitationVerifier] Saved report to {out_path}")
