"""List warp proofs that are (nearly) one flat colour: a black or faded proof means the warp's hold is wrong.

    python -X utf8 tools/debug/blank_proofs.py [work/qa/warp]

Exits 1 if any proof.png is blank. Uses the skill's sheet module (stdlib PNG reader).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from skill import SKILL  # noqa: E402

sys.path.insert(0, str(Path(SKILL) / "scripts"))
import sheet  # noqa: E402


def main():
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "work/qa/warp")
    bad = [p.parent.name for p in sorted(root.glob("*/proof.png")) if sheet.is_blank(sheet.read_png(str(p)))]
    for name in bad:
        print("blank", name)
    print(f"{len(bad)} blank proofs")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
