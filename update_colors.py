import os

replacements = {
    "#e0e7ff": "#0f172a",
    "#818cf8": "#0f766e",
    "#6b7280": "#64748b",
    "#4b5563": "#64748b",
    "#c7d2fe": "#334155",
    "background:rgba(30,27,75,0.4)": "background:#f8fafc; border:1px solid #e2e8f0",
    "background:rgba(30,27,75,0.3)": "background:#f8fafc; border:1px solid #e2e8f0",
    "#a5b4fc": "#475569",
    "background: linear-gradient(135deg, #6366f1, #8b5cf6);": "background: linear-gradient(135deg, #0f766e, #0d9488);",
    "color: white": "color: white",
}

for root, _, files in os.walk("views"):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            for old, new in replacements.items():
                content = content.replace(old, new)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
print("done")
