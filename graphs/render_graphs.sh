#!/bin/sh

if [ -z $1 ]; then
    echo "Usage: ./render_graphs.sh EXTENSION"
    echo
    echo "Available extensions: svg, png, pdf"
    exit 1
fi

if [ ! -d exports ]; then
    mkdir exports
fi

for FILE in *.mmd; do
    mmdc -i $FILE -o exports/$FILE.$1
done
