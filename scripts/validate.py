#!/usr/bin/env python3
"""화산혜은 MasterCanon 데이터 검증기.

출력 형식: `path: field: reason`. 오류가 없으면 exit 0.
"""
import argparse
import copy
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

STATUSES = {"draft", "confirmed", "disputed", "superseded"}
errors = []


def err(path, field, reason):
    errors.append(f"{path}: {field}: {reason}")


def rel(root, p):
    return str(Path(p).relative_to(root))


def load(root, p):
    try:
        text = Path(p).read_text(encoding="utf-8")
        return json.loads(text) if str(p).endswith(".json") else yaml.safe_load(text)
    except Exception as e:  # parse error
        err(rel(root, p), "-", f"parse error: {str(e).splitlines()[0]}")
        return None


def fpath(e):
    return ".".join(str(x) for x in e.absolute_path) or "(root)"


def check_schema(root, p, data, schema):
    for e in sorted(Draft202012Validator(schema).iter_errors(data), key=lambda x: list(map(str, x.absolute_path))):
        reason = e.message
        if e.validator == "enum" and fpath(e).split(".")[-1] in ("status", "record_status"):
            reason = f"invalid status value {e.instance!r}; allowed: {sorted(STATUSES)}"
        err(rel(root, p), fpath(e), reason)


def relax(schema):
    s = copy.deepcopy(schema)
    for k in ("id", "name_ko"):
        s["properties"][k] = {"type": ["string", "null"]}
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    root = Path(ap.parse_args().root).resolve()

    schemas = {}
    for n in ("character", "faction", "assets", "sources"):
        schemas[n] = load(root, root / "schemas" / f"{n}.schema.json")
    if any(v is None for v in schemas.values()):
        return finish()

    # templates (null 허용)
    for n in ("character", "faction"):
        p = root / "templates" / f"{n}.yaml"
        if p.exists():
            d = load(root, p)
            if d is not None:
                check_schema(root, p, d, relax(schemas[n]))

    ids = {}  # id -> (kind, path)
    def reg(kind, i, p, field):
        if not isinstance(i, str):
            return
        if i in ids:
            err(rel(root, p), field, f"duplicate id {i!r} (already used by {ids[i][0]} in {ids[i][1]})")
        else:
            ids[i] = (kind, rel(root, p))

    records = []
    for kind, sub in (("character", "characters"), ("faction", "factions")):
        for p in sorted((root / "canon" / sub).glob("*.yaml")):
            d = load(root, p)
            if d is None:
                continue
            check_schema(root, p, d, schemas[kind])
            if isinstance(d, dict):
                reg(kind, d.get("id"), p, "id")
                records.append((kind, p, d))

    lists = {}
    for kind, f, key in (("asset", "assets/manifest.yaml", "assets"), ("source", "sources/index.yaml", "sources")):
        p = root / f
        if not p.exists():
            err(f, "-", "file missing")
            continue
        d = load(root, p)
        if d is None:
            continue
        check_schema(root, p, d, schemas["assets" if kind == "asset" else "sources"])
        items = d.get(key) if isinstance(d, dict) and isinstance(d.get(key), list) else []
        lists[kind] = (p, items)
        for n, it in enumerate(items):
            if isinstance(it, dict):
                reg(kind, it.get("id"), p, f"{key}.{n}.id")

    def kind_of(i):
        return ids.get(i, (None,))[0] if isinstance(i, str) else None

    def ref(p, field, i, want):
        if kind_of(i) != want:
            err(rel(root, p), field, f"reference {i!r} is not a registered {want} id")

    def srcs(p, field, lst):
        for n, s in enumerate(lst if isinstance(lst, list) else []):
            ref(p, f"{field}.{n}", s, "source")

    def valid_src(lst):
        return isinstance(lst, list) and any(kind_of(s) == "source" for s in lst)

    for kind, p, d in records:
        if kind == "character":
            prof = d.get("profile") if isinstance(d.get("profile"), dict) else {}
            for n, a in enumerate(prof.get("affiliations") or []):
                ref(p, f"profile.affiliations.{n}", a, "faction")
            app = d.get("appearance") if isinstance(d.get("appearance"), dict) else {}
            for n, a in enumerate(app.get("reference_asset_ids") or []):
                ref(p, f"appearance.reference_asset_ids.{n}", a, "asset")
            for n, r in enumerate(d.get("relationships") or []):
                if not isinstance(r, dict):
                    continue
                ref(p, f"relationships.{n}.target_id", r.get("target_id"), "character")
                srcs(p, f"relationships.{n}.source_ids", r.get("source_ids"))
                if r.get("status") == "confirmed" and not valid_src(r.get("source_ids")):
                    err(rel(root, p), f"relationships.{n}.source_ids", "confirmed relationship requires at least one valid source_id")
        else:
            for k, want in (("leader_ids", "character"), ("member_ids", "character"), ("flag_asset_ids", "asset")):
                for n, a in enumerate(d.get(k) or []):
                    ref(p, f"{k}.{n}", a, want)
        for n, f in enumerate(d.get("facts") or []):
            if not isinstance(f, dict):
                continue
            srcs(p, f"facts.{n}.source_ids", f.get("source_ids"))
            if f.get("status") == "confirmed" and not valid_src(f.get("source_ids")):
                err(rel(root, p), f"facts.{n}.source_ids", "confirmed fact requires at least one valid source_id")
        ap_ = d.get("approval") if isinstance(d.get("approval"), dict) else {}
        srcs(p, "approval.source_ids", ap_.get("source_ids"))
        if d.get("record_status") == "confirmed":
            for k in ("approved_by", "approved_at"):
                if not ap_.get(k):
                    err(rel(root, p), f"approval.{k}", "confirmed record requires approval evidence")
            if not valid_src(ap_.get("source_ids")):
                err(rel(root, p), "approval.source_ids", "confirmed record requires at least one valid approval source_id")

    if "asset" in lists:
        p, items = lists["asset"]
        for n, it in enumerate(items):
            if isinstance(it, dict):
                srcs(p, f"assets.{n}.approval_source_ids", it.get("approval_source_ids"))

    # markdown local links
    link_re = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")
    for md in sorted(root.rglob("*.md")):
        parts = md.relative_to(root).parts
        if parts[0] in (".git", "node_modules"):
            continue
        text = md.read_text(encoding="utf-8")
        text = re.sub(r"```.*?```", "", text, flags=re.S)
        for m in link_re.finditer(text):
            target = m.group(1) or m.group(2)
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) or target.startswith("#"):
                continue
            t = target.split("#")[0]
            if t and not (md.parent / t).exists():
                err(rel(root, md), "link", f"local link target not found: {target}")
    return finish()


def finish():
    for e in errors:
        print(e)
    print(f"validate: {len(errors)} error(s)", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
