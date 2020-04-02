from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

includes = [
    "vmanage.*",
    "ansible.modules.*",
    "ansible.module_utils.*",
]

setup(
    name="viptela",
    version='0.1.7',
    packages=find_namespace_packages(include=includes),
    description="Cisco DevNet Viptela vManage CLI/SDK",
    install_requires=[
        'Click',
        'requests',
        'dictdiffer',
        'PyYAML'
    ],
    entry_points='''
        [console_scripts]
        vmanage=vmanage.__main__:main     
    ''',
)
