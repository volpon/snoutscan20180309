#!/bin/bash
#This script runs a snoutscan benchmark on the data at $1 using different indicies and prints a
# tsv-like output with the resuling accuracy and time
# set -x

dataDir="$1"

#This is a list of strings that fully define a faiss index:
indexDefinitions=(  "Flat" 
                    "IVF1024,Flat"
                    "IVF2048,Flat"
                    "IVF4096,Flat"
                    "PQ32"
                    "PCA80,Flat"
                    "IVF4096,PQ8+16"
                    "IVF4096,PQ32"
                    "IMI2x8,PQ32"
                    "IMI2x8,PQ8+16"
                    "OPQ16_64,IMI2x8,PQ8+16")

echo -e "indexDefinition\taccuracy\truntimeSec"

for index in ${indexDefinitions[*]}
    do
    timeBeforeSec=$(date +"%s")
    accuracy=$(snoutScan.py -i "$index" "$dataDir" 2>/dev/null | grep 'Proportion of subject' | sed 's/.*: //g')
    timeAfterSec=$(date +"%s")
    
    timeBetweenSec=$( echo "$timeAfterSec - $timeBeforeSec" | bc )
    echo -e "$index\t$accuracy\t$timeBetweenSec"
    
done