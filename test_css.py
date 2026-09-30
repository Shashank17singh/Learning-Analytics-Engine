import pathlib

css_to_add = """
    /* Fix tab text clipping completely */
    div[data-testid="stTabs"] {
        overflow: visible !important;
    }
    div[data-testid="stTabs"] button {
        height: auto !important;
        min-height: 48px !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
        overflow: visible !important;
    }
    div[data-testid="stTabs"] button p {
        overflow: visible !important;
        white-space: normal !important;
        line-height: 1.5 !important;
        padding-top: 5px !important;
        padding-bottom: 5px !important;
        word-break: keep-all !important;
        margin-top: 5px !important;
        display: block !important;
    }
    div[data-baseweb="tab-list"] {
        overflow: visible !important;
    }
    div[data-baseweb="tab"] {
        overflow: visible !important;
    }
    div[data-baseweb="tab"] > div {
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

    # Remove old fix
    start = content.find("/* Fix tab text clipping */")
    if start != -1:
        end = content.find("</style>", start)
        content = content[:start] + content[end:]

    # Inject new fix
    content = content.replace("</style>", css_to_add)
    p.write_text(content, encoding="utf-8")
    print(f"Fixed CSS in {f}")
