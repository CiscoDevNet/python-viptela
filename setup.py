from setuptools import setup

setup(
    name="cisco-sdwan",
    version='0.1',
    py_modules=['vmanage_cli', 'cisco_sdwan'],
    install_requires=[
        'Click',
        'requests',
    ],
    entry_points='''
        [console_scripts]
        vmanage=vmanage_cli.main:vmanage_cli     
    ''',
)