#!/usr/bin/env python3
"""Harness helper: bootstrap a CortexDB folder, recall, then write an action.

Grok Bot has no catalog CortexDB plugin. This is the HTTP helper.

  .venv/bin/python scripts/harness.py bootstrap --dir ~/CortexDB-Personal
  .venv/bin/python scripts/harness.py recall --query "what did Grok Bot do last?"
  .venv/bin/python scripts/harness.py write --text "..." --harness grokbot --agent my-bot
"""
from __future__ import annotations

import argparse
import json
import os
import stat
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_ROOT = _SCRIPTS.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from lib.cortex import (  # noqa: E402
    DEFAULT_URL,
    ConfigError,
    CortexError,
    idem,
    iso_utc,
    load_demo_env,
    answer,
    forget,
    recall,
    signup,
    whoami,
    write_text,
)

DOC_LABEL = "doc:{doc}"
HARNESS_LABEL = "harness:{harness}"
AGENT_LABEL = "agent:{agent}"

DEFAULT_AGENTS = {
    "grokbot": "housekeepin-product",
    "claude-code": "claude-code",
    "cursor": "cursor",
    "claude-chat": "claude-chat",
}

SOURCE_FOR_HARNESS = {
    "grokbot": "grokbot",
    "claude-code": "claude",
    "claude-chat": "claude",
    "cursor": "cursor",
}

REQUIRED_ENV = ("CORTEXDB_URL", "CORTEXDB_API_KEY", "CORTEXDB_ACTOR", "CORTEXDB_SCOPE")


def _parse() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bootstrap / recall / write CortexDB harness actions")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bootstrap", help="Use existing .env or mint a 7-day anonymous tenant")
    b.add_argument("--dir", default="", help="CortexDB folder. Default: this repo, or ~/CortexDB-Personal")
    b.add_argument("--url", default=DEFAULT_URL)

    r = sub.add_parser("recall", help="POST /v1/recall")
    r.add_argument("--query", required=True)
    r.add_argument("--doc", default="", help="Optional doc: label. Empty = no doc filter.")
    r.add_argument("--labels", default="", help="Comma-separated extra labels, e.g. harness:grokbot")
    r.add_argument("--view", default="descend")
    r.add_argument("--scope", default="")
    r.add_argument("--json", action="store_true")

    w = sub.add_parser("write", help="POST /v1/experience for a harness action")
    w.add_argument("--text", required=True)
    w.add_argument("--harness", default="grokbot")
    w.add_argument("--doc", default="handoff")
    w.add_argument("--agent", default="")
    w.add_argument("--dry-run", action="store_true")

    a = sub.add_parser("answer", help="POST /v1/answer (recall + LLM)")
    a.add_argument("--question", required=True)
    a.add_argument("--labels", default="")
    a.add_argument("--view", default="descend")
    a.add_argument("--scope", default="")

    f = sub.add_parser("forget", help="POST /v1/forget (only when the user asked to delete)")
    f.add_argument("--note", required=True)
    f.add_argument("--memory-ids", default="", help="Comma-separated ids")
    f.add_argument("--confirm-all", action="store_true")
    f.add_argument("--scope", default="")
    f.add_argument("--cascade", default="derived_only")
    return p.parse_args()


def _labels(harness: str, doc: str, agent: str) -> list[str]:
    out = [
        HARNESS_LABEL.format(harness=harness),
        DOC_LABEL.format(doc=doc),
    ]
    if agent:
        out.append(AGENT_LABEL.format(agent=agent))
    return out


def _read_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def _env_complete(path: Path) -> bool:
    vals = _read_env_file(path)
    return all(vals.get(k) for k in REQUIRED_ENV)


def _find_env(root: Path) -> Path | None:
    for candidate in (root / "personal-brain-demo" / ".env", root / ".env"):
        if _env_complete(candidate):
            return candidate
    return None


def _write_env(path: Path, *, url: str, token: str, actor: str, scope: str) -> None:
    body = (
        f"CORTEXDB_URL={url}\n"
        f"CORTEXDB_API_KEY={token}\n"
        f"CORTEXDB_ACTOR={actor}\n"
        f"CORTEXDB_SCOPE={scope}\n"
        "CORTEXDB_WAIT=indexed\n"
    )
    path.write_text(body, encoding="utf-8")
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


