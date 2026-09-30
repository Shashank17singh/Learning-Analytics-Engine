import pathlib
import re

css_to_add = """
    /* Fix tab text clipping completely */
    div[data-testid="stTabs"] button p {
        font-size: 16px !important;
        padding-top: 6px !important;
        line-height: 1.5 !important;
        overflow: visible !important;
        margin-top: 4px !important;
    }
    div[data-testid="stTabs"] button {
        height: auto !important;
        min-height: 3rem !important;
        overflow: visible !important;
        padding-top: 8px !important;
    }
    div[data-baseweb="tab-list"] {
        overflow: visible !important;
    }
    div[data-baseweb="tab"] {
        overflow: visible !important;
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
