import sys
import os
import inspect

def print_banner():
    print("\n" + "=" * 65)
    print("         SWEETYAI - MASTER LEGAL COMMAND CONSOLE        ")
    print("         Offline Arch Linux Legal Workstation           ")
    print("=" * 65)

def show_menu():
    print("\n[Select a Legal Module to Execute]:")
    print("  1. Knowledge Base RAG Search (BNSS / NI 138 / KA Filing / Precedents)")
    print("  2. Ingest New Case File / Judgment into ChromaDB RAG")
    print("  3. Docket OCR & Scanned Order Text Extraction")
    print("  4. Bail Petition Generator (BNSS 480/482/483 | CrPC 437/438/439)")
    print("  5. High Court Quashing & Writ Engine (BNSS 528 / Art. 226)")
    print("  6. NI Act Section 138 Timeline & PCR Complaint Generator")
    print("  7. Arbitration Suite (Sec 9 / Sec 11 / Sec 34 Petitions)")
    print("  8. IBC NCLT Petition Generator (Sec 7 / Sec 9 Insolvency)")
    print("  9. Contract Review & Indian Statutory Risk Assessment")
    print(" 10. Karnataka Court Fee (KCF & SV Act) & Limitation Calculator")
    print(" 11. Chronology & List of Dates / Synopsis Extractor")
    print(" 12. Advocate Diary, Morning Briefing & Client Alerts")
    print(" 13. Court-Ready Document Exporter (HTML / DOCX)")
    print(" 14. Advanced Legal Suite (Constitutional Writ, Arbitration Challenge, NCLT IBC, Antitrust)")
    print(" 15. Super Enterprise Expansion Suite (GST, Patents, Labour, Consumer, RERA, NCLAT)")
    print(" 16. Supreme Court & High Court Benchmark & Compliance Audit")
    print(" 17. Supreme Court Practice & Due Diligence Suite (SLP, Review/Curative, Notice Reply, Diligence)")
    print(" 18. Enterprise Legal Intelligence Suite (Harvey-Inspired: Cross-Border FEMA/FDI, Litigation Predictor, DPDP Compliance)")
    print("  0. Exit")
    print("-" * 65)

def smart_call(module_name, func_name):
    """Dynamically inspects function signature, prompts for required inputs, and runs it."""
    try:
        mod = __import__(module_name)
        func = getattr(mod, func_name)
    except Exception as e:
        print(f"[Import Error] Could not load {module_name}.{func_name}: {e}")
        return

    sig = inspect.signature(func)
    kwargs = {}
    pos_args = []

    print(f"\n--- Running {module_name}.{func_name} ---")
    for name, param in sig.parameters.items():
        if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
            continue
        has_default = param.default is not inspect.Parameter.empty
        default_display = f" [default: {param.default}]" if has_default else " (required)"
        val = input(f"  Enter {name}{default_display}: ").strip()

        if not val and has_default:
            kwargs[name] = param.default
        else:
            # Convert numeric types automatically if default is int/float
            if has_default and isinstance(param.default, bool):
                kwargs[name] = val.lower() in ("true", "1", "yes", "y")
            elif has_default and isinstance(param.default, int):
                try:
                    kwargs[name] = int(val)
                except ValueError:
                    kwargs[name] = val
            elif has_default and isinstance(param.default, float):
                try:
                    kwargs[name] = float(val)
                except ValueError:
                    kwargs[name] = val
            else:
                if param.kind == inspect.Parameter.POSITIONAL_ONLY:
                    pos_args.append(val)
                else:
                    kwargs[name] = val

    try:
        result = func(*pos_args, **kwargs)
        if result is not None:
            print("\n--- Execution Output ---")
            if isinstance(result, dict):
                for k, v in result.items():
                    print(f"  • {k}: {v}")
            else:
                print(str(result)[:2500])
    except Exception as e:
        print(f"[Execution Error in {func_name}]: {e}")

