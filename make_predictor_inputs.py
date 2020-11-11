#!/usr/bin/env python

# Script to prepare the files for prediction (including a class label file)
# Vikas Pejaver
# University of Washington
# 2020-04-07

import argparse
import numpy as np
import pandas as pd
import csv

## HELPER FUNCTIONS


## MAIN
if __name__ == '__main__':

    # Constants and defaults
    rrp = 0
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', help='<Input file (patient data linked to labs and tests)>')
    parser.add_argument('-r', '--rrp', help='[Include RRP column: 0 (no) or 1 (yes); defaults to 0]')
    parser.add_argument('-o', '--outfile', help='<Output prefix (will create two files: one for features and one for class labels>')
    
    # Parse arguments
    args = parser.parse_args()

    # Check parameters
    if args.infile:
        infile = args.infile
    if args.rrp:
        rrp = int(args.rrp)
    if args.outfile:
        outfile = args.outfile

    # Set headers
    if rrp == 1:
        headers = ['NEUTROPHIL, ABSOLUTE (AUTO DIFF)', 'LYMPHOCYTE, ABSOLUTE (AUTO DIFF)', 'HEMATOCRIT (HCT)', 'SexDSC', 'LABRESPPCR2_POS']
        commentlines = '# Female coded 0, male coded 1\n# RRP negative coded 0, RRP positive coded 1\n'
    else:
        headers = ['NEUTROPHIL, ABSOLUTE (AUTO DIFF)', 'LYMPHOCYTE, ABSOLUTE (AUTO DIFF)', 'HEMATOCRIT (HCT)', 'SexDSC']
        commentlines = '# Female coded 0, male coded 1\n'
        
    # Extract data from patient file
    df = pd.read_csv(infile, index_col=None, sep=',', quoting=csv.QUOTE_MINIMAL)

    # Keep only those patients to be considered in the final analysis
    df = df[df['Flag'] == 1]

    # Get class labels
    Y = df['ResultNum'].astype(int)

    # Get features
    X = df[['ResultNum_Neutrophils', 'ResultNum_Absolute.Lymphocyte.Count', 'ResultNum_Hematocrit']]
        
    # Encode gender
    X['SexDSC'] = 0
    X['SexDSC'][df['Gender'] == 'Male'] = 1
    X.columns = headers
    
    # Write to output files
    # labels
    labelfile = outfile + '_labels.txt'
    Y.to_csv(labelfile, header=False, index=False, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\t', na_rep='NA')

    # features
    featfile = outfile + '_features.txt'
    try:
        fid = open(featfile, 'w')
    except IOError:
        sys.exit('ERROR: cannot create the output file!')

    fid.write(commentlines)
    fid.close()
    X.to_csv(featfile, header=True, index=False, sep='\t', quoting=csv.QUOTE_NONE, escapechar='\t', na_rep='NA', mode='a')
