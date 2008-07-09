#!/bin/bash

# Add a coding: utf-8 line to all python files specified if it doesn't
# already have one

FILES=`grep -LE "coding: utf[- ]8" $*`

for f in $FILES; do
    echo "Fixing utf8 in file $f"
    sed -i -e '1s/^/# -*- coding: utf-8 -*-\n/' $f
done
    
