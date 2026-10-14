import os
import sys
import datetime
import re

EXPORT_DIR = "court_ready_exports"

def export_document(input_path, output_format="html"):
    os.makedirs(EXPORT_DIR, exist_ok=True)
    if not os.path.exists(input_path):
        print(f"[Error] Source file '{input_path}' not found.")
        return

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        md_text = f.read()

    base_name = os.path.basename(input_path).rsplit(".", 1)[0]
    today = datetime.datetime.now().strftime("%d-%m-%Y")

    print("\n=== SweetyAI Court-Ready Document Exporter ===")
    print(f"Source Document : {input_path}")
    print(f"Format Standard : Karnataka High Court Rules, Ch. XII Rule 2 (Verdana 12pt/14pt, A4)")

    html_body = md_text
    html_body = re.sub(r"^# (.*?)$", r"<h1>\1</h1>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^## (.*?)$", r"<h2>\1</h2>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"^### (.*?)$", r"<h3>\1</h3>", html_body, flags=re.MULTILINE)
    html_body = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", html_body)
    html_body = re.sub(r"\*(.*?)\*", r"<em>\1</em>", html_body)
    html_body = re.sub(r"`(.*?)`", r"<code>\1</code>", html_body)
    html_body = html_body.replace("\n\n", "</p><p>").replace("\n", "<br/>")

    styled_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{base_name} - High Court of Karnataka Filing Format</title>
    <style>
        @page {{
            size: A4;
            margin-top: 1.5in;
            margin-bottom: 1.5in;
            margin-left: 1.75in;
            margin-right: 1.0in;
        }}
        body {{
            font-family: Verdana, Geneva, sans-serif;
            font-size: 12pt;
            line-height: 2.0;
            color: #000;
            background: #fff;
            margin: 0;
            padding: 40px;
        }}
        h1, h2 {{
            font-family: Verdana, Geneva, sans-serif;
            font-size: 14pt;
            font-weight: bold;
            line-height: 1.15;
            text-align: center;
            text-transform: uppercase;
            margin-top: 24px;
            margin-bottom: 16px;
        }}
        h1 {{
            text-decoration: underline;
        }}
        h3 {{
            font-family: Verdana, Geneva, sans-serif;
            font-size: 12pt;
            font-weight: bold;
            line-height: 1.5;
            margin-top: 18px;
        }}
        p {{
            text-align: justify;
            text-indent: 0.5in;
            margin: 12px 0;
        }}
        .signature-block {{
            text-align: right;
            margin-top: 48px;
            line-height: 1.5;
        }}
        @media print {{
            body {{ padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="content">
        <p>{html_body}</p>
    </div>
    <div class="signature-block">
        <p>____________________________________<br/>
        <strong>ADVOCATE FOR THE PETITIONER</strong><br/>
        Enrolment No: KAR/_______/______<br/>
        High Court of Karnataka, Bengaluru<br/>
        Date: {today}</p>
    </div>
</body>
</html>"""

    out_file = os.path.join(EXPORT_DIR, f"{base_name}_court_ready.html")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(styled_html)

    print(f"[Success] High Court compliant HTML generated -> '{out_file}'")
    print("=========================================================\n")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        export_document(sys.argv[1])
    else:
        print("Usage: python3 document_exporter.py <file.md>")
