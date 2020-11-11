#!/usr/bin/env python

# Script to convert the two separate patient and encounter files into a master file with the most recent SARS-CoV-2 test and the closest blood tests to it
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
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--patientfile', help='<Patient CSV>')
    parser.add_argument('-e', '--encounterfile', help='<Encounter/lab CSV>')
    parser.add_argument('-o', '--outfile', help='<Output CSV>')
    
    # Parse arguments
    args = parser.parse_args()

    # Check parameters
    if args.patientfile:
        pfile = args.patientfile
    if args.encounterfile:
        efile = args.encounterfile
    if args.outfile:
        outfile = args.outfile

    # Extract data from patient file
    pdf = pd.read_csv(pfile, index_col=None, sep=',', quoting=csv.QUOTE_MINIMAL)
    pdf.drop(columns='Unnamed: 0', inplace=True)
    
    # Extract data from encounter file and convert relevant columns to datetime
    edf = pd.read_csv(efile, index_col=None, sep=',', quoting=csv.QUOTE_MINIMAL)
    edf.drop(columns='Unnamed: 0', inplace=True)
    edf['OrderTime'] = pd.to_datetime(edf['OrderTime'])
    edf['SpecimenReceivedTime'] = pd.to_datetime(edf['SpecimenReceivedTime'])
    edf['ResultTime'] = pd.to_datetime(edf['ResultTime'])
    
    # Get encounters with most recent SARS-CoV-2 tests
    sc2test = edf[edf['LabName'] == 'COVID-19 Coronavirus Qual PCR Result']
    #sc2test['sc2OrderTime'] = sc2test.groupby('PersonId')['OrderTime'].transform(max) ### CHANGED TO MATCH STANFORD'S PROTOCOL ###
    sc2test['sc2OrderTime'] = sc2test.groupby('PersonId')['OrderTime'].transform(min)
    outdf = sc2test[sc2test['OrderTime'] == sc2test['sc2OrderTime']]
    outdf.drop(columns='sc2OrderTime', inplace=True)

    # Get non-SARS-CoV-2 test encounters closest to SARS-CoV-2 tests
    labsdf = []
    bloodtest = edf[edf['LabName'] != 'COVID-19 Coronavirus Qual PCR Result']
    testnames = bloodtest['LabName'].unique()
    for t in testnames: # loop by lab test names so that column headers can be changed
        col_suffix = t.replace(' ', '.')
        tmpdf = bloodtest[bloodtest['LabName'] == t]

        # merge by patient ID
        mergedf = pd.merge(tmpdf, outdf, how='left', on='PersonId', indicator=True, suffixes=('_' + col_suffix, '_SCV2'))
        mergedf = mergedf[mergedf['_merge'] == 'both']
        mergedf.drop(columns='_merge', inplace=True)
        
        # get number of hours between SARS-CoV-2 test and blood test
        mergedf['TimeDiff_' + col_suffix] = (mergedf['OrderTime_SCV2'] - mergedf['OrderTime_' + col_suffix]).astype('timedelta64[h]')

        # get encounter closest to SARS-CoV-2 test
        mindf = mergedf.loc[mergedf.groupby('PersonId')['TimeDiff_' + col_suffix].idxmin()]
        mindf.drop(list(mindf.filter(regex='SCV2')), axis = 1, inplace = True)
        
        # add to list of dataframes
        labsdf.append(mindf)

    # Add demographics to outdf
    outdf = pdf.merge(outdf, how='left', on='PersonId')
    
    # Reorder dataframes so that merging starts with the largest dataframe
    for df in labsdf:
        outdf = outdf.merge(df, how='left', on='PersonId')

    # Final clean-up of data types for encounter IDs
    encols = list(outdf.filter(regex=('EncounterId')).columns)
    outdf[encols] = outdf[encols].astype('Int64')
        
    # Write to output file
    outdf.to_csv(outfile, header=True, index=False, sep=',', quoting=csv.QUOTE_NONE, escapechar='\t', na_rep='NA')
