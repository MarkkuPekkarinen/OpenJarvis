# OpenJarvis Roadmap Progress

Last updated: 2026-02-27

## Phase 17: Production Tool Parity

### Core Tools
- [x] `FileWriteTool` — `src/openjarvis/tools/file_write.py` + `tests/tools/test_file_write.py` (16 tests)
- [x] `ApplyPatchTool` — `src/openjarvis/tools/apply_patch.py` + `tests/tools/test_apply_patch.py` (13 tests)
- [x] `ShellExecTool` — `src/openjarvis/tools/shell_exec.py` + `tests/tools/test_shell_exec.py` (19 tests)
- [x] `GitTool` (4 ops) — `src/openjarvis/tools/git_tool.py` + `tests/tools/test_git_tool.py` (41 tests)
- [x] `HttpRequestTool` — `src/openjarvis/tools/http_request.py` + `tests/tools/test_http_request.py` (21 tests)
- [x] `DatabaseQueryTool` — `src/openjarvis/tools/db_query.py` + `tests/tools/test_db_query.py` (26 tests)

### Inter-Agent Tools
- [x] `AgentSpawnTool` — `src/openjarvis/tools/agent_tools.py` + `tests/tools/test_agent_tools.py`
- [x] `AgentSendTool` — (same file)
- [x] `AgentListTool` — (same file)
- [x] `AgentKillTool` — (same file, 22 tests total)

### Browser Automation
- [x] `BrowserNavigateTool` — `src/openjarvis/tools/browser.py` + `tests/tools/test_browser.py`
- [x] `BrowserClickTool` — (same file)
- [x] `BrowserTypeTool` — (same file)
- [x] `BrowserScreenshotTool` — (same file)
- [x] `BrowserExtractTool` — (same file, 71 tests total)

### Media Tools
- [x] `ImageGenerateTool` — `src/openjarvis/tools/image_tool.py` + `tests/tools/test_image_tool.py` (12 tests)
- [x] `AudioTranscribeTool` — `src/openjarvis/tools/audio_tool.py` + `tests/tools/test_audio_tool.py` (17 tests)
- [x] `PDFExtractTool` — `src/openjarvis/tools/pdf_tool.py` + `tests/tools/test_pdf_tool.py` (19 tests)

### Security Hardening
- [x] SSRF protection — `src/openjarvis/security/ssrf.py` + `tests/security/test_ssrf.py` (18 tests)
- [x] Subprocess sandbox — `src/openjarvis/security/subprocess_sandbox.py` + `tests/security/test_subprocess_sandbox.py` (11 tests)
- [x] Prompt injection scanner — `src/openjarvis/security/injection_scanner.py` + `tests/security/test_injection_scanner.py` (10 tests)
- [x] Rate limiting — `src/openjarvis/security/rate_limiter.py` + `tests/security/test_rate_limiter.py` (12 tests)
- [x] Security headers middleware — `src/openjarvis/server/middleware.py` + `tests/server/test_middleware.py` (4 tests)

### Config & Integration
- [x] New extras in `pyproject.toml`: `browser`, `media`, `pdf`, channel extras for Phase 21
- [x] `ToolsConfig.browser` section added to `config.py` (`BrowserConfig`: headless, timeout_ms, viewport)
- [x] `SecurityConfig.ssrf_protection`, `rate_limit_enabled`, `rate_limit_rpm`, `rate_limit_burst` fields

## Phase 18: CLI & API Expansion

### CLI Commands
- [x] `jarvis start/stop/restart/status` — `src/openjarvis/cli/daemon_cmd.py` + `tests/cli/test_daemon_cmd.py` (7 tests)
- [x] `jarvis chat` — `src/openjarvis/cli/chat_cmd.py` + `tests/cli/test_chat_cmd.py` (6 tests)
- [x] `jarvis agent` — `src/openjarvis/cli/agent_cmd.py` + `tests/cli/test_agent_cmd.py` (3 tests)
- [x] `jarvis workflow` — `src/openjarvis/cli/workflow_cmd.py` + `tests/cli/test_workflow_cmd.py` (4 tests)
- [x] `jarvis skill` — `src/openjarvis/cli/skill_cmd.py` + `tests/cli/test_skill_cmd.py` (4 tests)
- [x] `jarvis vault` — `src/openjarvis/cli/vault_cmd.py` + `tests/cli/test_vault_cmd.py` (6 tests)
- [x] `jarvis add` — `src/openjarvis/cli/add_cmd.py` + `tests/cli/test_add_cmd.py` (5 tests)

