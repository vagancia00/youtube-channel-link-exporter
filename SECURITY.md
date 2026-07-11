# Security Policy

## Supported versions

Security fixes are applied to the latest release and the current `main` branch.

## Reporting a vulnerability

Do not publish credentials, cookies, saved browser sessions, private HTML exports or other sensitive material in a public issue.

Report vulnerabilities through GitHub's private vulnerability reporting feature when available. Include:

- the affected version or commit;
- a minimal reproduction using synthetic data;
- the expected and observed behavior;
- the security impact.

## Security model

The exporter processes local HTML as inert text. It does not execute embedded JavaScript, access a browser profile, use credentials or make network requests. Output files are not overwritten unless the user explicitly requests it.
