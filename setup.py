from setuptools import setup

APP = ['src/main.py']
VERSION = '0.1.0'
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'src/assets/icons/appicon.png',
    'plist': {
        'CFBundleIdentifier': 'com.jriggles.MAQI',
        'CFBundleShortVersionString': VERSION,
        'LSUIElement': True,  # menu bar app
        'NSHumanReadableCopyright': (
            'Copyright © 2026 John Riggles [sudo_whoami] - MIT License'
        ),
    },
    'packages': ['httpx', 'rumps',],
}

setup(
    app=APP,
    name='MAQI',
    version=VERSION,
    description='Get the current air quality index (AQI) for your ZIP code and display it in the menu bar',
    author='J. Riggles [sudo_whoami]',
    url='https://github.com/JRiggles/MAQI',
    license='MIT',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
