from setuptools import setup

setup(
    name='kintro',
    version='0.0.1',
    description='Command line tool for looking up PoD cluster information',
    author='bru',
    url=(
        'something'
    ),
    entry_points = {
        'console_scripts': ['kintro = kintro.kintro:cli']
        },
    packages=['kintro'],
    keywords=['kodi', 'plex' 'intro'],
    classifiers=[],
    install_requires=['click', 'click_option_group', 'plexapi']
)
