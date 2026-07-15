#!/usr/bin/env python3
"""
iOS Developer Mode Enabler
--------------------------
Automates enabling iOS Developer Mode using pymobiledevice3.
"""

import sys
import os
import shutil
import json
import subprocess

# On Windows, we need winreg to query Apple registry keys
if sys.platform == "win32":
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None


def check_itunes_drivers() -> bool:
    """
    Checks if Apple Mobile Device / iTunes drivers are installed on Windows.
    Returns True if found, False otherwise. On non-Windows platforms, returns True.
    """
    if sys.platform != "win32":
        # Native drivers/libusb are used on macOS/Linux
        return True

    # 1. Check if the Apple Mobile Device Service is running/registered
    try:
        # sc.exe is standard on all Windows versions
        result = subprocess.run(
            ["sc.exe", "query", "Apple Mobile Device Service"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and "RUNNING" in result.stdout:
            return True
    except Exception:
        pass

    # 2. Check registry paths for Apple Mobile Device Support or iTunes
    if winreg:
        registry_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Apple Inc.\Apple Mobile Device Support"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Apple Inc.\Apple Mobile Device Support"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Apple Computer, Inc.\iTunes"),
        ]
        for hive, path in registry_paths:
            try:
                with winreg.OpenKey(hive, path, 0, winreg.KEY_READ) as _:
                    return True
            except FileNotFoundError:
                continue

    return False


def check_pymobiledevice3() -> bool:
    """
    Checks if pymobiledevice3 is available on PATH or importable.
    Returns True if available, False otherwise.
    """
    # Check if executable is on PATH
    if shutil.which("pymobiledevice3") is not None:
        return True

    # Check if we can run it via python module
    try:
        import pymobiledevice3
        return True
    except ImportError:
        return False


def run_pymobiledevice_command(args: list) -> subprocess.CompletedProcess:
    """
    Runs a pymobiledevice3 command, trying the global executable first,
    then falling back to running it as a python module.
    """
    # Try global executable first
    try:
        return subprocess.run(
            ["pymobiledevice3"] + args,
            capture_output=True,
            text=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to python module execution
        return subprocess.run(
            [sys.executable, "-m", "pymobiledevice3"] + args,
            capture_output=True,
            text=True,
            check=True
        )


def prompt_user(message: str) -> str:
    """
    Prints a message, explicitly flushes stdout, and reads a line from stdin.
    """
    print(message, end="", flush=True)
    return sys.stdin.readline().strip()


def get_ios_major_version(version_str: str) -> int:
    """
    Parses the major version number from the product version string.
    Returns 0 if it cannot be parsed.
    """
    try:
        parts = version_str.split(".")
        if parts:
            return int(parts[0])
    except Exception:
        pass
    return 0


def list_connected_devices() -> list:
    """
    Queries usbmuxd via pymobiledevice3 to list connected iOS devices.
    Returns a list of device dictionaries.
    """
    try:
        result = run_pymobiledevice_command(["usbmux", "list"])
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error querying usbmuxd: {e.stderr}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"Failed to query connected devices: {e}", file=sys.stderr)
        return []


def main():
    print("==============================================")
    print("   iOS Developer Mode Enabler Tool (iOS 16)   ")
    print("==============================================")
    print()

    # Step 1: Check Windows Drivers
    print("[*] Checking Apple/iTunes USB drivers...")
    if not check_itunes_drivers():
        print("[-] WARNING: Apple Mobile Device Support drivers were not detected.")
        print("    Please ensure iTunes or the 'Apple Devices' app is installed")
        print("    so that iOS devices can be detected over USB.")
        print()
        choice = prompt_user("Do you want to attempt to proceed anyway? (y/N): ").lower()
        if choice != 'y':
            print("[*] Exiting.")
            sys.exit(1)
    else:
        print("[+] Apple/iTunes drivers detected.")

    # Step 2: Check pymobiledevice3 installation
    print("[*] Checking for pymobiledevice3...")
    if not check_pymobiledevice3():
        print("[-] ERROR: pymobiledevice3 was not found on your system.", file=sys.stderr)
        print("    Please install it using your Python package manager:", file=sys.stderr)
        print("    pip install pymobiledevice3", file=sys.stderr)
        print()
        sys.exit(1)
    else:
        print("[+] pymobiledevice3 detected.")

    # Step 3: Discover connected devices
    print("[*] Discovering connected iOS devices...")
    devices = list_connected_devices()

    if not devices:
        print("[-] No iOS devices detected. Please make sure:")
        print("    1. The device is connected via USB.")
        print("    2. The device is unlocked.")
        print("    3. You have tapped 'Trust This Computer' on the device screen.")
        print()
        sys.exit(1)

    # Step 4: Device Selection
    selected_device = None
    if len(devices) == 1:
        selected_device = devices[0]
        print(f"[+] Found device: {selected_device.get('DeviceName', 'iPhone')} ({selected_device.get('DeviceClass', 'Unknown')})")
        print(f"    iOS Version: {selected_device.get('ProductVersion', 'Unknown')}")
        print(f"    UDID:        {selected_device.get('UniqueDeviceID', 'Unknown')}")
        print()
    else:
        print(f"[+] Found {len(devices)} connected devices:")
        for idx, dev in enumerate(devices):
            print(f"  {idx + 1}) {dev.get('DeviceName', 'iPhone')} ({dev.get('DeviceClass', 'Unknown')})")
            print(f"     iOS Version: {dev.get('ProductVersion', 'Unknown')}")
            print(f"     UDID:        {dev.get('UniqueDeviceID', 'Unknown')}")
            print()
        
        while True:
            try:
                choice_str = prompt_user(f"Select a device (1-{len(devices)}) or 'q' to quit: ")
                if choice_str.lower() == 'q':
                    print("[*] Exiting.")
                    sys.exit(0)
                choice_idx = int(choice_str) - 1
                if 0 <= choice_idx < len(devices):
                    selected_device = devices[choice_idx]
                    break
                else:
                    print("Invalid selection. Please choose a number in range.")
            except ValueError:
                print("Invalid input. Please enter a number.")

    udid = selected_device.get("UniqueDeviceID")
    if not udid:
        print("[-] ERROR: Could not retrieve device UDID.", file=sys.stderr)
        sys.exit(1)

    # Step 4.5: iOS Version Verification (Support iOS 16 only)
    version_str = selected_device.get('ProductVersion', '')
    major_version = get_ios_major_version(version_str)

    if major_version >= 17:
        print()
        print("==============================================")
        print("            iOS 17+ NOT SUPPORTED             ")
        print("==============================================")
        print(f"Your device is running iOS {version_str}.")
        print("Apple blocked programmatic Developer Mode enabling on iOS 17+.")
        print()
        print("To enable Developer Mode on iOS 17+:")
        print("  1. Go to Settings > Privacy & Security.")
        print("  2. Scroll to the bottom and check for 'Developer Mode'.")
        print("  3. If it is NOT visible, you must reveal it by attempting")
        print("     to sideload an app (e.g. via Sideloadly or AltStore).")
        print("==============================================")
        sys.exit(1)
    elif major_version < 16:
        print()
        print(f"[*] Note: Your device is running iOS {version_str}.")
        print("    Developer Mode was introduced in iOS 16.")
        print("    For iOS 15 and lower, Developer Mode is not required")
        print("    to run development apps.")
        print("[*] Exiting.")
        sys.exit(0)

    # Step 5: Confirmation and Explanation of Reboot Flow
    print("==============================================")
    print("                  WARNING                     ")
    print("==============================================")
    print("Enabling Developer Mode will AUTOMATICALLY REBOOT your device.")
    print()
    print("After the device boots back up, you MUST:")
    print("  1. Unlock the device.")
    print("  2. Wait a few seconds for the prompt:")
    print("     'Turn On Developer Mode?'")
    print("  3. Tap 'Turn On'.")
    print("  4. Enter your device passcode.")
    print("==============================================")
    print()

    confirm = prompt_user("Do you want to proceed with enabling Developer Mode? (y/N): ").lower()
    if confirm != 'y':
        print("[*] Cancelled. Exiting.")
        sys.exit(0)

    # Step 6: Trigger Enablement
    print(f"[*] Triggering Developer Mode enablement on device {udid}...")
    try:
        cmd_args = ["amfi", "enable-developer-mode", "--udid", udid]
        result = run_pymobiledevice_command(cmd_args)
        combined_output = (result.stdout or "") + (result.stderr or "")
        if "ERROR" in combined_output or "Failed to start service" in combined_output:
            print("[-] ERROR: pymobiledevice3 failed to start the AMFI service.", file=sys.stderr)
            if combined_output:
                print(f"    Details: {combined_output.strip()}", file=sys.stderr)
            sys.exit(1)

        print("[+] SUCCESS: Developer Mode signal sent successfully.")
        print("[*] Your device should be rebooting now.")
        print("[*] Please complete the activation on your device screen after it restarts.")
    except subprocess.CalledProcessError as e:
        print(f"[-] ERROR: Failed to enable Developer Mode.", file=sys.stderr)
        combined = (e.stdout or "") + (e.stderr or "")
        if combined:
            print(f"    Details: {combined.strip()}", file=sys.stderr)
        else:
            print(f"    Command exited with code {e.returncode}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[-] ERROR: An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[*] Interrupted by user. Exiting.")
        sys.exit(0)
