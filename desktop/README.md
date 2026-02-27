# OpenJarvis Desktop

Tauri 2.0 native desktop application for OpenJarvis with auto-updates, energy monitoring, trace debugging, and learning visualization.

## Development Setup

```bash
# Prerequisites: Node.js 22+, Rust stable, system deps (see below)

cd desktop
npm install
cargo tauri dev    # Hot-reload development mode
cargo tauri build  # Production build
```

### Linux System Dependencies

```bash
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev libgtk-3-dev libappindicator3-dev \
  librsvg2-dev patchelf libxdo-dev
```

## Auto-Update Architecture

Every push to `main` (touching `desktop/` or the workflow) triggers a CI pipeline that:

1. Validates TypeScript + Rust (`validate` job)
2. Builds for Linux, macOS (ARM + Intel), and Windows (`build-and-release` job)
3. Creates/updates a `desktop-latest` pre-release on GitHub Releases
4. Uploads platform installers and a signed `latest.json` manifest

The desktop app checks `latest.json` on startup and every 30 minutes. When a newer version is found, it shows a banner prompting the user to download and relaunch.

```
Push to main -> CI builds -> desktop-latest release -> latest.json
                                                          |
Desktop app checks periodically <-------------------------+
  -> "Update available" banner
  -> Download in background
  -> "Relaunch now" prompt
```

## Releases

### Rolling (Nightly)

Automatic on every push to `main`. Users on the desktop app receive updates seamlessly.

### Stable (Versioned)

```bash
# Bump version in all 3 config files
./scripts/bump-desktop-version.sh 1.0.1

# Commit and tag
git add desktop/package.json desktop/src-tauri/tauri.conf.json desktop/src-tauri/Cargo.toml
git commit -m "chore(desktop): bump version to 1.0.1"
git tag desktop-v1.0.1
git push origin main --tags
```

CI creates a versioned GitHub Release (e.g., `desktop-v1.0.1`) with full installers.

## Code Signing

### Update Signing (Required for Auto-Updates)

Generate a key pair for signing update manifests:

```bash
cargo tauri signer generate -w ~/.tauri/openjarvis.key
```

Set the public key in `src-tauri/tauri.conf.json` under `plugins.updater.pubkey`, then add these GitHub Secrets:

| Secret | Description |
|--------|-------------|
| `TAURI_SIGNING_PRIVATE_KEY` | Contents of the `.key` file |
| `TAURI_SIGNING_PRIVATE_KEY_PASSWORD` | Password used during generation |

### macOS Notarization (Optional)

| Secret | Description |
|--------|-------------|
| `APPLE_CERTIFICATE` | Base64-encoded `.p12` certificate |
| `APPLE_CERTIFICATE_PASSWORD` | Certificate password |
| `APPLE_SIGNING_IDENTITY` | e.g., `Developer ID Application: Name (TEAMID)` |
| `APPLE_ID` | Apple ID email |
| `APPLE_PASSWORD` | App-specific password |
| `APPLE_TEAM_ID` | 10-character team ID |

### Windows Authenticode (Optional)

| Secret | Description |
|--------|-------------|
| `WINDOWS_CERTIFICATE` | Base64-encoded `.pfx` certificate |
| `WINDOWS_CERTIFICATE_PASSWORD` | Certificate password |

All signing is optional — unsigned builds work without any secrets configured.

## Dashboard Panels

- **Energy** — Real-time power monitoring (recharts)
- **Traces** — Timeline inspection with step-type color coding
- **Learning** — Policy visualization (GRPO/bandit stats)
- **Memory** — Search and stats for memory backends
- **Admin** — Health checks, agent management, server control
