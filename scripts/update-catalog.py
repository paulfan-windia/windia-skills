#!/usr/bin/env python3
"""Render the public catalog from verified product metadata; no external API calls."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "catalog/products.json").read_text())
assert data["brand"] == "WINDIA"
ids = set()
rows = []
for product in data["products"]:
    assert product["id"] not in ids
    ids.add(product["id"])
    assert product["name"].startswith("WINDIA ")
    assert isinstance(product["price_usd"], (int, float)) and product["price_usd"] >= 0
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", product["verified_on"])
    assert product["status"] in {"Live", "Available", "Pending Review", "Planned", "Retired"}
    price = "Free" if product["price_usd"] == 0 else f"USD {product['price_usd']:.2f}"
    if product.get("pricing_model") == "one_time":
        price += " one-time"
    version = product.get("version") or "Not recorded"
    availability = product['status']
    if product.get('agensi_status') and product.get('agensi_url') and 'GitHub' in product['platform']:
        availability += f" on GitHub / [Agensi: {product['agensi_status']}]({product['agensi_url']})"
    rows.append(f"| [{product['name']}]({product['url']}) | {version} | {price} | {product['platform']} | {availability} | {product['verified_on']} |")
table = "\n".join([
    "| Product | Version | Price | Distribution | Last verified status | Verified on |",
    "| --- | --- | --- | --- | --- | --- |", *rows,
])
notice = "Platform status and prices are recorded from the latest verified listing information. Planned and Pending Review entries are not live offers. Agensi product links are provided when verified; use the search terms below when needed."
searches = "\n".join(f"- **{p['name']}**: `{p['search_term']}`" for p in data["products"] if "Agensi" in p["platform"])
catalog = f"# WINDIA product catalog\n\n<p align=\"center\"><img src=\"assets/windia-skill-logo.png\" alt=\"WINDIA\" width=\"180\" /></p>\n\n{table}\n\n{notice}\n\n## Agensi search terms\n\n{searches}\n\n## Planned skills\n\n" + "\n".join(f"- {x}" for x in data["roadmap"]) + "\n\nRoadmap items are planned products, not current released capabilities.\n\n## Maintenance\n\nThe source of truth is [catalog/products.json](catalog/products.json). After a listing is checked, update its price, version, status and verified date there. The catalog workflow regenerates this page and the README table. It does not query Agensi or assume that a pending listing has been approved.\n\nContact esofanwentao@gmail.com.\n"
(ROOT / "CATALOG.md").write_text(catalog)
readme = ROOT / "README.md"
text = readme.read_text()
start = "<!-- WINDIA-CATALOG:START -->"
end = "<!-- WINDIA-CATALOG:END -->"
assert text.count(start) == text.count(end) == 1
text = text.split(start)[0] + start + "\n\n" + table + "\n\n" + end + text.split(end)[1]
readme.write_text(text)
print(f"Rendered {len(rows)} WINDIA product records.")