### API Endpoints
- [x] Agent API endpoints — `src/openjarvis/server/api_routes.py`
- [x] Workflow API endpoints — (same file)
- [x] Memory API endpoints — (same file)
- [x] Traces API endpoints — (same file)
- [x] Telemetry API endpoints — (same file)
- [x] Skills API endpoints — (same file)
- [x] Sessions API endpoints — (same file)
- [x] Budget API endpoints — (same file)
- [x] Prometheus metrics — (same file)
- [x] Security headers middleware wired into app — `src/openjarvis/server/app.py`
- [x] All routes tested — `tests/server/test_api_routes.py` (11 tests)
- [x] WebSocket streaming endpoint — `WS /v1/chat/stream` + `tests/server/test_websocket.py` (9 tests)

## Phase 19: Learning System Productionization
- [x] GRPO Router — `src/openjarvis/learning/grpo_policy.py` (replaced stub) + `tests/learning/test_grpo_policy.py` (13 tests)
- [x] Multi-Armed Bandit Router — `src/openjarvis/learning/bandit_router.py` + `tests/learning/test_bandit_router.py` (13 tests)
- [x] Closed-Loop Skill Discovery — `src/openjarvis/learning/skill_discovery.py` + `tests/learning/test_skill_discovery.py` (10 tests)
- [x] Auto-Apply ICL Updates — modified `src/openjarvis/learning/icl_updater.py` + `tests/learning/test_icl_updates.py` (13 tests)
- [x] Learning Dashboard API — `GET /v1/learning/stats`, `GET /v1/learning/policy` + `tests/learning/test_learning_api.py` (8 tests)

## Phase 20: Desktop App (Tauri 2.0)
- [x] Tauri scaffold in `desktop/` — `src-tauri/`, `package.json`, `vite.config.ts`, `tsconfig.json`
- [x] Tauri Rust backend — `src-tauri/src/lib.rs` with 11 commands (health, energy, telemetry, traces, learning, memory, agents, jarvis CLI)
- [x] Tauri plugins — notification, shell, global-shortcut, autostart, updater, single-instance
- [x] Energy dashboard — `src/components/EnergyDashboard.tsx` (recharts line chart, auto-refresh)
- [x] Trace debugger — `src/components/TraceDebugger.tsx` (dual-panel, color-coded step timeline)
- [x] Learning curve visualization — `src/components/LearningCurve.tsx` (GRPO/bandit/ICL stats)
- [x] Memory browser — `src/components/MemoryBrowser.tsx` (search + stats)
- [x] Admin panel — `src/components/AdminPanel.tsx` (health, agents, server control)
- [x] Build successful — `.deb`, `.rpm`, `.AppImage` bundles produced
- [x] CI workflow — `.github/workflows/desktop.yml` (Linux/macOS/Windows matrix)

## Phase 21: Channels
- [x] LINE — `src/openjarvis/channels/line_channel.py`
- [x] Viber — `src/openjarvis/channels/viber_channel.py`
- [x] Facebook Messenger — `src/openjarvis/channels/messenger_channel.py`
- [x] Reddit — `src/openjarvis/channels/reddit_channel.py`
- [x] Mastodon — `src/openjarvis/channels/mastodon_channel.py`
- [x] XMPP — `src/openjarvis/channels/xmpp_channel.py`
- [x] Rocket.Chat — `src/openjarvis/channels/rocketchat_channel.py`
- [x] Zulip — `src/openjarvis/channels/zulip_channel.py`
- [x] Twitch — `src/openjarvis/channels/twitch_channel.py`
- [x] Nostr — `src/openjarvis/channels/nostr_channel.py`
- [x] All channels tested — `tests/channels/test_channels_phase21.py` (103 tests)

## Test Summary

| Phase | New Tests | Cumulative |
|-------|-----------|------------|
| Pre-existing | ~2,447 | 2,447 |
| Phase 17 | ~300 | ~2,747 |
| Phase 18 | ~56 | ~2,803 |
| Phase 19 | ~49 | ~2,852 |
| Phase 21 | ~103 | ~2,923 |
| WebSocket + Learning API | ~17 | ~2,940 |
| **Verified total** | | **2,997 passed, 42 skipped** |

## CLAUDE.md
- [x] Updated with all new tools, CLI commands, API endpoints, channels, learning policies, desktop app, config fields, and phase table
