#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 09:29:08 2019

@author: Pablo Carbonell, SYNBIOCHEM
@description: Get plate from primer list.
"""
import argparse
import pandas as pd
import csv
import os
import re

def readPlate(df):
    well = {}
    wp = 'Well Position'
    sn = 'Sequence Name'
    sn2 = 'Name'
    sequence = 'Sequence'
    try:
        assert wp in df.columns and (sn in df.columns or sn2 in df.columns) and sequence in df.columns
    except:
        raise Exception('Unknown columns')
    for ix in df.index:
        pos = df.loc[ix,wp]
        try:
            seq = df.loc[ix,sn]
        except:
            seq = df.loc[ix,sn2]
        part = seq.split('_')[0]
        well[ pos ] = part
    return well

def rowCol( pos ):
    row = re.search('^(\D+)', pos).group()
    col = int( re.search('(\d+)$', pos).group() )
    return (row,col)

def sortWell( pos, byRow=True ):
    if byRow:
        return tuple( reversed( rowCol(pos) ) )
    else:
        return rowCol(pos) 

def nextPos( pos ):
    row, col = rowCol( pos )
    if ord(row) < ord('H'):
        npos = chr( ord(row)+1 ) + str(col)
    else:
        npos = 'A' + str(col+1)
    return npos

def makePlate(wells):
    """ Take the first plate as it is and continue moving in the plate from there """
    plate = {}
    iplate = {}
    firstWell = True
    done = set()
    for well in wells:
        for pos in sorted( well,key = lambda x: sortWell(x) ):
            part = well[pos]
            if part not in done:
                done.add( part )
            else:
                continue
            if not firstWell:
                npos = nextPos( last )
            else:
                npos = pos
            plate[npos] = well[pos]
            iplate[ well[pos] ] = npos
            last = npos
        if firstWell:
            last = sorted(well,key=lambda x: sortWell(x) )[-1]
            firstWell = False
    return plate, iplate
        

def arguments():
    parser = argparse.ArgumentParser(description='Read list of primers and outputs merged list. Pablo Carbonell, SYNBIOCHEM, 2019')
    parser.add_argument('-i', '--input', action='append', 
                        help='Input csv file.')
    parser.add_argument('-o', '--output', 
                        help='Output csv file.')
    return parser

if __name__ == '__main__':
    parser = arguments()
    args = parser.parse_args()
    wells = []
    for infile in args.input:
        if os.path.exists(infile):
            try:
                df = pd.read_csv(infile)
            except:
                raise Exception('Unkown file format!')
            wells.append ( readPlate(df) )
        else:
            raise Exception('File not found')
    plate, iplate = makePlate( wells )
    iwell = {}
    w = set()
    with open(args.output, 'w') as h:
        cw = csv.writer(h)
        head = True
        for infile in args.input:
            cv = csv.reader(open(infile))
            header = next(cv)
            if head:
                cw.writerow( header )
                head = False
            for row in cv:
                rid = row[1].split('_')[0]
                if row[1] not in w:
                    row[0] = iplate[ rid ]
                    cw.writerow( row )
                w.add( row[1] )
        
