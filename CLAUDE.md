# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A **self-contained Home Assistant custom integration** (HACS, category `integration`) for Lexman/Leroy Merlin CCT smart bulbs over Bluetooth LE. Everything ships under [custom_components/lexman_ble/](custom_components/lexman_ble/).

The BLE device library lives **vendored** inside the integration at
[custom_components/lexman_ble/lexman_ble/](custom_components/lexman_ble/lexman_ble/) and is imported with a relative import (`from .lexman_ble import ...`). It used to be a separate PyPI package (`lexman-ble`, still the upstream `davidsmfreire/lexman-ble` project); this fork **vendored it** so local library changes ship directly via HACS without a PyPI release. Key consequences:

- There is **no PyPI dependency** on `lexman-ble` anymore. Editing the vendored library takes effect in HA as soon as users update the integration — no publish step.
- The only third-party runtime requirement is `parse` (in `manifest.json` `requirements`). Home Assistant's Bluetooth stack already provides `bleak`, `bleak-retry-connector`, and `bluetooth-data-tools`, so those are **not** redeclared in `requirements`.
- **Only one version number matters now**: `manifest.json` `version`. Bump it by hand when you want HACS to offer users an update. (`pyproject.toml`'s version is vestigial — the repo is no longer built as a package.)

## Tooling

Dependency/dev manager is **`uv`**. The project is configured as a **non-package** dev environment (`[tool.uv] package = false`, no `[build-system]`) — `uv` only resolves the lint/test environment; it does not build a wheel. `pyproject.toml`'s `dependencies` mirror the vendored library's runtime deps so the dev/lint environment can resolve them. Requires Python ≥ 3.13.

Dependency groups: `ha` (Home Assistant, for type-checking against), `dev` (linters). `default-groups = "all"` so `uv sync` installs everything.

> Note: the [Makefile](Makefile) and [CONTRIBUTING.md](CONTRIBUTING.md) still reference `poetry` — that is stale; use `uv`.

## Common commands

```bash
uv sync                             # install all deps (replaces stale `poetry install`)
uv run pre-commit install           # enable git hooks (lint + commit-msg)
uv run pre-commit run --all-files   # run the full lint/format/type-check suite

make dev-container-run               # throwaway HA in Docker with the integration +
                                     # .devcontainer/configuration.yaml mounted on
                                     # http://localhost:9123 (needs host D-Bus for BLE)
make dev-container-rm                # stop & remove that container
```

There is **no test suite** — pytest config and the CI `test` job are commented out, and there is no `tests/` directory. Don't claim tests pass; there are none to run. The vendored library's protocol layer ([lexman_ble/const.py](custom_components/lexman_ble/lexman_ble/const.py)) is pure and hardware-free, so it's the highest-ROI place to add unit tests if you introduce any.

Linting/formatting runs entirely through pre-commit ([.pre-commit-config.yaml](.pre-commit-config.yaml)): `ruff` + `ruff-format`, `mypy`, `bandit`, `codespell`, `prettier`, `pyupgrade`. CI runs `pre-commit`, `hassfest`, and `hacs/action` validation.

## Commits & releases

Commit messages follow **Conventional Commits** (enforced by `commitizen` commit-msg hook and `commitlint` in CI). This is now stylistic only: **the PyPI semantic-release job was removed** (this fork doesn't publish to PyPI). To ship a change to users, merge to `main` and bump `manifest.json` `version`; HACS picks it up from GitHub releases or the default branch.

## Library architecture (vendored: `custom_components/lexman_ble/lexman_ble/`)

The device protocol is the heart of the library and lives in [lexman_ble/const.py](custom_components/lexman_ble/lexman_ble/const.py):

- `CctSmartBulbCommand` is an `Enum` where each member carries a `(set, query, response)` triple of colon-separated hex templates with `{0}`/`{1}` byte placeholders (little-endian, split across bytes).
- `_hex_string_formatting` fills placeholders to build request bytes; `_hex_string_parsing` reverse-parses notification responses back into an int, validating that repeated placeholders agree.
- `CctSmartBulbCommandInstance` is a per-call wrapper (`.set(value)` / `.query` / `.match_response(...)`) that holds the concrete value and produces `request_bytes`.

[lexman_ble/cct_smart_bulb.py](custom_components/lexman_ble/lexman_ble/cct_smart_bulb.py) — `LexmanCCTSmartBulb` is the connection-managing device class, modeled on the `led_ble` / Bluetooth-Devices pattern:

- Uses `bleak` + `bleak_retry_connector` (`establish_connection`, `@retry_bluetooth_connection_error`).
- Lazy connect on command, auto-disconnect after `DISCONNECT_DELAY` (120s) of inactivity; `_connect_lock` and `_operation_lock` serialize access.
- Commands are **fire-and-confirm**: writes go to `WRITE_CHAR_UUID`, and the _actual_ state is updated in `_notification_handler` from notifications on `READ_CHAR_UUID`, then `_fire_callbacks()` notifies subscribers (the HA coordinator). `set_*` methods optimistically update local state too.
- Brightness is 0–254 on the wire but exposed as 0–255 (HA) and set via 0–100 (%). Color temperature maps between device units (153 cool … 454 warm) and Kelvin (6500 cool … 2700 warm) — note the inverted ordering, see `CCT_TEMPERATURE_*` constants.

## Integration architecture (`custom_components/lexman_ble/`)

Standard modern HA BLE config-entry integration. Note two `const.py`/`models.py` pairs exist — one for the integration (`custom_components/lexman_ble/`) and one for the vendored library (`custom_components/lexman_ble/lexman_ble/`); they are distinct modules.

- [config_flow.py](custom_components/lexman_ble/config_flow.py) — Bluetooth discovery flow. Devices are identified by the vendor service UUID `SERVICE_UUID` (see [const.py](custom_components/lexman_ble/const.py)), **not** the generic advertised name. The manifest `bluetooth` matcher pairs `manufacturer_id: 5393` with that custom UUID — do not relax it to `manufacturer_id` alone (sibling Lexman/Adeo BLE products share the manufacturer id but speak a different protocol; the comment on `SERVICE_UUID` explains this).
- [`__init__.py`](custom_components/lexman_ble/__init__.py) — `async_setup_entry` resolves the `BLEDevice` from the address, builds a `LexmanCCTSmartBulb`, wraps it in a `DataUpdateCoordinator` (polls every `UPDATE_SECONDS`=15s), registers a passive BLE advertisement callback to refresh the device handle, and waits for a first notification (`startup_event`) before declaring the entry ready.
- Runtime objects are passed via `entry.runtime_data` typed as `LexmanConfigEntry` ([typing.py](custom_components/lexman_ble/typing.py)) holding `LexmanCCTSmartBulbData` ([models.py](custom_components/lexman_ble/models.py)).
- [light.py](custom_components/lexman_ble/light.py) — the only platform (`Platform.LIGHT`); a `CoordinatorEntity` + `LightEntity` in `COLOR_TEMP` mode. It subscribes to the device's own callback in `async_added_to_hass` for push updates, on top of coordinator polling.
- Config-flow UI strings: [strings.json](custom_components/lexman_ble/strings.json) is the source, but custom integrations are **not** processed by Core's translation build step, so a literal-English [translations/en.json](custom_components/lexman_ble/translations/en.json) (with `[%key:...%]` references resolved) must be shipped and kept in sync.

When extending things: keep the BLE wire protocol in the vendored library (`lexman_ble/`), keep Home Assistant imports out of it, and bump `manifest.json` `version` to release.
