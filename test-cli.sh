#!/usr/bin/env bash
input="./tests/commands.csv"

function version_gt() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }

if [[ $1 == "" ]]; then
    version="19.2.1"
else
    version=$1
fi

while IFS=',' read -r cmdver line
do
    if version_gt $version $cmdver || [[ $version == $cmdver ]]; then
        printf "Running: $line..."
        $line > /dev/null
        if [ $? -eq 0 ]; then
            echo OK
        else
            echo FAIL; exit 1
        fi
    fi
done < "$input"
