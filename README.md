# LexmanBLE

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![pre-commit][pre-commit-shield]][pre-commit]
[![hacs][hacsbadge]][hacs]
[![Project Maintenance][maintenance-shield]][user_profile]

Home Assistant custom integration for controlling [Lexman (Leroy Merlin brand) CCT smart bulbs](https://www.leroymerlin.fr/produits/decoration-eclairage/ampoule-et-led/ampoule-led/ampoule-e27/ampoule-led-connectee-e27-806lm-60w-variations-blanc-couleurs-lexman-enki-84372272.html) over Bluetooth.

The integration is **self-contained**: the BLE device library is vendored under
[`custom_components/lexman_ble/lexman_ble/`](custom_components/lexman_ble/lexman_ble/),
so there is nothing to install from PyPI.

**The custom component sets up the following platforms.**

| Platform | Description          |
| -------- | -------------------- |
| `light`  | Control a smart bulb |

![logo][lexmanimg]

## Installation

### HACS (recommended)

1. In Home Assistant, open **HACS → ⋮ (top right) → Custom repositories**.
2. Add the repository URL `https://github.com/tiagoagueda/lexman-ble` with type **Integration**.
3. Search for **LexmanBLE**, download it, and restart Home Assistant.
4. The bulbs are discovered automatically over Bluetooth. To add one manually, go to
   **Settings → Devices & Services → + Add Integration → LexmanBLE**.

### Manual

1. Open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory there, create it.
3. Copy the `custom_components/lexman_ble/` directory from this repository (including the
   nested `lexman_ble/` library folder) into your `custom_components` directory.
4. Restart Home Assistant.
5. Add the integration via **Settings → Devices & Services → + Add Integration → LexmanBLE**.

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md).

## Credits

This is a fork of [@davidsmfreire](https://github.com/davidsmfreire)'s [lexman-ble](https://github.com/davidsmfreire/lexman-ble) project, with the BLE library vendored into the integration. Consider supporting the original author: [![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

The original project was generated from [@oncleben31](https://github.com/oncleben31)'s [Home Assistant Custom Component Cookiecutter](https://github.com/oncleben31/cookiecutter-homeassistant-custom-component) template, with code template mainly taken from [@Ludeeus](https://github.com/ludeeus)'s [integration_blueprint][integration_blueprint] template.

The lexman_ble library implementation was inspired by [@Bluetooth-Devices](https://github.com/Bluetooth-Devices)'s [led_ble](https://github.com/Bluetooth-Devices/led-ble) project.

---

[integration_blueprint]: https://github.com/custom-components/integration_blueprint
[buymecoffee]: https://www.buymeacoffee.com/davidsmfreire
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/tiagoagueda/lexman-ble.svg?style=for-the-badge
[commits]: https://github.com/tiagoagueda/lexman-ble/commits/main
[hacs]: https://hacs.xyz
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[lexmanimg]: images/logo.png
[license-shield]: https://img.shields.io/github/license/tiagoagueda/lexman-ble.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40tiagoagueda-blue.svg?style=for-the-badge
[pre-commit]: https://github.com/pre-commit/pre-commit
[pre-commit-shield]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/tiagoagueda/lexman-ble.svg?style=for-the-badge
[releases]: https://github.com/tiagoagueda/lexman-ble/releases
[user_profile]: https://github.com/tiagoagueda
