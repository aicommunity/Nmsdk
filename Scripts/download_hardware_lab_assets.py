#!/usr/bin/env python3
"""Download CC/PD pinout and board images for Firmata lab docs.

Writes into:
  Libraries/Rdk-HardwareLib/Catalog/assets/reference/
  Bin/Configs/SpikeSamples/Hardware/_shared/media/

Only saves a file when the source page/API states an allowed license
(CC BY, CC BY-SA, CC0, Public Domain). Marketplace photos are not fetched.
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "Libraries/Rdk-HardwareLib/Catalog/assets/reference"
MEDIA = ROOT / "Bin/Configs/SpikeSamples/Hardware/_shared/media"
ATTRIBUTION = ROOT / "Libraries/Rdk-HardwareLib/Catalog/assets/ATTRIBUTION.md"

USER_AGENT = (
    "NmsdkHardwareLabAssets/1.0 (educational; +https://github.com/)"
)
ALLOWED_LICENSE_RE = re.compile(
    r"(CC[\s-]?BY(?:[\s-]?SA)?(?:\s+\d(?:\.\d)?)?|CC0|Public Domain|PD)",
    re.IGNORECASE,
)
TODAY = date.today().isoformat()

ssl_ctx = ssl.create_default_context()


def request(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as resp:
        return resp.read()


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def copy_to_media(src: Path) -> None:
    MEDIA.mkdir(parents=True, exist_ok=True)
    dest = MEDIA / src.name
    dest.write_bytes(src.read_bytes())


def commons_extmetadata(title: str) -> dict:
    api = (
        "https://commons.wikimedia.org/w/api.php"
        "?action=query&format=json&prop=imageinfo"
        "&iiprop=url|extmetadata|size|mime"
        f"&titles={urllib.parse.quote(title)}"
    )
    payload = json.loads(request(api).decode("utf-8"))
    pages = payload["query"]["pages"]
    page = next(iter(pages.values()))
    info = page["imageinfo"][0]
    meta = info.get("extmetadata", {})
    return {
        "url": info["url"],
        "license": meta.get("LicenseShortName", {}).get("value", ""),
        "license_url": meta.get("LicenseUrl", {}).get("value", ""),
        "artist": re.sub(r"<[^>]+>", "", meta.get("Artist", {}).get("value", "")).strip(),
        "credit": re.sub(r"<[^>]+>", "", meta.get("Credit", {}).get("value", "")).strip(),
        "page": f"https://commons.wikimedia.org/wiki/{title.replace(' ', '_')}",
    }


def license_ok(text: str) -> bool:
    return bool(ALLOWED_LICENSE_RE.search(text or ""))


def fetch_commons(title: str, dest_name: str) -> dict | None:
    meta = commons_extmetadata(title)
    if not license_ok(meta["license"]):
        print(f"SKIP Commons {title}: license {meta['license']!r} not allowed", file=sys.stderr)
        return None
    data = request(meta["url"])
    dest = REF / dest_name
    write_bytes(dest, data)
    copy_to_media(dest)
    rec = {
        "file": dest_name,
        "source": meta["page"],
        "download": meta["url"],
        "author": meta["artist"] or "see source page",
        "license": meta["license"],
        "license_url": meta["license_url"],
        "date": TODAY,
        "bytes": len(data),
    }
    print(f"OK Commons {title} -> {dest} ({len(data)} bytes, {meta['license']})")
    return rec


def fetch_arduino_pdf(filename: str, url: str) -> dict | None:
    data = request(url)
    if not data.startswith(b"%PDF"):
        print(f"SKIP {filename}: not a PDF ({data[:16]!r})", file=sys.stderr)
        return None
    dest = REF / filename
    write_bytes(dest, data)
    copy_to_media(dest)
    rec = {
        "file": filename,
        "source": url,
        "download": url,
        "author": "Arduino",
        "license": "CC BY-SA 4.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
        "docs_license": "https://github.com/arduino/docs-content/blob/main/LICENSE.md",
        "date": TODAY,
        "bytes": len(data),
    }
    print(f"OK Arduino pinout {filename} ({len(data)} bytes)")
    return rec


def fetch_wayne_and_layne() -> list[dict]:
    """Public-domain SVG drawings; skip if the download URL is dead."""
    blog = "https://www.wayneandlayne.com/blog/2010/12/19/nice-drawings-of-the-arduino-uno-and-mega-2560/"
    try:
        html = request(blog).decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        print(f"SKIP Wayne and Layne blog: {exc}", file=sys.stderr)
        return []
    if "public domain" not in html.lower():
        print("SKIP Wayne and Layne: blog no longer states public domain", file=sys.stderr)
        return []
    pairs = re.findall(
        r'<a[^>]+href="([^"]+\.svg)"[^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL
    )
    labeled: dict[str, list[str]] = {"uno": [], "mega": []}
    for href, text in pairs:
        blob = f"{href} {re.sub(r'<[^>]+>', '', text)}".lower()
        if href.startswith("/"):
            href = "https://www.wayneandlayne.com" + href
        elif href.startswith("http") is False:
            href = urllib.parse.urljoin(blog, href)
        if "mega" in blob:
            labeled["mega"].append(href)
        elif "uno" in blob:
            labeled["uno"].append(href)
    candidates = [
        ("Arduino_UNO_Rev3.svg", labeled["uno"]),
        ("Arduino_Mega_2560_Rev3.svg", labeled["mega"]),
    ]
    out: list[dict] = []
    for name, urls in candidates:
        saved = False
        seen: set[str] = set()
        for url in urls:
            if url in seen:
                continue
            seen.add(url)
            try:
                data = request(url)
            except urllib.error.URLError:
                continue
            if b"<svg" not in data.lower():
                continue
            dest = REF / name
            write_bytes(dest, data)
            copy_to_media(dest)
            rec = {
                "file": name,
                "source": blog,
                "download": url,
                "author": "Wayne and Layne",
                "license": "Public Domain",
                "license_url": blog,
                "date": TODAY,
                "bytes": len(data),
            }
            out.append(rec)
            print(f"OK Wayne and Layne {name} from {url} ({len(data)} bytes)")
            saved = True
            break
        if not saved:
            print(f"SKIP Wayne and Layne {name}: no live SVG URL", file=sys.stderr)
    return out


def write_attribution(records: list[dict]) -> None:
    lines = [
        "# Hardware Catalog assets",
        "",
        "## Attribution",
        "",
        "- In-house shield/module SVG silhouettes: Nmsdk project license.",
        "- Downloaded reference files (vendored " + TODAY + "):",
        "",
    ]
    for rec in records:
        lines.append(f"  - `{rec['file']}`")
        lines.append(f"    - source: {rec['source']}")
        if rec.get("download") and rec["download"] != rec["source"]:
            lines.append(f"    - download: {rec['download']}")
        lines.append(f"    - author: {rec['author']}")
        lic = rec["license"]
        if rec.get("license_url"):
            lic = f"{lic} ({rec['license_url']})"
        lines.append(f"    - license: {lic}")
        if rec.get("docs_license"):
            lines.append(f"    - Arduino docs LICENSE: {rec['docs_license']}")
        lines.append(f"    - retrieved: {rec['date']} ({rec['bytes']} bytes)")
        lines.append("")
    lines.extend(
        [
            "Copies of lab illustrations also live in "
            "`Bin/Configs/SpikeSamples/Hardware/_shared/media/`.",
            "",
            "Do not copy marketplace product photos without a clear license.",
            "Arduino is a trademark of Arduino SA; do not use the logo as a product mark.",
            "CC BY-SA share-alike applies to the vendored files and derivatives in `assets/`,",
            "not to the rest of the SDK.",
            "",
        ]
    )
    ATTRIBUTION.write_text("\n".join(lines), encoding="utf-8")
    (REF / "README.md").write_text(
        "# Official pinout and board reference\n\n"
        "Vendored PDFs/SVG/photos for documentation. Licenses: see "
        "[ATTRIBUTION.md](../ATTRIBUTION.md).\n",
        encoding="utf-8",
    )
    (MEDIA / "ATTRIBUTION.md").write_text(
        "Lab illustrations. Licenses and URLs: "
        "`Libraries/Rdk-HardwareLib/Catalog/assets/ATTRIBUTION.md`.\n",
        encoding="utf-8",
    )


def main() -> int:
    records: list[dict] = []
    for filename, url in (
        (
            "A000066-full-pinout.pdf",
            "https://docs.arduino.cc/resources/pinouts/A000066-full-pinout.pdf",
        ),
        (
            "A000067-full-pinout.pdf",
            "https://docs.arduino.cc/resources/pinouts/A000067-full-pinout.pdf",
        ),
    ):
        rec = fetch_arduino_pdf(filename, url)
        if rec:
            records.append(rec)

    for title, dest in (
        ("File:Arduino MEGA2560.png", "Arduino_MEGA2560.png"),
        ("File:Arduino Uno - R3.jpg", "Arduino_Uno_R3.jpg"),
    ):
        rec = fetch_commons(title, dest)
        if rec:
            records.append(rec)

    records.extend(fetch_wayne_and_layne())
    if not records:
        print("No assets downloaded", file=sys.stderr)
        return 1
    write_attribution(records)
    print(f"Wrote attribution for {len(records)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
