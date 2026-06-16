#!/usr/bin/env python3
"""ingest_kenney — fetch the FIRST sample assets (Kenney, CC0) into the graphicist library and
(re)generate the catalog. Provenance: CC0 / kenney.nl. STARTER samples — swappable later.

  python ingest_kenney.py            # download + unzip the packs, then write the catalog
  python ingest_kenney.py --catalog  # only (re)generate the catalog from already-unzipped assets

The committed artefact is the CATALOG (the library definition, with provenance/tags/license); the raw
binaries are gitignored and fetched on demand by this script.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
LICENSE, SOURCE = "CC0-1.0", "kenney.nl"
PACKS = [
    {"id": "kenney-isometric-roads", "kind": "sprite-2d", "style": "kenney-iso-2d", "ext": "png",
     "url": "https://kenney.nl/media/pages/assets/isometric-roads/d3b7757a28-1677695247/"
            "kenney_isometric-roads.zip"},
    {"id": "kenney-city-kit-commercial", "kind": "mesh-3d", "style": "kenney-3d", "ext": "glb",
     "url": "https://kenney.nl/media/pages/assets/city-kit-commercial/a742d900eb-1753115042/"
            "kenney_city-kit-commercial_2.1.zip"},
]


def _tags(stem: str) -> list[str]:
    toks = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", stem)
    return sorted({t.lower() for t in toks if t.isalpha() and len(t) > 1})


def download():
    (ASSETS / "_dl").mkdir(parents=True, exist_ok=True)
    for p in PACKS:
        dst = ASSETS / p["id"]
        if dst.exists():
            continue
        zp = ASSETS / "_dl" / (p["id"] + ".zip")
        if not zp.exists():
            print("download", p["url"])
            urllib.request.urlretrieve(p["url"], zp)
        with zipfile.ZipFile(zp) as z:
            z.extractall(dst)
        print("unzipped", dst)


def write_catalog():
    rows = []
    for p in PACKS:
        for f in sorted((ASSETS / p["id"]).rglob("*." + p["ext"])):
            if f.stem.lower() in ("preview", "thumbnail"):
                continue
            rows.append({"id": f"{p['id']}/{f.stem}", "tags": _tags(f.stem), "style": p["style"],
                         "kind": p["kind"], "provenance": "downloaded", "license": LICENSE,
                         "source": SOURCE, "path": str(f.relative_to(HERE)).replace("\\", "/")})
    out = ASSETS / "catalog.json"
    out.write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"catalog: {len(rows)} assets -> {out.relative_to(HERE)}")
    return rows


if __name__ == "__main__":
    if "--catalog" not in sys.argv:
        download()
    write_catalog()
