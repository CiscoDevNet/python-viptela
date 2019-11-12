import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="viptela",
    version='0.1.6',
    packages=[
        'vmanage',
        'vmanage.cli',
        'vmanage.cli.show',
        'vmanage.cli.import_cmd',
        'vmanage.cli.export'
        ],
    description="Cisco DevNet Viptela vManage CLI/SDK",
    install_requires=[
        'Click',
        'requests',
        'dictdiffer',
        'PyYAML'
    ],
    entry_points='''
        [console_scripts]
        vmanage=vmanage.cli.vmanage:main     
    ''',
)