def main():
    while True:
        print_banner()
        show_menu()
        choice = input("Enter your choice (0-13): ").strip()

        if choice == '1':
            q = input("\nEnter legal search query: ").strip()
            if q:
                import rag
                print("\n--- RAG Search Results ---")
                print(rag.search_knowledge_base(q))
        elif choice == '2':
            p = input("\nEnter file path to ingest into RAG: ").strip()
            if p and os.path.exists(p):
                import rag
                rag.ingest_document(p)
            else:
                print("[!] File path does not exist.")
        elif choice == '3':
            smart_call("docket_ocr", "extract_text")
        elif choice == '4':
            smart_call("bail_petition_generator", "generate_bail_bundle")
        elif choice == '5':
            smart_call("hc_quashing_writ_engine", "generate_hc_quashing_suite")
        elif choice == '6':
            sub = input("\n  [1] Compute 138 Statutory Timeline  [2] Generate Full NI 138 Bundle: ").strip()
            if sub == '1':
                smart_call("ni138_engine", "compute_ni138_timeline")
            else:
                smart_call("ni138_engine", "generate_ni138_bundle")
        elif choice == '7':
            smart_call("arbitration_engine", "generate_arbitration_suite")
        elif choice == '8':
            smart_call("ibc_engine", "generate_ibc_suite")
        elif choice == '9':
            smart_call("contract_reviewer", "review_contract")
        elif choice == '10':
            sub = input("\n  [1] Karnataka Ad Valorem Court Fee  [2] Full Calculation Suite: ").strip()
            if sub == '1':
                smart_call("court_fee_calculator", "compute_ad_valorem_karnataka")
            else:
                smart_call("court_fee_calculator", "run_calculation")
        elif choice == '11':
            smart_call("chronology_extractor", "generate_chronology_document")
        elif choice == '12':
            import advocate_diary
            print("\n  [1] Show Morning Briefing  [2] Export HTML Dashboard  [3] Full Diary CLI")
            sub = input("  Select Diary Action: ").strip()
            if sub == '1':
                advocate_diary.show_morning_briefing()
            elif sub == '2':
                advocate_diary.export_html_dashboard()
            else:
                smart_call("advocate_diary", "handle_diary_cli")
        elif choice == '13':
            smart_call("document_exporter", "export_document")
        elif choice == '14':
            print("\n[Advanced Legal Suite Options]:")
            print("  [1] Constitutional Writ Petition (Art. 226/32)")
            print("  [2] Arbitration Award Challenge (Sec. 34)")
            print("  [3] NCLT IBC Insolvency Petition (Sec. 7/9)")
            print("  [4] CCI Merger & Antitrust Assessment")
            print("  [5] IP Trademark Opposition & Rectification")
            print("  [6] SEBI / SAT Appellate Tribunal Appeal")
            sub_choice = input("Select option (1-6): ").strip()
            import advanced_legal_tools
            if sub_choice == '1':
                advanced_legal_tools.execute_advanced_tool("constitutional-writ", [])
            elif sub_choice == '2':
                advanced_legal_tools.execute_advanced_tool("arbitration-challenge", [])
            elif sub_choice == '3':
                advanced_legal_tools.execute_advanced_tool("nclt-ibc", [])
            elif sub_choice == '4':
                advanced_legal_tools.execute_advanced_tool("merger-antitrust", [])
            elif sub_choice == '5':
                advanced_legal_tools.execute_advanced_tool("ip-trademark-opposition", [])
            elif sub_choice == '6':
                advanced_legal_tools.execute_advanced_tool("sebi-sat-appeal", [])
            else:
                print("[!] Invalid option.")
        elif choice == '15':
            print("\n[Super Enterprise Expansion Suite Options]:")
            print("  [1] Tax & GST Appellate Tribunal (GSTAT) Appeal")
            print("  [2] Patent Revocation & Infringement Defense")
            print("  [3] Labour Court Industrial Dispute Statement")
            print("  [4] Consumer Commission Class Action Complaint")
            print("  [5] RERA Adjudication & Complaint Bundle")
            print("  [6] NCLAT Company Law Appellate Tribunal Appeal")
            sub_choice = input("Select option (1-6): ").strip()
            import super_legal_expansion
            if sub_choice == '1':
                super_legal_expansion.execute_super_expanded_suite("tax-gst-appeal", [])
            elif sub_choice == '2':
                super_legal_expansion.execute_super_expanded_suite("ip-patent-revocation", [])
            elif sub_choice == '3':
                super_legal_expansion.execute_super_expanded_suite("labour-industrial-dispute", [])
            elif sub_choice == '4':
                super_legal_expansion.execute_super_expanded_suite("consumer-class-action", [])
            elif sub_choice == '5':
                super_legal_expansion.execute_super_expanded_suite("rera-compliance-complaint", [])
            elif sub_choice == '6':
                super_legal_expansion.execute_super_expanded_suite("nclat-company-appeal", [])
            else:
                print("[!] Invalid option.")
        elif choice == '16':
            import supreme_court_audit
            supreme_court_audit.run_supreme_court_benchmark_audit()
        elif choice == '17':
            print("\n[Supreme Court Practice & Due Diligence Suite Options]:")
            print("  [1] Special Leave Petition (SLP) under Article 136")
            print("  [2] Review Petition (Art. 137) & Curative Petition")
            print("  [3] Advocate Reply to Legal / Statutory Notice")
            print("  [4] Corporate & Property Title Due Diligence Search")
            sub_choice = input("Select option (1-4): ").strip()
            import supreme_court_practice_suite
            if sub_choice == '1':
                supreme_court_practice_suite.execute_supreme_court_suite("slp-supreme-court", [])
            elif sub_choice == '2':
                supreme_court_practice_suite.execute_supreme_court_suite("review-curative-petition", [])
            elif sub_choice == '3':
                supreme_court_practice_suite.execute_supreme_court_suite("legal-notice-reply", [])
            elif sub_choice == '4':
                supreme_court_practice_suite.execute_supreme_court_suite("due-diligence-search", [])
            else:
                print("[!] Invalid option.")
        elif choice == '18':
            print("\n[Enterprise Legal Intelligence Suite Options (Harvey-Inspired)]: ")
            print("  [1] Cross-Border M&A / FEMA & FDI Deal Structure Analyst")
            print("  [2] AI Litigation Strategy & Settlement Probability Predictor")
            print("  [3] Enterprise DPDP Act, 2023 & Regulatory Compliance Radar")
            sub_choice = input("Select option (1-3): ").strip()
            import harvey_legal_ai_suite
            if sub_choice == '1':
                harvey_legal_ai_suite.execute_harvey_inspired_suite("cross-border-deal-analyst", [])
            elif sub_choice == '2':
                harvey_legal_ai_suite.execute_harvey_inspired_suite("comprehensive-litigation-strategy", [])
            elif sub_choice == '3':
                harvey_legal_ai_suite.execute_harvey_inspired_suite("regulatory-compliance-radar", [])
            else:
                print("[!] Invalid option.")
        elif choice == '0':
            print("\nExiting SweetyAI Master Console.")
            sys.exit(0)
        else:
            print("\n[!] Invalid selection. Choose 0-18.")

        input("\nPress Enter to return to menu...")

if __name__ == "__main__":
    main()
