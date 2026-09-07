# Security Policy

## Reporting a vulnerability

**Do not open a public GitHub issue for a security problem.**

Report privately, either way:

1. **Preferred —** GitHub private advisory:
   [Report a vulnerability](https://github.com/vkhatana-cortexdb/Onboarding-Packs/security/advisories/new)
2. Email **security@cortexdb.ai**

Please include what you found, how to reproduce it, and what you think the impact is.
We aim to acknowledge within **3 business days** and to give you a remediation plan or a
reasoned "not a vulnerability" within **10 business days**.

Please give us a reasonable window to ship a fix before disclosing publicly. We're happy to
credit you in the advisory unless you'd rather stay anonymous.

## Scope

This repository is **documentation and onboarding scripts**. Things in scope:

- A leaked credential, token, or private hostname committed to this repo (**report privately, urgently**)
- A documented command that would damage a reader's machine, expose their keys, or send
  secrets somewhere unexpected
- A malicious or compromised change to the helper scripts under `03-harness-attach/`
- Instructions that steer readers into an insecure configuration (e.g. binding an unauthenticated
  service to a public interface)

Out of scope here — report those to the CortexDB product security contact above instead:

- Vulnerabilities in the CortexDB server, API, SDK, or hosted service itself
- Issues in third-party tools referenced by these docs (Docker, Ollama, Tika, OpenAI, …)

## If you find a committed secret

Report it privately and **do not** quote the secret value in the report body — say which file
and line, and we'll pull it. Any credential exposed this way is treated as compromised and
rotated, whether or not we think it was read.

## Notes for contributors

- `.env`, `cortex.env`, and `.signup.json` are gitignored and must stay that way.
- Example env files carry placeholders only — never a real value.
- Never paste an API key or bearer token into an issue, PR, commit message, or screenshot;
  redact them from attached logs.
- Free-tier tokens expire (~7 days), but an expired token is still a credential — don't post it.
