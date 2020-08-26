#!/usr/bin/env sh
path=`dirname $_`
input="${path}/commands.csv"
if [[ $1 == "" ]]; then
    version="19.2.1"
else
    version=$1
fi
while IFS=',' read -r cmdver line
do
    if [[ $version > $cmdver || $version == $cmdver ]]; then
        printf "Running: $line..."
        $line > /dev/null
        if [ $? -eq 0 ]; then
            echo OK
        else
            echo FAIL; exit 1
        fi
    fi
done < "$input"
