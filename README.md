# Zepto Scraper — Environment Setup

This project uses Appium and Selenium to scrape the Zepto Android app. Follow these steps on Windows.

1) Create and activate virtual environment (PowerShell):

```powershell
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
```

Or run the helper script:

```powershell
.\setup_env.ps1
```

2) Start Appium server (Appium Desktop or npm global):

```powershell
# if you have Node.js
npm install -g appium
appium
```

3) Ensure Android device is connected and ADB recognizes it:

```powershell
adb devices
```

4) Run the script:

```powershell
python zepto.py
```

Notes:
- Edit `zepto.py` to set your device `udid` and confirm `app_package`/`app_activity`.
- The script saves results to `zepto_veg_fruits.csv` in the working directory.

**Appium Inspector**

- **Purpose:** Describe and inspect app UI, locate element selectors, capture screenshots and record interactions for test automation.
- **Prerequisites:** Appium Server installed (`appium`), Appium Inspector (Appium Desktop or Inspector app), `adb` available, Android device/emulator connected and authorized.
- **How I did this:**
	- Started Appium server locally (default `0.0.0.0:4723`) using `appium`.
	- Launched Appium Inspector and created a new session using the same Desired Capabilities as `zepto.py` (set `udid`, `platformName`, `automationName`, `appPackage`, `appActivity`).
	- Clicked Start Session to connect to the device; the app screen appeared in the Inspector.
	- Used the element tree and highlight tool to find elements and copy reliable selectors (`resource-id`, `accessibility id`).
	- Pasted selectors into `zepto.py` and iterated: re-ran Inspector sessions to confirm selectors worked.
	- Captured screenshots and saved them to the project for reference.
- **Tips:** Prefer `resource-id` or accessibility id over `xpath`. If Inspector shows a blank screen, ensure the app is foregrounded and `adb devices` lists your device.
