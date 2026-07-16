import os
from pathlib import Path

import httpx
import rumps
from dotenv import load_dotenv

load_dotenv()

AIRNOW_API_KEY = os.getenv('AIRNOW_API_KEY', '')
ZIP_CODE = os.getenv('ZIP_CODE', '12345')
ICON_DIR = Path(__file__).resolve().parent / 'assets'

# TODO:
# - add automatic refresh every 30-60 minutes
# - add option to change ZIP code from menu
# - add option to change refresh interval
# - add option to change API key from menu
# - notifications for when AQI exceeds a certain threshold
# - notifications for when AQI is updated
# - async for refreshing AQI data like LTOTD
# - fallback icons for error states / no data
# - build & release


def update_aqi_icon(aqi: int) -> str:
    if aqi <= 50:
        return str(ICON_DIR / 'aqi_1@2x.png')
    if aqi <= 100:
        return str(ICON_DIR / 'aqi_2@2x.png')
    if aqi <= 150:
        return str(ICON_DIR / 'aqi_3@2x.png')
    if aqi <= 200:
        return str(ICON_DIR / 'aqi_4@2x.png')
    if aqi <= 300:
        return str(ICON_DIR / 'aqi_5@2x.png')
    return str(ICON_DIR / 'aqi_6@2x.png')


class AirQualityApp(rumps.App):
    def __init__(self) -> None:
        super().__init__(
            '---',
            icon=str(ICON_DIR / 'appicon Exports/appicon.png'),
            quit_button='Quit',
        )
        self.quality_item = rumps.MenuItem('Quality: ---')
        self.quality_item._menuitem.setEnabled_(False)
        self.menu = [self.quality_item, None, 'Refresh']
        self.get_air_quality()

    @rumps.clicked('Refresh')
    def get_air_quality(self, _=None) -> None:
        try:
            if not AIRNOW_API_KEY:
                rumps.alert(
                    'Missing AIRNOW_API_KEY in .env',
                    message='Add AIRNOW_API_KEY=<your_key> to .env in the project root.',
                )
                self.quality_item.title = 'Quality: Missing key'
                return
            response = httpx.get(
                'https://www.airnowapi.org/aq/observation/current/ziplatlong/',
                params={
                    'format': 'application/json',
                    'zipCode': ZIP_CODE,
                    'API_KEY': AIRNOW_API_KEY,
                },
            )
            response.raise_for_status()
            data = response.json()
            if data:
                aqi = data[0]['nowcastAQI']
                category = data[0]['aqiCategoryName']
                self.icon = update_aqi_icon(aqi)
                self.title = f'{aqi}'
                self.quality_item.title = f'Quality: {category}'
            else:
                rumps.alert(
                    'No air quality data available for this ZIP code.',
                    icon_path=str(
                        ICON_DIR
                        / 'appicon Exports/appicon-iOS-Dark-1024x1024@1x.png'
                    ),
                )
                self.icon = str(ICON_DIR / 'filled@2x.png')  # FIXME
                self.title = '---'
                self.quality_item.title = 'Quality: Unknown'
        except httpx.RequestError as e:
            rumps.alert(
                'An error occurred while fetching air quality data',
                message=str(e),
                icon_path=str(
                    ICON_DIR
                    / 'appicon Exports/appicon-iOS-Dark-1024x1024@1x.png'
                ),
            )
            self.icon = str(ICON_DIR / 'appicon Exports/appicon.png')
            self.title = '---'
            self.quality_item.title = 'Quality: Err'
        except Exception as e:
            rumps.alert(
                'An unexpected error occurred',
                message=str(e),
                icon_path=str(
                    ICON_DIR
                    / 'appicon Exports/appicon-iOS-Dark-1024x1024@1x.png'
                ),
            )
            self.icon = str(ICON_DIR / 'appicon Exports/appicon.png')
            self.title = '---'
            self.quality_item.title = 'Quality: Err'


if __name__ == '__main__':
    AirQualityApp().run()
