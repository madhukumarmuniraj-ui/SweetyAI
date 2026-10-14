"""
SweetyAI Daily Cause List & Hearing Tracker Daemon
Automates cause list polling, hearing calendar synchronization, and deadline alerts.
"""

import json
from datetime import datetime, timedelta

class CauseListDaemon:
    def __init__(self):
        self.active_matters = [
            {"case_number": "CC/2026/4891", "court": "XXI ACMM Bengaluru", "petitioner": "Rahul Sharma", "respondent": "M/s Apex Enterprises", "next_date": "2026-11-05", "stage": "Cross-examination"},
            {"case_number": "OS/2026/1042", "court": "City Civil Court Bengaluru", "petitioner": "Rahul Sharma", "respondent": "Builders Corp", "next_date": "2026-11-12", "stage": "Written Statement Filing"}
        ]

    def check_upcoming_hearings(self, days_ahead: int = 7) -> list:
        today = datetime.now().date()
        upcoming = []
        for matter in self.active_matters:
            hearing_date = datetime.strptime(matter["next_date"], "%Y-%m-%d").date()
            delta = (hearing_date - today).days
            if 0 <= delta <= days_ahead:
                upcoming.append({**matter, "days_remaining": delta})
        return upcoming

    def generate_daily_digest(self) -> str:
        upcoming = self.check_upcoming_hearings(days_ahead=30)
        digest = f"""
================================================================================
                 SWEETYAI AUTOMATED CAUSE LIST DIGEST
================================================================================
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

Active Matters Monitored: {len(self.active_matters)}
Upcoming Hearings (Next 30 Days): {len(upcoming)}
--------------------------------------------------------------------------------
"""
        for item in upcoming:
            digest += f"• [{item['next_date']} - In {item['days_remaining']} days] Case: {item['case_number']} | Court: {item['court']} | Stage: {item['stage']}\n"
        digest += "================================================================================"
        return digest

if __name__ == "__main__":
    daemon = CauseListDaemon()
    print(daemon.generate_daily_digest())
