from os import path
from setuptools import setup, find_namespace_packages

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

includes = [
    "vmanage",
    "vmanage.*",
    "ansible.modules.viptela",
    "ansible.module_utils.viptela",
    "ansible.plugins.httpapi",
]

setup(
    name="viptela",
    version='0.3.9',
    packages=find_namespace_packages(include=includes),
    description="Cisco DevNet SD-WAN vManage (Viptela) CLI/SDK",
    install_requires=['Click', 'requests', 'dictdiffer', 'PyYAML'],
    entry_points='''
        [console_scripts]
        vmanage=vmanage.__main__:vmanage
    ''',
    long_description=long_description,
    long_description_content_type='text/markdown',
)
