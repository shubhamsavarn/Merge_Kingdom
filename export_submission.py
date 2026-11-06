#!/usr/bin/env python3
"""
Submission Exporter for Chaos Engine Labs Take-Home Assignment.

Prepares all 4 deliverables required by Section 04 of the brief:
1. Written solution document (Markdown & standalone HTML).
2. Full AI conversation logs (AI_CONVERSATION_LOGS.jsonl).
3. Summary statement on AI collaboration.
4. Time spent summary.
"""

import os
import shutil
import json

def export_all():
    print("=" * 80)
    print(" EXPORTING SUBMISSION PACKAGE - CHAOS ENGINE LABS")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Export AI conversation logs as required by Section 04 item 2
    transcript_path = r"C:\Users\shubham.savarn\.gemini\antigravity\brain\18302720-68a8-425d-b9b4-96531f482bc0\.system_generated\logs\transcript.jsonl"
    dest_log_path = os.path.join(base_dir, "AI_CONVERSATION_LOGS.jsonl")

    if os.path.exists(transcript_path):
        shutil.copyfile(transcript_path, dest_log_path)
        log_size = os.path.getsize(dest_log_path)
        print(f"[OK] Exported full raw AI logs -> {dest_log_path} ({log_size:,} bytes)")
    else:
        print("[WARN] Transcript file not found at standard path.")

    # 2. Render Markdown to standalone HTML for easy reading
    md_file = os.path.join(base_dir, "CEL_AI_Engineer_Assignment_Solution.md")
    html_file = os.path.join(base_dir, "CEL_AI_Engineer_Assignment_Solution.html")

    if os.path.exists(md_file):
        with open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Generate lightweight HTML with clean styling
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chaos Engine Labs - Take-Home Assignment Solution</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #24292e;
            max-width: 960px;
            margin: 40px auto;
            padding: 0 20px;
            background-color: #fbfbfb;
        }}
        .container {{
            background: #ffffff;
            border: 1px solid #e1e4e8;
            border-radius: 8px;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }}
        h1, h2, h3, h4 {{
            color: #0d1117;
            border-bottom: 1px solid #eaecef;
            padding-bottom: 0.3em;
        }}
        pre {{
            background-color: #f6f8fa;
            border-radius: 6px;
            padding: 16px;
            overflow-x: auto;
            border: 1px solid #e1e4e8;
            font-size: 13px;
        }}
        code {{
            font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
            background-color: #f0f2f5;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 85%;
        }}
        pre code {{
            background-color: transparent;
            padding: 0;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }}
        th, td {{
            border: 1px solid #dfe2e5;
            padding: 8px 13px;
            text-align: left;
        }}
        th {{
            background-color: #f6f8fa;
        }}
        blockquote {{
            border-left: 4px solid #0366d6;
            margin: 0;
            padding: 0 15px;
            color: #586069;
            background-color: #f1f8ff;
            border-radius: 0 4px 4px 0;
        }}
    </style>
</head>
<body>
<div class="container">
<pre style="white-space: pre-wrap; font-family: inherit; font-size: inherit; background: transparent; border: none; padding: 0;">{md_content}</pre>
</div>
</body>
</html>"""
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_template)
        print(f"[OK] Generated standalone HTML view -> {html_file}")

    print("\n" + "=" * 80)
    print(" SUBMISSION PACKAGE READY:")
    print(" 1. Written Solution: CEL_AI_Engineer_Assignment_Solution.md (& .html)")
    print(" 2. AI Logs (Raw):    AI_CONVERSATION_LOGS.jsonl")
    print(" 3. Python/Java Code: client/, server/, tests/, java/")
    print(" 4. Test Suite:       run_all_simulations.py")
    print("=" * 80)

if __name__ == "__main__":
    export_all()

