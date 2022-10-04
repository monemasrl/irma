#!/bin/sh

if [ ! -d exports ]; then
    mkdir exports
fi

for FILE in *.mmd; do
    mmdc -i $FILE -o exports/$FILE.svg
done
