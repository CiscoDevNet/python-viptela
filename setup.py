from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

py_files = [
    "ansible/module_utils/viptela",
]
files = [
    "vmanage/cli",
    "vmanage/api",
    "vmanage/apps",
    "vmanage/data",
    "ansible/modules/viptela",
]

setup(
    name="viptela",
    version='0.1.7',
    packages=find_packages(),
    # packages=files,
    py_modules=py_files,
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