def bootstrap(args: argparse.Namespace) -> int:
    target = Path(args.dir).expanduser() if args.dir else _ROOT
    if not args.dir and not ((_ROOT / "scripts" / "harness.py").exists()):
        target = Path.home() / "CortexDB-Personal"
    target.mkdir(parents=True, exist_ok=True)

    dest_scripts = target / "scripts"
    dest_lib = dest_scripts / "lib"
    dest_lib.mkdir(parents=True, exist_ok=True)
    src_harness = _SCRIPTS / "harness.py"
    src_cortex = _SCRIPTS / "lib" / "cortex.py"
    if src_harness.resolve() != (dest_scripts / "harness.py").resolve():
        dest_scripts.joinpath("harness.py").write_text(src_harness.read_text(encoding="utf-8"), encoding="utf-8")
    if src_cortex.resolve() != (dest_lib / "cortex.py").resolve():
        dest_lib.joinpath("cortex.py").write_text(src_cortex.read_text(encoding="utf-8"), encoding="utf-8")
        dest_lib.joinpath("__init__.py").write_text("", encoding="utf-8")
    dest_scripts.joinpath("__init__.py").write_text("", encoding="utf-8")

    gi = target / ".gitignore"
    if not gi.exists():
        gi.write_text(".env\n.signup.json\n.venv/\n__pycache__/\n", encoding="utf-8")

    existing = _find_env(target)
    if existing:
        print(f"using existing env at {existing} (token not printed)")
        load_demo_env()
        os.environ.update({k: v for k, v in _read_env_file(existing).items() if k in REQUIRED_ENV})
        try:
            me = whoami()
        except (ConfigError, CortexError) as exc:
            print(f"whoami failed on existing env: {exc}", file=sys.stderr)
            return 2
        actor = me.get("actor") or me.get("user_id") or me.get("sub")
        print(json.dumps({"ok": True, "minted": False, "dir": str(target), "actor": actor, "env": str(existing)}))
        return 0

    try:
        payload = signup(url=args.url)
    except CortexError as exc:
        print(f"signup failed: {exc}", file=sys.stderr)
        return 1

    env_path = target / ".env"
    _write_env(
        env_path,
        url=args.url.rstrip("/"),
        token=str(payload["token"]),
        actor=str(payload["user_id"]),
        scope=str(payload["scope"]),
    )
    identity = {
        "user_id": payload.get("user_id"),
        "scope": payload.get("scope"),
        "tier": payload.get("tier"),
        "expires_at": payload.get("expires_at"),
        "jti": payload.get("jti"),
        "url": args.url.rstrip("/"),
        "note": "7-day anonymous signup. Token lives only in .env (gitignored).",
    }
    (target / "identity.json").write_text(json.dumps(identity, indent=2) + "\n", encoding="utf-8")
    # keep a gitignored copy of the raw signup minus echoing to stdout
    (target / ".signup.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.chmod(target / ".signup.json", stat.S_IRUSR | stat.S_IWUSR)

    os.environ["CORTEXDB_URL"] = args.url.rstrip("/")
    os.environ["CORTEXDB_API_KEY"] = str(payload["token"])
    os.environ["CORTEXDB_ACTOR"] = str(payload["user_id"])
    os.environ["CORTEXDB_SCOPE"] = str(payload["scope"])
    try:
        me = whoami()
    except (ConfigError, CortexError) as exc:
        print(f"minted but whoami failed: {exc}", file=sys.stderr)
        return 2
    actor = me.get("actor") or payload.get("user_id")
    print(json.dumps({
        "ok": True,
        "minted": True,
        "dir": str(target),
        "actor": actor,
        "scope": payload.get("scope"),
        "expires_at": payload.get("expires_at"),
        "env": str(env_path),
    }))
    return 0


def main() -> int:
    args = _parse()
    if args.cmd == "bootstrap":
        return bootstrap(args)

    load_demo_env()
    try:
        me = whoami()
    except (ConfigError, CortexError) as exc:
        print(f"whoami failed: {exc}", file=sys.stderr)
        return 2
    del me

    if args.cmd == "recall":
        labels: list[str] = []
        if args.doc:
            labels.append(DOC_LABEL.format(doc=args.doc))
        if getattr(args, "labels", ""):
            labels.extend(s.strip() for s in args.labels.split(",") if s.strip())
        try:
            pack = recall(
                query=args.query,
                scope=args.scope or None,
                view=args.view,
                labels=labels or None,
            )
        except CortexError as exc:
            print(f"recall failed: {exc}", file=sys.stderr)
            return 1
        if args.json:
            print(json.dumps(pack, indent=2)[:8000])
            return 0
        block = pack.get("context_block") or ""
        layers = pack.get("layers") or {}
        counts = {k: len(v or []) for k, v in layers.items()}
        print(f"pack={pack.get('pack_id')} view={pack.get('view')} layers={counts}")
        print(block[:3000] if block else "(empty context_block)")
        return 0

    if args.cmd == "answer":
        labels = [s.strip() for s in args.labels.split(",") if s.strip()] if args.labels else None
        try:
            out = answer(
                question=args.question,
                scope=args.scope or None,
                view=args.view,
                labels=labels,
            )
        except CortexError as exc:
            print(f"answer failed: {exc}", file=sys.stderr)
            return 1
        text = out.get("answer") or ""
        print(f"pack={out.get('pack_id')}")
        print(text[:4000] if text else json.dumps({k: out.get(k) for k in ('pack_id','citations')}, indent=2)[:2000])
        return 0

    if args.cmd == "forget":
        ids = [s.strip() for s in args.memory_ids.split(",") if s.strip()] if args.memory_ids else None
        if not ids and not args.confirm_all:
            print("forget refused: pass --memory-ids or --confirm-all", file=sys.stderr)
            return 2
        try:
            out = forget(
                scope=args.scope or None,
                memory_ids=ids,
                confirm_all=args.confirm_all,
                cascade=args.cascade,
                audit_note=args.note,
            )
        except CortexError as exc:
            print(f"forget failed: {exc}", file=sys.stderr)
            return 1
        print(json.dumps(out, indent=2)[:4000])
        return 0

    harness = args.harness.strip()
    agent = (args.agent or DEFAULT_AGENTS.get(harness, "")).strip()
    labels = _labels(harness, args.doc, agent)
    key = idem("hk:", f"{harness}:{args.doc}:{args.text}")
    try:
        source = SOURCE_FOR_HARNESS.get(harness, harness)
        out = write_text(
            source=source,
            modality="text",
            text=args.text,
            observed_at=iso_utc(),
            labels=labels,
            idempotency_key=key,
            dry_run=args.dry_run,
            kind="text",
        )
    except CortexError as exc:
        print(f"write failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"ok": True, "labels": labels, "idempotency_key": key, "result_keys": sorted(out.keys())}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
