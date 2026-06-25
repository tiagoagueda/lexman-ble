# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single repository with **two coupled but independent deliverables**:

1. **`src/lexman_ble/`** — a standalone PyPI package (`lexman-ble`) that talks to Lexman/Leroy Merlin CCT smart bulbs over Bluetooth LE. Has no Home Assistant dependency.
2. **`custom_components/lexman_ble/`** — a Home Assistant custom integration (HACS, category `integration`) that imports the published `lexman_ble` package.

The critical, non-obvious detail: **the integration does NOT import from `src/`.** It depends on the *published PyPI release* declared in [custom_components/lexman_ble/manifest.json](custom_components/lexman_ble/manifest.json) (`requirements: ["lexman-ble==0.1.2"]`). HA installs that wheel into its own environment at runtime. So a change in `src/` is invisible to the integration until it is released to PyPI **and** the `requirements` pin (and `manifest.json` `version`) are bumped to match.

There are **three version numbers** to keep in sync, by hand where noted:
- `pyproject.toml` `project.version` — the library; bumped automatically by semantic-release on release.
- `manifest.json` `requirements` pin — which library version the integration pulls (manual).
- `manifest.json` `version` — the integration's own HACS version (manual).

## Tooling

Package/dependency manager is **`uv`** (build backend `uv_build`, dependency groups in `pyproject.toml`). Note: the [Makefile](Makefile) and [CONTRIBUTING.md](CONTRIBUTING.md) still reference `poetry` — that is stale; use `uv`. Requires Python ≥ 3.13 for the library.

Dependency groups: `ha` (Home Assistant, for type-checking the integration against), `dev` (linters). `default-groups = "all"` so `uv sync` installs everything.

## Common commands

```bash
uv sync                        # install all deps (replaces `make dev-setup` / poetry install)
uv run pre-commit install      # enable git hooks (lint + commit-msg)
uv run pre-commit run --all-files   # run the full lint/format/type-check suite

make dev-container-run          # start a throwaway HA instance in Docker with the
                                # integration + .devcontainer/configuration.yaml mounted,
                                # on http://localhost:9123 (needs host D-Bus for BLE)
make dev-container-rm           # stop & remove that container
```

There is **no test suite** — pytest config and the CI `test` job are commented out, and there is no `tests/` directory. Don't claim tests pass; there are none to run. If you add tests, re-enable the matching blocks in [.github/workflows/ci.yml](.github/workflows/ci.yml) and [CONTRIBUTING.md](CONTRIBUTING.md).

Linting/formatting is driven entirely through pre-commit ([.pre-commit-config.yaml](.pre-commit-config.yaml)): `ruff` + `ruff-format`, `mypy`, `bandit`, `codespell`, `prettier`, `pyupgrade`. CI runs `pre-commit`, `hassfest`, and `hacs/action` validation.

## Commits & releases

Commit messages **must follow Conventional Commits** — enforced by `commitizen` (commit-msg hook) and `commitlint` in CI. This is not cosmetic: [python-semantic-release](.github/workflows/ci.yml) parses commit history on every push to `main` to decide the next version, then updates `CHANGELOG.md` + `pyproject.toml` version, tags, creates a GitHub release, and publishes the library to PyPI. Commits matching `deps(...): ...` are excluded from triggering a release (see `[tool.semantic_release]` in `pyproject.toml`).

## Library architecture (`src/lexman_ble/`)

The device protocol is the heart of the package and lives in [const.py](src/lexman_ble/const.py):

- `CctSmartBulbCommand` is an `Enum` where each member carries a `(set, query, response)` triple of colon-separated hex templates with `{0}`/`{1}` byte placeholders (little-endian, split across bytes).
- `_hex_string_formatting` fills placeholders to build request bytes; `_hex_string_parsing` reverse-parses notification responses back into an int, validating that repeated placeholders agree.
- `CctSmartBulbCommandInstance` is a per-call wrapper (`.set(value)` / `.query` / `.match_response(...)`) that holds the concrete value and produces `request_bytes`.

[cct_smart_bulb.py](src/lexman_ble/cct_smart_bulb.py) — `LexmanCCTSmartBulb` is the connection-managing device class, modeled on the `led_ble` / Bluetooth-Devices pattern:

- Uses `bleak` + `bleak_retry_connector` (`establish_connection`, `@retry_bluetooth_connection_error`).
- Lazy connect on command, auto-disconnect after `DISCONNECT_DELAY` (120s) of inactivity; `_connect_lock` and `_operation_lock` serialize access.
- Commands are **fire-and-confirm**: writes go to `WRITE_CHAR_UUID`, and the *actual* state is updated in `_notification_handler` from notifications on `READ_CHAR_UUID`, then `_fire_callbacks()` notifies subscribers (the HA coordinator). `set_*` methods optimistically update local state too.
- Brightness is 0–254 on the wire but exposed as 0–255 (HA) and set via 0–100 (%). Color temperature maps between device units (153 cool … 454 warm) and Kelvin (6500 cool … 2700 warm) — note the inverted ordering, see `CCT_TEMPERATURE_*` constants.

## Integration architecture (`custom_components/lexman_ble/`)

Standard modern HA BLE config-entry integration:

- [config_flow.py](custom_components/lexman_ble/config_flow.py) — Bluetooth discovery flow; matches advertised `local_name` against `LOCAL_NAMES` in [const.py](custom_components/lexman_ble/const.py) (currently `["CCT smart bulb"]`, must also match the `bluetooth` matcher in `manifest.json`). Probes the device with `.update()` before creating the entry.
- [__init__.py](custom_components/lexman_ble/__init__.py) — `async_setup_entry` resolves the `BLEDevice` from the address, builds a `LexmanCCTSmartBulb`, wraps it in a `DataUpdateCoordinator` (polls every `UPDATE_SECONDS`=15s), registers a passive BLE advertisement callback to refresh the device handle, and waits for a first notification (`startup_event`) before declaring the entry ready.
- Runtime objects are passed via `entry.runtime_data` typed as `LexmanConfigEntry` ([typing.py](custom_components/lexman_ble/typing.py)) holding `LexmanCCTSmartBulbData` ([models.py](custom_components/lexman_ble/models.py)).
- [light.py](custom_components/lexman_ble/light.py) — the only platform (`Platform.LIGHT`); a `CoordinatorEntity` + `LightEntity` in `COLOR_TEMP` mode. It subscribes to the device's own callback in `async_added_to_hass` for push updates, on top of coordinator polling.

When extending the library/integration, keep the wire protocol in the library's `const.py`, keep HA-specific code out of `src/`, and remember the PyPI-release coupling described above before assuming integration changes take effect.
