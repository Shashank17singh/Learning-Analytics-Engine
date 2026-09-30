import pathlib

css_to_add = """
    /* Fix tab text clipping completely */
    button[role="tab"] {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        height: auto !important;
        overflow: visible !important;
    }
    button[role="tab"] div, button[role="tab"] p, button[role="tab"] span {
        overflow: visible !important;
        line-height: 1.6 !important;
    }
    div[data-baseweb="tab-list"] {
        overflow: visible !important;
        padding-top: 5px !important;
        padding-bottom: 5px !important;
    }
</style>"""

files = [
    "pages/1_Student_Portal.py",
    "pages/2_Admin_Portal.py",
    "app.py",
]

for f in files:
    p = pathlib.Path(f)
    content = p.read_text(encoding="utf-8")
    
    start = content.find("/* Fix tab text clipping completely */")
    if start != -1:
        end = content.find("</style>", start)
        if end != -1:
            content = content[:start] + content[end:]
            content = content.replace("</style>", css_to_add)
            p.write_text(content, encoding="utf-8")
            print(f"Fixed CSS in {f}")
        else:
            print(f"Could not find closing style tag in {f}")
    else:
        print(f"No previous fix found in {f}, skipping.")
