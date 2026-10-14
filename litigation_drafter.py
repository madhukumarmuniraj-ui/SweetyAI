"""
SweetyAI Live Litigation Drafting Engine
Automated generation of petitions, written statements, and statutory legal notices.
"""

import sys
import json
from datetime import datetime

class LitigationDrafter:
    def __init__(self, client_name: str, opposing_party: str, cause_of_action: str):
        self.client_name = client_name
        self.opposing_party = opposing_party
        self.cause_of_action = cause_of_action
        self.timestamp = datetime.now().strftime("%Y-%m-%d")

    def generate_legal_notice(self, statutory_provision: str, demand_amount: float, notice_period_days: int = 15) -> str:
        notice = f"""
================================================================================
                         FORMAL STATUTORY LEGAL NOTICE
================================================================================
Date: {self.timestamp}

To,
{self.opposing_party}

SUBJECT: Legal Notice under {statutory_provision} for Breach of Obligations / Recovery of Dues amounting to INR {demand_amount:,.2f}.

Under instructions from and on behalf of my client, {self.client_name}, I do hereby serve you with this statutory legal notice as under:

1. That my client states the cause of action arose on account of: {self.cause_of_action}.
2. That despite multiple oral and written reminders, you have failed and neglected to clear the outstanding liability of INR {demand_amount:,.2f}.
3. That you are hereby called upon to pay the aforesaid sum within {notice_period_days} days from the receipt of this notice, failing which my client shall initiate appropriate criminal/civil proceedings under the relevant provisions of law at your sole risk, cost, and consequences.

Advocate for {self.client_name}
SweetyAI Legal Workstation
================================================================================
"""
        return notice

    def generate_petition_synopsis(self, court_name: str, legal_grounds: list) -> str:
        grounds_formatted = "\n".join([f"    (G) {ground}" for ground in legal_grounds])
        petition = f"""
================================================================================
IN THE COURT OF {court_name.upper()}
BETWEEN:
{self.client_name}                                              ... Petitioner
VERSUS
{self.opposing_party}                                           ... Respondent

SYNOPSIS AND LIST OF DATES
--------------------------------------------------------------------------------
CAUSE OF ACTION: {self.cause_of_action}

SALIENT GROUNDS:
{grounds_formatted}

PRAYER:
It is most respectfully prayed that this Hon'ble Court may be pleased to grant relief in favor of the Petitioner as prayed for in the accompanying petition.
================================================================================
"""
        return petition

if __name__ == "__main__":
    drafter = LitigationDrafter("Rahul Sharma", "M/s Apex Enterprises", "Non-payment of commercial invoices under service agreement.")
    print("--- Sample Legal Notice Preview ---")
    print(drafter.generate_legal_notice("Section 138 of the Negotiable Instruments Act read with BNS", 150000.00))
