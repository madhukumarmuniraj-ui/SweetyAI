"""
SweetyAI Docket & Cause List Ingestion Engine
Parses cause list texts and syncs deadlines to Google Workspace.
"""

import re
from google_workspace_connector import GoogleWorkspaceConnector

def parse_and_sync_docket(cause_list_text: str):
    hub = GoogleWorkspaceConnector()
    
    # Simple regex pattern for case hearing logs in cause lists
    # Example format: "W.P. 4819/2026 | Date: 2026-11-20 | Coram: Bench 1"
    pattern = r"(W\.P\.\s*\d+/\d+).*?Date:\s*([\d-]+)"
    matches = re.findall(pattern, cause_list_text)

    results = []
    for case_no, date_str in matches:
        summary = f"Hearing: {case_no}"
        start_time = f"{date_str}T10:30:00+05:30"
        end_time = f"{date_str}T11:00:00+05:30"
        
        # Sync to Calendar
        cal_res = hub.create_calendar_event(summary, start_time, end_time)
        # Sync corresponding prep task to Google Tasks
        task_res = hub.add_to_do_task(f"Prepare brief for {case_no}", date_str)
        
        results.append({"case": case_no, "calendar": cal_res, "task": task_res})
        
    return results

if __name__ == "__main__":
    sample_cause_list = """
    High Court Daily Board:
    1. W.P. 4819/2026 | Date: 2026-11-20 | Coram: Hon'ble Judge
    2. W.P. 5012/2026 | Date: 2026-11-22 | Coram: Hon'ble Judge
    """
    print("Parsing sample cause list...")
    print(parse_and_sync_docket(sample_cause_list))
