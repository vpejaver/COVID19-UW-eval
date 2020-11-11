#!/usr/bin/env python

# Script to parse the master dataset (or linked tests) file to count number of patients with time constraints fulfilled
# Vikas Pejaver
# University of Washington
# 2020-04-06

import argparse
import numpy as np
import pandas as pd
import csv

## HELPER FUNCTIONS


## MAIN
if __name__ == '__main__':

    # Constants and defaults
    intervals = [0, 4, 8, 12, 16, 20, 24]
    int_name = ['0', '(0, 4]', '(4, 8]', '(8, 12]', '(12, 16]', '(16, 20]', '(20, 24]', '>24']
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='<Input file (patient data linked to labs and tests)>')
    parser.add_argument('-o', '--outfile', help='<Output file>')
    
    # Parse arguments
    args = parser.parse_args()

    # Check parameters
    if args.infile:
        infile = args.infile
    if args.outfile:
        outfile = args.outfile

    # Extract data from patient file
    df = pd.read_csv(infile, index_col=None, sep=',', quoting=csv.QUOTE_MINIMAL)

    # Keep only those patients for whom all information is available
    df = df[(df['ResultNum_Neutrophils'].notna()) & (df['ResultNum_Absolute.Lymphocyte.Count'].notna()) & (df['ResultNum_Hematocrit'].notna()) & (df['ResultNum'].notna()) & (df['Gender'].notna())]
    denom = len(df)
    
    # Loop through each interval and return get fractions
    for i in range(len(intervals)+1):
        tmpdf = df[['TimeDiff_Neutrophils', 'TimeDiff_Absolute.Lymphocyte.Count', 'TimeDiff_Hematocrit']].abs()
        if i == 0:
            start = intervals[i]
            countdf = tmpdf.eq(start).sum().to_frame().T
        elif i == len(intervals):
            finish = intervals[i-1]
            countdf = countdf.append(tmpdf.gt(finish).sum().to_frame().T)
        else:
            start = intervals[i-1]
            finish = intervals[i]
            countdf = countdf.append(tmpdf.le(finish).sum().to_frame().T - tmpdf.le(start).sum().to_frame().T)
            
    countdf = countdf / denom
    countdf['Intervals'] = int_name
    countdf = countdf.set_index('Intervals')
    print(countdf)
    
    # Flag 1 if patients satisfy time constraints and are not already excluded (above)
    #df[(df['TimeDiff_Neutrophils'].abs() < thr) & (df['TimeDiff_Absolute.Lymphocyte.Count'].abs() < thr) & (df['TimeDiff_Hematocrit'].abs() < thr)]

    # Write to output file
    #df.to_csv(outfile, header=True, index=False, sep=',', quoting=csv.QUOTE_NONE, escapechar='\t', na_rep='NA')
