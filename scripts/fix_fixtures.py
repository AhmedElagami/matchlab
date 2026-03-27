"""Remove core.organization entries from fixtures and convert
organization FK references back to plain text strings."""

import json
import glob

# Map org PKs back to their text names (from the organization entries)
def fix_fixture(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # First pass: build org PK -> name map from core.organization entries
    org_map = {}
    for obj in data:
        if obj["model"] == "core.organization":
            org_map[obj["pk"]] = obj["fields"]["name"]

    # Remove core.organization entries
    data = [obj for obj in data if obj["model"] != "core.organization"]

    # Fix participant organization fields (convert FK int -> text)
    for obj in data:
        if obj["model"] == "core.participant":
            org_val = obj["fields"].get("organization")
            if isinstance(org_val, int) and org_val in org_map:
                obj["fields"]["organization"] = org_map[org_val]

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"  ✓ {filepath} (removed {len(org_map)} org entries)")

if __name__ == "__main__":
    files = sorted(glob.glob("fixtures/*.json"))
    for fp in files:
        fix_fixture(fp)
    print("Done.")
