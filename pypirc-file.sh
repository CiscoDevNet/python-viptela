#!/bin/sh

FILE="./.pypirc"

cat >$FILE <<EOL
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username: $PYPI_USERNAME
password: $PYPI_PASSWORD

[testpypi]
repository = https://test.pypi.org/legacy/
username: $PYPI_USERNAME
password: $PYPI_PASSWORD
EOL