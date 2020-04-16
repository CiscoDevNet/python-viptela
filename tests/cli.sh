#!/bin/sh
path=`dirname $_`
input="${path}/commands.txt"
while IFS= read -r line
do
    printf "Running: $line..."
    $line > /dev/null
    if [ $? -eq 0 ]; then
        echo OK
    else
        echo FAIL
fi
done < "$input"

# printf "Running vmanage show device status..."
# vmanage show device status > /dev/null

