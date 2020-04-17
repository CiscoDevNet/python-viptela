from setuptools import setup, find_namespace_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

includes = [
    "vmanage",
    "vmanage.*",
    "ansible.modules.viptela",
    "ansible.module_utils.viptela",
    "ansible.plugins.httpapi",
]

setup(
    name="viptela",
    version='0.2.1.dev1',
    packages=find_namespace_packages(include=includes),
    description="Cisco DevNet Viptela vManage CLI/SDK",
    install_requires=['Click', 'requests', 'dictdiffer', 'PyYAML'],
    entry_points='''
        [console_scripts]
        vmanage=vmanage.__main__:vmanage
    ''',
)
