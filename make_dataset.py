#!/usr/bin/env python

# Script to prepare the master dataset for analysis and prediction (checks for missing data, filters out cases where tests are too far apart in time from the SARS-CoV-2 test)
# Vikas Pejaver
# University of Washington
# 2020-04-04

import argparse
import numpy as np
import pandas as pd
import csv

## HELPER FUNCTIONS


## MAIN
if __name__ == '__main__':

    # Constants and defaults
    thr = 4
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='<Input file (patient data linked to labs and tests)>')
    parser.add_argument('-t', '--threshold', help='[Other tests should have occurred within +/- t hours of the SARS-CoV-2 test; defaults to 4]>')
    parser.add_argument('-o', '--outfile', help='<Output file>')
    
    # Parse arguments
    args = parser.parse_args()

    # Check parameters
    if args.infile:
        infile = args.infile
    if args.threshold:
        thr = int(args.threshold)
    if args.outfile:
        outfile = args.outfile

    # Extract data from patient file
    df = pd.read_csv(infile, index_col=None, sep=',', quoting=csv.QUOTE_MINIMAL)
    df['Flag'] = 0

    # Flag -1 if any of the tests' order times is NA
    df['Flag'][(df['OrderTime_Neutrophils'].isna()) | (df['OrderTime_Absolute.Lymphocyte.Count'].isna()) | (df['OrderTime_Hematocrit'].isna())] = -1

    # Flag -2 if any of the tests' results are NA
    df['Flag'][(df['ResultNum_Neutrophils'].isna()) | (df['ResultNum_Absolute.Lymphocyte.Count'].isna()) | (df['ResultNum_Hematocrit'].isna())] = -2

    # Flag -3 if gender is NA
    df['Flag'][df['Gender'].isna()] = -3 

    # Flag -4 if SARS-CoV-2 order time is NA
    df['Flag'][(df['OrderTime'].isna())] = -4

    # Flag -5 if SARS-CoV-2 result is NA
    df['Flag'][(df['ResultNum'].isna())] = -5
    
    # Flag 1 if patients satisfy time constraints and are not already excluded (above)
    df['Flag'][(df['TimeDiff_Neutrophils'].abs() < thr) & (df['TimeDiff_Absolute.Lymphocyte.Count'].abs() < thr) & (df['TimeDiff_Hematocrit'].abs() < thr) & (df['Flag'] >= 0)] = 1

    # Write to output file
    df.to_csv(outfile, header=True, index=False, sep=',', quoting=csv.QUOTE_NONE, escapechar='\t', na_rep='NA')
