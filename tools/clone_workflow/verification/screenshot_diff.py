#!/usr/bin/env python3
"""Compare screenshots and write dependency-free diff/overlay artifacts.

Single pair:
  python .../screenshot_diff.py --slug saunas --reference ref.png --actual clone.png

Directory mode compares matching relative ``*.png`` files. All generated files
and the JSON/Markdown report are written below ``.cloning/<slug>/reports``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

try:
    from .common import resolve_workspace
    from .png_tools import read_png, write_png
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import resolve_workspace  # type: ignore
    from png_tools import read_png, write_png  # type: ignore


def _name(value: str) -> str:
    return "".join(c if c.isalnum() or c in "._-" else "-" for c in value).strip("-") or "image"


def compare_pair(reference: Path, actual: Path, diff_path: Path, overlay_path: Path, pixel_threshold: int) -> dict[str, object]:
    ref_width, ref_height, ref = read_png(reference)
    actual_width, actual_height, actual = read_png(actual)
    width, height = max(ref_width, actual_width), max(ref_height, actual_height)
    diff = bytearray(width * height * 4)
    overlay = bytearray(width * height * 4)
    mismatch = 0
    for y in range(height):
        for x in range(width):
            out = (y * width + x) * 4
            in_ref = x < ref_width and y < ref_height
            in_actual = x < actual_width and y < actual_height
            rp = ref[(y * ref_width + x) * 4 : (y * ref_width + x + 1) * 4] if in_ref else (0, 0, 0, 0)
            ap = actual[(y * actual_width + x) * 4 : (y * actual_width + x + 1) * 4] if in_actual else (0, 0, 0, 0)
            different = not (in_ref and in_actual) or any(abs(rp[i] - ap[i]) > pixel_threshold for i in range(3))
            if different:
                mismatch += 1
                # Bright red is visible in reports, while alpha is opaque for
                # easy viewing in image viewers and CI artifact previews.
                diff[out : out + 4] = bytes((255, 35, 35, 255))
            else:
                grey = round((int(rp[0]) + int(rp[1]) + int(rp[2])) / 3)
                diff[out : out + 4] = bytes((grey, grey, grey, 255))
            if in_ref and in_actual:
                overlay[out : out + 4] = bytes((
                    (int(rp[0]) + int(ap[0])) // 2,
                    (int(rp[1]) + int(ap[1])) // 2,
                    (int(rp[2]) + int(ap[2])) // 2,
                    255,
                ))
            else:
                overlay[out : out + 4] = bytes((255, 0, 0, 255))
    write_png(diff_path, width, height, bytes(diff))
    write_png(overlay_path, width, height, bytes(overlay))
    total = width * height
    ratio = mismatch / total if total else 1.0
    return {
        "reference": str(reference), "actual": str(actual),
        "diff": str(diff_path), "overlay": str(overlay_path),
        "referenceWidth": ref_width, "referenceHeight": ref_height,
        "actualWidth": actual_width, "actualHeight": actual_height,
        "width": width, "height": height, "totalPixels": total,
        "diffPixels": mismatch, "mismatchRatio": ratio,
        "dimensionMismatch": ref_width != actual_width or ref_height != actual_height,
    }


def _pairs(args: argparse.Namespace, reference_root: Path | None = None, actual_root: Path | None = None) -> list[tuple[Path, Path, str]]:
    if args.reference and args.actual:
        return [(Path(args.reference), Path(args.actual), Path(args.reference).stem)]
    if not args.reference_dir or not args.actual_dir:
        raise ValueError("provide either --reference/--actual or --reference-dir/--actual-dir")
    ref_root, actual_root = Path(args.reference_dir), Path(args.actual_dir)
    ref_files = {p.relative_to(ref_root).as_posix(): p for p in ref_root.rglob("*.png")}
    actual_files = {p.relative_to(actual_root).as_posix(): p for p in actual_root.rglob("*.png")}
    names = sorted(set(ref_files) | set(actual_files))
    return [(ref_files.get(name, ref_root / name), actual_files.get(name, actual_root / name), name.replace("/", "--")[:-4])
            for name in names]


def run(args: argparse.Namespace) -> int:
    paths = resolve_workspace(args.slug, args.root)
    report_dir = paths["reports"] / "screenshots"
    report_dir.mkdir(parents=True, exist_ok=True)
    pairs = _pairs(args)
    if not pairs:
        raise ValueError("no matching PNG screenshots found")
    rows: list[dict[str, object]] = []
    for reference, actual, label in pairs:
        stem = f"{args.slug}-{_name(label)}"
        if not reference.exists() or not actual.exists():
            rows.append({"name": label, "reference": str(reference), "actual": str(actual),
                         "diff": None, "overlay": None, "diffPixels": 0,
                         "mismatchRatio": 1.0, "dimensionMismatch": False,
                         "missing": True})
            continue
        rows.append(compare_pair(reference, actual, report_dir / f"{stem}-diff.png", report_dir / f"{stem}-overlay.png", args.pixel_threshold))
        rows[-1]["name"] = label
    if not rows:
        raise ValueError("no screenshot pairs found")
    passed = all(not row.get("missing") and float(row["mismatchRatio"]) <= args.max_mismatch and not bool(row["dimensionMismatch"]) for row in rows)
    report: dict[str, object] = {
        "slug": args.slug, "generatedAt": datetime.now(timezone.utc).isoformat(),
        "pixelThreshold": args.pixel_threshold, "maxMismatch": args.max_mismatch,
        "passed": passed, "screenshots": rows,
    }
    json_path = paths["reports"] / f"{args.slug}-screenshot-diff.json"
    md_path = paths["reports"] / f"{args.slug}-screenshot-diff.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [f"# Screenshot diff: {args.slug}", "", f"Result: {'PASS' if passed else 'FAIL'}", "", "| Image | Mismatch | Dimensions |", "|---|---:|---|\n"]
    for row in rows:
        dimensions = "MISSING" if row.get("missing") else "OK" if not row["dimensionMismatch"] else f"{row['referenceWidth']}x{row['referenceHeight']} vs {row['actualWidth']}x{row['actualHeight']}"
        lines.append(f"| `{row['name']}` | {float(row['mismatchRatio']) * 100:.3f}% | {dimensions} |")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[screenshot-diff] {'PASS' if passed else 'FAIL'}; report: {json_path}")
    return 0 if passed else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--slug", required=True)
    result.add_argument("--reference")
    result.add_argument("--actual")
    result.add_argument("--reference-dir")
    result.add_argument("--actual-dir")
    result.add_argument("--root")
    result.add_argument("--pixel-threshold", type=int, default=8, help="per-channel difference, 0-255")
    result.add_argument("--max-mismatch", type=float, default=0.10, help="allowed mismatch ratio")
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(run(parser().parse_args()))
    except Exception as exc:
        print(f"[screenshot-diff] error: {exc}", file=sys.stderr)
        raise SystemExit(2)
