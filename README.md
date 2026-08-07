# Krish

**Developer. Hacker. Phone-as-machine advocate.**

Building production systems since 2018. Currently focused on on-device AI, MCP tooling, and mobile-first development infrastructure. Based in India.

---

## what i do

- **on-device AI agents** — local LLM inference on Android, zero cloud dependency
- **MCP / agent tooling** — typed protocol surfaces for AI-to-hardware bridges
- **mobile-first dev environments** — Termux, proot, reproducible phone-based workflows
- **security research** — APK analysis, threat detection, pentesting

## stack

```
runtime     termux · ubuntu proot · android (no root required)
language    python · shell · javascript · rust (learning)
ai          local llm · mcp · adb bridge · agent orchestration
security    apk analysis · manifest diffing · threat hunting
```

## selected work

| project | description | status |
|---------|-------------|--------|
| **[android-ai-agent](https://github.com/axe01010/android-ai-agent)** | local-llm agent that controls your phone over ADB. zero cloud. | active |
| **[adb-mcp](https://github.com/axe01010/adb-mcp)** | typed MCP server wrapping adb: tap, swipe, screencap, install, logcat. | active |
| **[termux-toolkit](https://github.com/axe01010/termux-toolkit)** | dotfiles + scripts that turn Android + Termux into a reproducible dev env. | stable |
| **[cursor-on-android](https://github.com/axe01010/cursor-on-android)** | one-command Cursor IDE + agent setup on Android. termux-native. | stable |
| **[on-device-llm-mobile](https://github.com/axe01010/on-device-llm-mobile)** | local LLM inference on Android. GPU-accelerated, no API keys. | active |
| **[mcp-server-hub](https://github.com/axe01010/mcp-server-hub)** | curated directory of MCP servers, installable from Termux. | stable |
| **[skills-orchestrator](https://github.com/axe01010/skills-orchestrator)** | install + route Cursor skills per project domain. one script. | stable |
| **[android-security-lab](https://github.com/axe01010/android-security-lab)** | APK analysis, manifest diffing, threat hunting. CLI-first. | active |

## principles

- **no cloud by default.** if a thing can run on a phone, it ships on a phone.
- **reproducible from a single script.** no "follow these 12 steps".
- **typed, tested, documented.** if it's not tested, it doesn't ship.
- **if it can't run on Termux, it doesn't ship in this org.**

## experience

- **2018–2020** — Python automation, CLI tools, Linux system administration
- **2020–2022** — Security research, APK analysis, mobile pentesting
- **2022–2024** — Dev tooling, Termux environments, Cursor agent skills
- **2024–present** — On-device AI, MCP protocol, agent orchestration

## currently

porting llama.cpp GPU paths to Termux. building typed accessibility event wrappers for ADB-MCP. researching on-device vision models for screen understanding.

## open to

- **collaboration** — on-device AI, MCP tooling, mobile security
- **contributions** — PRs welcome on all repos. shellcheck clean, one concern per diff.
- **security research** — APK samples (manifest + dex, no personal data), threat intel sharing
- **speaking / writing** — mobile-first dev, on-device AI, Termux workflows

## principles (anti-features)

- no telemetry. no analytics. no "phone home".
- no docker. no node_modules. no electron.
- no "coming soon" features without an issue.

## colophon

this README is hand-rolled. no stats card, no visitor counter, no "profile views" widget.

## contact

- github: [@axe01010](https://github.com/axe01010)
- portfolio: [krish.dev](https://krish.dev) *(coming soon)*
- email: DM on GitHub or open an issue
