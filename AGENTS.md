# AGENTS.md

## Project

A Python utility for enabling Developer Mode on connected iOS 16 devices via USB using `pymobiledevice3`, designed for Windows and Linux environments without Xcode.

Key file:
- `iOS_16_Enable_developer_mode.py` — device detection, lockdownd pairing verification, developer mode trigger, and post-activation reboot sequencing.

## Commands

- Run enabler: `python iOS_16_Enable_developer_mode.py`
- Install dependencies: `pip install pymobiledevice3`

## Invariants & Design Principles

- **iOS version support:**
  - **iOS 16:** Fully supported via programmatic lockdownd activation.
  - **iOS 15 and lower:** Not required (Developer Mode was introduced in iOS 16).
  - **iOS 17 and later:** Not supported (Apple blocked programmatic lockdownd activation on iOS 17+; requires manual on-device toggling or sideloading via developer provisioning).
- **USB pairing prerequisite:** The target device must be connected via USB, unlocked, and have trusted the computer before running the script.

## Repository policy

- Public repository (`NightMean/iOS-Enable-Developer-Mode-iOS-16`).
