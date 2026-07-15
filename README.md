# iOS Developer Mode Enabler Tool for iOS 16

A simple Python utility to enable Developer Mode on connected iOS 16 devices using `pymobiledevice3`, designed for Windows and Linux environments where Xcode is unavailable.

## Supported iOS Versions

- **iOS 16**: **Fully Supported**. The script can programmatically trigger Developer Mode enabling and reboot the device over USB.
- **iOS 15 and lower**: **Not Required**. Developer Mode was introduced in iOS 16. Local developer-signed apps run natively without it.
- **iOS 17 and later**: **Not Supported**. Apple blocked programmatic activation of Developer Mode on iOS 17+. Devices running iOS 17+ must be enabled manually on-device or revealed by sideloading an app using signing utilities (e.g., Sideloadly, AltStore, or 3uTools on Windows).

## Prerequisites

Before running the script, make sure you have the following installed on your machine:

1. **Python 3**: Verify by running `python --version`.
2. **iTunes / Apple Devices Drivers (Windows only)**:
   - For the tool to detect and communicate with your iOS device over USB, you must have Apple's USB drivers installed.
   - You can install these by downloading and installing **iTunes** (via the Microsoft Store or Apple website) or the **Apple Devices** app.
   - Ensure the `Apple Mobile Device Service` is running.
3. **USB Connection**:
   - Connect your iPhone/iPad to your computer via USB.
   - Unlock your device and tap **"Trust This Computer"** (entering your passcode if prompted).

## Installation

Install the required `pymobiledevice3` library using `pip`:

```bash
pip install pymobiledevice3
```

## Usage

1. Open your terminal/command prompt.
2. Navigate to the script's directory.
3. Run the script:

```bash
python iOS_16_Enable_developer_mode.py
```

### How it works:
1. **System Diagnostics**: The script will verify that your Apple USB drivers are active and that `pymobiledevice3` is installed.
2. **Device Discovery**: The script will check for connected iOS devices.
   - If one device is found, it will display its name, model, iOS version, and UDID.
   - If multiple devices are found, it will prompt you to select the correct one.
3. **Confirmation Prompt**: You will be asked if you want to proceed.
4. **Automatic Reboot**: Upon confirmation, the script sends the Developer Mode enable command. **Your iOS device will automatically restart.**
5. Search for "Developer Mode" in **Settings** > **Privacy & Security** > **Developer Mode** and enable it.

## Support the Project

<p align="center">
  <a href="https://github.com/sponsors/NightMean"><img src="https://img.shields.io/badge/Sponsor-ea4aaa?style=for-the-badge&logo=githubsponsors&logoColor=white" /></a>&nbsp;
  <a href="https://www.buymeacoffee.com/nightmean"><img src="https://img.shields.io/badge/Buy_Me_a_Coffee-FFDD00?style=for-the-badge&logo=buymeacoffee&logoColor=black" /></a>&nbsp;
  <a href="https://ko-fi.com/nightmean"><img src="https://img.shields.io/badge/Ko--fi-FF5E5B?style=for-the-badge&logo=kofi&logoColor=white" /></a>
</p>

## Credits

- **[doronz88](https://github.com/doronz88/pymobiledevice3)** — Built the pymobiledevice3 library.

## License

Licensed under the [GPL-3.0 license](LICENSE).