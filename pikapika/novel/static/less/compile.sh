#!/bin/bash

for f in `ls *.less`; do
    lessc "$f" > "../css/${f%.*}.css"
done;
