> phone. termux. real work.

android is a real computer. i treat it like one.

this org is the dev stack that fits in your pocket.

## stack

```
phone
  └─ termux  (no root required)
       ├─ dotfiles · setup scripts · reproducible envs
       ├─ python · node · shell · proot ubuntu
       ├─ local llm (gpu-accelerated, no cloud)
       ├─ cursor + agent skills over mcp
       └─ adb as a typed mcp surface
```

## pinned

- **[termux-toolkit](https://github.com/axe01010/termux-toolkit)** — dotfiles + scripts that turn android + termux into a reproducible dev env.
- **[android-ai-agent](https://github.com/axe01010/android-ai-agent)** — local-llm agent that controls your phone over adb. zero cloud.
- **[adb-mcp](https://github.com/axe01010/adb-mcp)** — typed mcp server wrapping adb: tap, swipe, screencap, install, logcat.
- **[cursor-on-android](https://github.com/axe01010/cursor-on-android)** — one-command cursor ide + agent setup on android. termux-native.
- **[skills-orchestrator](https://github.com/axe01010/skills-orchestrator)** — install + route cursor skills per project domain. one script.
- **[android-security-lab](https://github.com/axe01010/android-security-lab)** — apk analysis, manifest diffing, threat hunting. cli-first.

## more

- **[on-device-llm-mobile](https://github.com/axe01010/on-device-llm-mobile)** — local llm inference on android. gpu-accelerated, no api keys.
- **[mcp-server-hub](https://github.com/axe01010/mcp-server-hub)** — curated directory of mcp servers, installable from termux.
- **[security-research-hub](https://github.com/axe01010/security-research-hub)** — writeups + diagrams.
- **[nothing-phone-bootloop-recovery](https://github.com/axe01010/nothing-phone-bootloop-recovery)** — documented rescue of a nothing phone (3a) from a boot loop.

## principles

- no cloud by default. if a thing can run on a phone, it ships on a phone.
- reproducible from a single script. no "follow these 12 steps".
- if it can't run on termux, it doesn't ship in this org.

## currently

porting llama.cpp gpu paths to termux. adb-mcp needs typed wrappers for accessibility events.

## looking for

- prs on `termux-toolkit` — `shellcheck` clean, one concern per diff.
- apk samples for `android-security-lab` — manifest + dex, no personal data.
- feedback from anyone running `android-ai-agent` on a non-pixel device.

## not

- no telemetry. no analytics. no "phone home".
- no docker. no node_modules. no electron. no electron.
- no "coming soon" features without an issue.

## colophon

this readme is hand-rolled. no stats card, no visitor counter, no "profile views" widget.

## elsewhere

- portfolio: [axe01010.github.io/portfolio-v2](https://axe01010.github.io/portfolio-v2/)
- email: dm on github or open an issue
