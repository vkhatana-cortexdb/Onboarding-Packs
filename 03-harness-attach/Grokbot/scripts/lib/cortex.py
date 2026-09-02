"""CortexDB v1 HTTP helpers for Personal Brain ingest.

Endpoints and envelope fields follow the official docs, not guesses:
  POST {url}/v1/experience?wait=indexed
  POST {url}/v1/experience/bulk
  POST {url}/v1/blobs          (raw bytes, Content-Type = MIME)
  GET  {url}/v1/auth/whoami

Docs:
  https://cortexdb.ai/docs/api-reference/experience
  https://cortexdb.ai/docs/api-reference/blobs
  https://cortexdb.ai/docs/sdks/rest-api
  https://cortexdb.ai/docs/concepts/experience-envelope
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

# scripts/lib/cortex.py -> repo root is two levels up
REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_URL = "https://api-v1.cortexdb.ai"
DEFAULT_SCOPE = "user:vipul"
IDEM_MAX = 64


def load_env() -> Path:
    """Load dotenv from the ingest repo root, then cwd (no override)."""
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()
    return REPO_ROOT


load_env()


class CortexError(RuntimeError):
    """HTTP or envelope error talking to CortexDB."""


class ConfigError(CortexError):
    """Missing local credential/config. Standalone scripts exit 2."""


@dataclass
class Stats:
    wrote: int = 0
    skipped: int = 0
    errors: int = 0

    def summary(self, source: str) -> str:
        return f"{source}: wrote {self.wrote}, skipped {self.skipped}, errors {self.errors}"


def iso_utc(dt: datetime | float | int | str | None = None) -> str:
    """Format an instant as ISO-8601 UTC with a trailing Z (seconds)."""
    if dt is None:
        instant = datetime.now(timezone.utc)
    elif isinstance(dt, datetime):
        instant = dt
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        else:
            instant = instant.astimezone(timezone.utc)
    elif isinstance(dt, (int, float)):
        ts = float(dt)
        if ts > 1e12:
            ts /= 1000.0
        instant = datetime.fromtimestamp(ts, tz=timezone.utc)
    elif isinstance(dt, str):
        s = dt.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        instant = datetime.fromisoformat(s)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        else:
            instant = instant.astimezone(timezone.utc)
    else:
        raise TypeError(f"iso_utc: unsupported type {type(dt)!r}")
    return instant.strftime("%Y-%m-%dT%H:%M:%SZ")


def idem(prefix: str, raw: str) -> str:
    """Build a mandatory idempotency_key of at most 64 characters.

    If ``prefix + raw`` fits, use it verbatim (stable, readable).
    Otherwise SHA-1 hex of the concatenation, keeping ``prefix`` when it still fits.
    """
    prefix = prefix or ""
    raw = raw or ""
    candidate = f"{prefix}{raw}"
    if len(candidate) <= IDEM_MAX:
        return candidate
    digest = hashlib.sha1(candidate.encode("utf-8")).hexdigest()  # 40 hex chars
    if prefix and len(prefix) + len(digest) <= IDEM_MAX:
        return f"{prefix}{digest}"
    return digest[:IDEM_MAX]


def source_scope(source: str) -> str:
    """``{CORTEXDB_SCOPE}/source:{gmail|drive|airtable|slack|local}``."""
    base = os.environ.get("CORTEXDB_SCOPE", DEFAULT_SCOPE).strip().rstrip("/")
    if not base:
        base = DEFAULT_SCOPE
    return f"{base}/source:{source}"


def max_blob_bytes() -> int:
    mb = os.environ.get("BRAIN_MAX_BLOB_MB", "8").strip() or "8"
    try:
        return max(0, int(float(mb) * 1024 * 1024))
    except ValueError:
        return 8 * 1024 * 1024


def env_bool(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on", "y"}


def env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw.strip())


def _base_url() -> str:
    return os.environ.get("CORTEXDB_URL", DEFAULT_URL).strip().rstrip("/") or DEFAULT_URL


def _wait() -> str:
    return os.environ.get("CORTEXDB_WAIT", "indexed").strip() or "indexed"


def _auth_headers(*, json_body: bool = False) -> dict[str, str]:
    key = os.environ.get("CORTEXDB_API_KEY", "").strip()
    actor = os.environ.get("CORTEXDB_ACTOR", "").strip()
    if not key:
        raise ConfigError("CORTEXDB_API_KEY is not set (copy .env.example to .env)")
    if not actor:
        raise ConfigError("CORTEXDB_ACTOR is not set (must match token sub; see `cortexdb auth whoami`)")
    headers = {
        "Authorization": f"Bearer {key}",
        "X-Cortex-Actor": actor,
    }
    if json_body:
        headers["Content-Type"] = "application/json"
    return headers


def _request(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    timeout: float = 120.0,
    retries: int = 5,
    **kwargs: Any,
) -> requests.Response:
    resp: requests.Response | None = None
    for attempt in range(retries):
        resp = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
        if resp.status_code not in (429, 502, 503, 504):
            return resp
        retry_after = resp.headers.get("Retry-After")
        try:
            delay = float(retry_after) if retry_after else min(2 ** attempt, 30)
        except ValueError:
            delay = min(2 ** attempt, 30)
        time.sleep(delay)
    assert resp is not None
    return resp


def _raise_for_status(resp: requests.Response, what: str) -> None:
    if resp.status_code < 400:
        return
    body = (resp.text or "")[:800]
    raise CortexError(f"{what} failed HTTP {resp.status_code}: {body}")


def whoami() -> dict[str, Any]:
    """GET /v1/auth/whoami — verify token + X-Cortex-Actor match."""
    url = f"{_base_url()}/v1/auth/whoami"
    resp = _request("GET", url, headers=_auth_headers())
    _raise_for_status(resp, "whoami")
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text}


def experience(
    *,
    scope: str,
    modality: str,
    content: dict[str, Any],
    context: dict[str, Any],
    idempotency_key: str,
    dry_run: bool = False,
    wait: str | None = None,
) -> dict[str, Any]:
    """POST /v1/experience?wait=indexed (or CORTEXDB_WAIT).

    Envelope (required fields from the official reference):
      scope, modality, content, context (observed_at + optional labels[]),
      idempotency_key (mandatory, <= 64 chars).
    """
    key = idempotency_key if len(idempotency_key) <= IDEM_MAX else idem("", idempotency_key)
    body = {
        "scope": scope,
        "modality": modality,
        "content": content,
        "context": context,
        "idempotency_key": key,
    }
    if dry_run:
        return {"dry_run": True, "idempotency_key": key, "scope": scope}
    w = wait or _wait()
    url = f"{_base_url()}/v1/experience?wait={w}"
    resp = _request("POST", url, headers=_auth_headers(json_body=True), data=json.dumps(body))
    _raise_for_status(resp, "experience")
    if not resp.content:
        return {"status": "ok", "http": resp.status_code, "idempotency_key": key}
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text, "http": resp.status_code, "idempotency_key": key}


def experience_bulk(
    items: list[dict[str, Any]],
    *,
    scope: str,
    dry_run: bool = False,
    wait: str | None = None,
    ordering: str = "batch_throughput",
) -> dict[str, Any]:
    """POST /v1/experience/bulk (max 1000 items per official docs).

    Body: { scope, items: [{ modality, content, context, idempotency_key }, ...], ordering }
    """
    if len(items) > 1000:
        raise CortexError(f"experience_bulk: {len(items)} items exceeds the 1000-item cap")
    cleaned: list[dict[str, Any]] = []
    for item in items:
        row = dict(item)
        key = str(row.get("idempotency_key", ""))
        if len(key) > IDEM_MAX:
            row["idempotency_key"] = idem("", key)
        cleaned.append(row)
    if dry_run:
        return {"dry_run": True, "accepted": len(cleaned), "scope": scope}
    payload = {
        "scope": scope,
        "items": cleaned,
        "ordering": ordering,
    }
    w = wait or _wait()
    url = f"{_base_url()}/v1/experience/bulk?wait={w}"
    resp = _request(
        "POST",
        url,
        headers=_auth_headers(json_body=True),
        data=json.dumps(payload),
        timeout=300.0,
    )
    _raise_for_status(resp, "experience/bulk")
    if not resp.content:
        return {"accepted": len(cleaned), "http": resp.status_code}
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text, "http": resp.status_code}


def upload_blob(
    data: bytes,
    content_type: str,
    *,
    dry_run: bool = False,
) -> str:
    """POST /v1/blobs with raw bytes. Content-Type is the file MIME.

    Returns blob_id. Do not wrap the body in JSON/multipart/base64.
    """
    if dry_run:
        digest = hashlib.sha1(data).hexdigest()[:12]
        return f"blob_dry_run_{digest}"
    url = f"{_base_url()}/v1/blobs"
    headers = _auth_headers()
    headers["Content-Type"] = content_type or "application/octet-stream"
    resp = _request("POST", url, headers=headers, data=data, timeout=300.0)
    _raise_for_status(resp, "blobs")
    try:
        payload = resp.json()
    except json.JSONDecodeError as exc:
        raise CortexError(f"blob upload: non-JSON response: {resp.text[:400]}") from exc
    blob_id = payload.get("blob_id")
    if not blob_id:
        raise CortexError(f"blob upload missing blob_id: {payload}")
    return str(blob_id)


def write_text(
    *,
    source: str,
    modality: str,
    text: str,
    observed_at: str,
    labels: list[str],
    idempotency_key: str,
    dry_run: bool = False,
    kind: str = "text",
    role: str | None = None,
) -> dict[str, Any]:
    """Convenience wrapper: kind=text or kind=message (+ optional role)."""
    content: dict[str, Any]
    if kind == "message":
        content = {"kind": "message", "role": role or "user", "text": text}
    else:
        content = {"kind": "text", "text": text}
    ctx: dict[str, Any] = {"observed_at": observed_at}
    if labels:
        ctx["labels"] = labels
    return experience(
        scope=source_scope(source),
        modality=modality,
        content=content,
        context=ctx,
        idempotency_key=idempotency_key,
        dry_run=dry_run,
    )


def write_blob_ref(
    *,
    source: str,
    modality: str,
    blob_id: str,
    observed_at: str,
    labels: list[str],
    idempotency_key: str,
    dry_run: bool = False,
    transcript: str | None = None,
) -> dict[str, Any]:
    """content.kind=blob_ref. Optional transcript skips server-side re-derivation."""
    content: dict[str, Any] = {"kind": "blob_ref", "blob_id": blob_id}
    if transcript:
        content["transcript"] = transcript
    ctx: dict[str, Any] = {"observed_at": observed_at}
    if labels:
        ctx["labels"] = labels
    return experience(
        scope=source_scope(source),
        modality=modality,
        content=content,
        context=ctx,
        idempotency_key=idempotency_key,
        dry_run=dry_run,
    )


def load_demo_env() -> Path:
    """Prefer personal-brain-demo/.env (override), then repo .env."""
    demo = REPO_ROOT / "personal-brain-demo" / ".env"
    if demo.exists():
        load_dotenv(demo, override=True)
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv()
    return REPO_ROOT


def recall(
    *,
    query: str,
    scope: str | None = None,
    view: str = "descend",
    labels: list[str] | None = None,
    include: list[str] | None = None,
    observed_actor: list[str] | None = None,
    max_tokens: int = 2000,
) -> dict[str, Any]:
    """POST /v1/recall — stratified pack + context_block.

    Docs: https://cortexdb.ai/docs/api-reference/recall
    """
    base = (scope or os.environ.get("CORTEXDB_SCOPE", DEFAULT_SCOPE)).strip().rstrip("/")
    body: dict[str, Any] = {
        "scope": base,
        "view": view,
        "query": query,
        "citation_mode": "inline_with_markers",
        "diagnostics": "none",
        "budgets": {"max_tokens": max_tokens},
    }
    metadata: dict[str, Any] = {}
    if labels:
        metadata["labels"] = labels
    if observed_actor:
        metadata["observed_actor"] = observed_actor
    if metadata:
        body["filters"] = {"metadata": metadata}
    if include:
        body["include"] = include
    url = f"{_base_url()}/v1/recall"
    resp = _request("POST", url, headers=_auth_headers(json_body=True), data=json.dumps(body), timeout=120.0)
    _raise_for_status(resp, "recall")
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text, "http": resp.status_code}


def signup(*, url: str | None = None) -> dict[str, Any]:
    """POST /v1/auth/signup — anonymous 7-day PASETO. No auth header.

    Docs: https://cortexdb.ai/docs/api-reference/auth
    Body is always {}. A new signup is a new tenant; do not call this if
    a working token already exists.
    """
    base = (url or DEFAULT_URL).strip().rstrip("/") or DEFAULT_URL
    resp = _request(
        "POST",
        f"{base}/v1/auth/signup",
        headers={"Content-Type": "application/json"},
        data=json.dumps({}),
        timeout=30.0,
    )
    _raise_for_status(resp, "signup")
    try:
        payload = resp.json()
    except json.JSONDecodeError as exc:
        raise CortexError(f"signup: non-JSON response: {resp.text[:400]}") from exc
    if not payload.get("token") or not payload.get("user_id") or not payload.get("scope"):
        raise CortexError(f"signup missing token/user_id/scope: {sorted(payload.keys())}")
    return payload


def answer(
    *,
    question: str,
    scope: str | None = None,
    view: str = "descend",
    labels: list[str] | None = None,
    include: list[str] | None = None,
    max_tokens: int = 2000,
    answer_max_tokens: int = 1500,
) -> dict[str, Any]:
    """POST /v1/answer — recall + LLM in one call.

    Docs: https://cortexdb.ai/docs/api-reference/answer
    """
    base = (scope or os.environ.get("CORTEXDB_SCOPE", DEFAULT_SCOPE)).strip().rstrip("/")
    body: dict[str, Any] = {
        "scope": base,
        "view": view,
        "question": question,
        "citation_mode": "inline_with_markers",
        "diagnostics": "none",
        "budgets": {"max_tokens": max_tokens},
        "answer_max_tokens": answer_max_tokens,
    }
    if labels:
        body["filters"] = {"metadata": {"labels": labels}}
    if include:
        body["include"] = include
    url = f"{_base_url()}/v1/answer"
    resp = _request("POST", url, headers=_auth_headers(json_body=True), data=json.dumps(body), timeout=180.0)
    _raise_for_status(resp, "answer")
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text, "http": resp.status_code}


def forget(
    *,
    scope: str | None = None,
    layers: list[str] | None = None,
    memory_ids: list[str] | None = None,
    cascade: str = "derived_only",
    confirm_all: bool = False,
    audit_note: str = "",
) -> dict[str, Any]:
    """POST /v1/forget — selective derived-layer forget.

    Docs: https://cortexdb.ai/docs/api-reference/forget
    Leaves events in the WAL unless cascade=redact_events (needs extra capability).
    Empty selector requires confirm_all=True.
    """
    base = (scope or os.environ.get("CORTEXDB_SCOPE", DEFAULT_SCOPE)).strip().rstrip("/")
    selector: dict[str, Any] = {}
    if memory_ids:
        selector["memory_ids"] = memory_ids
    body: dict[str, Any] = {
        "scope": base,
        "layers": layers or ["beliefs", "facts", "episodes", "understanding"],
        "selector": selector,
        "cascade": cascade,
        "confirm_all": confirm_all,
        "audit_note": audit_note or "harness forget",
        "idempotency_key": idem("fg:", f"{base}:{','.join(memory_ids or [])}:{audit_note}"),
    }
    url = f"{_base_url()}/v1/forget"
    resp = _request("POST", url, headers=_auth_headers(json_body=True), data=json.dumps(body), timeout=120.0)
    _raise_for_status(resp, "forget")
    try:
        return resp.json()
    except json.JSONDecodeError:
        return {"raw": resp.text, "http": resp.status_code}
