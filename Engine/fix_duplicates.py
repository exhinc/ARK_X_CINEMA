from pathlib import Path
from datetime import datetime

target = Path(r"C:\Users\owena\Desktop\ARK_X_CINEMA\Engine\orchestrator.py")
backup = Path(r"C:\Users\owena\Desktop\ARK_X_CINEMA\Backups") / f"orchestrator_before_duplicate_fix_{datetime.now():%Y%m%d_%H%M%S}.py"

text = target.read_text(encoding="utf-8")

start_marker = 'def filename_looks_like_ad(path):\n    name = path.stem.lower()\n\n    normalized = name.replace("-", " ")'
end_marker = "# ============================================================\n# EMBEDDED SUBTITLE DETECTION\n# ============================================================"

start_index = text.find(start_marker)
end_index = text.find(end_marker)

if start_index == -1 or end_index == -1:
    print("ERROR: Could not find the duplicate block markers. No changes made.")
    print(f"start_index={start_index}, end_index={end_index}")
else:
    backup.parent.mkdir(parents=True, exist_ok=True)
    backup.write_text(text, encoding="utf-8")
    print(f"Backup saved: {backup}")

    new_text = text[:start_index] + text[end_index:]
    target.write_text(new_text, encoding="utf-8")

    print("Duplicate block removed successfully.")
    print(f"Removed {len(text) - len(new_text)} characters.")