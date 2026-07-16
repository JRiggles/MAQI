"""
MIT License

Copyright (c) 2024-25 John Riggles [sudo_whoami]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from asyncio import run
from os import getenv
from pathlib import Path

import httpx
import rumps
from dotenv import load_dotenv

load_dotenv()

AIRNOW_API_URL = 'https://www.airnowapi.org/aq/observation/current/ziplatlong/'
AIRNOW_API_KEY = getenv('AIRNOW_API_KEY', '')
ZIP_CODE = getenv('ZIP_CODE', '')
REFRESH_INTERVAL_SECONDS = int(getenv('REFRESH_INTERVAL_SECONDS', '3600'))
ICON_DIR = Path(__file__).resolve().parent / 'assets'

# TODO:
# - add option to change API key, refresh intervale and ZIP code from menu
# - add option to enable/disable notifications
# - notifications for when AQI exceeds a certain threshold
# - notifications for when AQI is updated
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
        self.quality_item = rumps.MenuItem('Quality: ---')
        self.quality_item._menuitem.setEnabled_(False)
        super().__init__(
            'MAQI',
            icon=str(ICON_DIR / 'appicon exports/appicon.png'),
            menu=[self.quality_item, rumps.separator, 'Refresh'],
            quit_button='Quit',
        )
        rumps.Timer(self.refresh, REFRESH_INTERVAL_SECONDS).start()

    @rumps.clicked('Refresh')
    def refresh(self, _sender=None) -> None:
        self.title = '...'
        self.quality_item.title = 'Quality: Refreshing...'
        run(self._refresh_handler())

    async def _refresh_handler(self) -> None:
        try:
            aqi, category = await self.get_air_quality()
            self.icon = str(ICON_DIR / 'appicon exports/appicon.png')
            self.title = '---'
        except ValueError as e:
            rumps.alert('Invalid AQI response', message=str(e))
            self.quality_item.title = 'Quality: Unknown'
        except RuntimeError as e:
            rumps.alert(str(e))
            self.icon = str(ICON_DIR / 'appicon exports/appicon.png')
            self.quality_item.title = 'Missing API key'
        except httpx.HTTPStatusError as e:
            rumps.alert(
                'AirNow request failed',
                message=f'{e.response.status_code}: {e.response.reason_phrase}',
            )
            self.quality_item.title = 'Quality: Err'
        except httpx.RequestError as e:
            rumps.alert('Network error while fetching AQI', message=str(e))
            self.icon = str(ICON_DIR / 'appicon exports/appicon.png')
            self.quality_item.title = 'Quality: Err'
        except Exception as e:
            rumps.alert(
                'Unexpected error while refreshing AQI', message=str(e)
            )
            self.quality_item.title = 'Quality: Err'
        else:
            self.icon = update_aqi_icon(aqi)
            self.title = str(aqi)
            self.quality_item.title = f'Quality: {category}'

    @staticmethod
    async def get_air_quality() -> tuple[int, str]:
        if not AIRNOW_API_KEY:
            raise RuntimeError(
                'Missing AIRNOW_API_KEY in .env. '
                'Add AIRNOW_API_KEY=<your_key> and restart.'
            )

        response = httpx.get(
            AIRNOW_API_URL,
            params={
                'format': 'application/json',
                'zipCode': ZIP_CODE,
                'API_KEY': AIRNOW_API_KEY,
            },
            timeout=15.0,
        )
        response.raise_for_status()

        if not (data := response.json()):
            raise ValueError(
                'No air quality data available for this ZIP code.'
            )

        record = data[0]
        aqi = record.get('nowcastAQI', -1)
        category = record.get('aqiCategoryName')

        if aqi == -1 or category is None:
            raise ValueError('AQI response did not include expected fields.')

        return int(aqi), str(category)


if __name__ == '__main__':
    app = AirQualityApp()
    app.run()
