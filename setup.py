import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vmanage",
    version='0.1.5',
    packages=[
        'vmanage',
        'vmanage.command',
        'vmanage.command.show',
        'vmanage.command.import_cmd',
        'vmanage.command.export'
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
        vmanage=vmanage.vmanage_cli:vmanage_cli     
    ''',
)