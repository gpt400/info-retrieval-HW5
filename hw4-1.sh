#!/bin/bash

inputDirectory="$1"
outputDirectory="$2"

python3 index.py "$inputDirectory" "$outputDirectory"

ls -l $2
wc -l $2/*
