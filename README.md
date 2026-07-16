# MAQI

### Menubar Air Quality Index

<img src="assets/appicon Exports/appicon-iOS-Dark-1024x1024@1x.png" alt="MAQI application icon - a stylized maki roll" width="256" height="256" />

A helpful little menu bar app for fetching the current air quality index (AQI) for your ZIP code from [airnow.gov](https://www.airnow.gov).

### Changes:
**v0.1.0** - Initial release


### Environment Variables:
This application expects a `.env` file at the project root. Your `.env` must contain the following keys:
```ini
# Required
AIRNOW_API_KEY = <your API key here>
ZIP_CODE = <your zip code here>
# Optional
REFRESH_INTERVAL_SECONDS = <default is 3600>
```
***You will need to create this file if it does not exist.***


## Dependencies
  - [httpx](https://github.com/encode/httpx)
  - [py2app](https://py2app.readthedocs.io/en/latest/index.html)
  - [rumps](https://github.com/jaredks/rumps?tab=readme-ov-file)
  - [python-dotenv](https://github.com/theskumar/python-dotenv)
