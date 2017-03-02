#!/usr/bin/env python
#coding=utf-8

'''
To convert GC data to a summary txt file

Codes needed to be changed:
1. Change the relative folder position (folderPrefix = '...')
'''

from __future__ import print_function
import os
import time

__author__ = 'LI Kezhi'
__date__ = '$2017-03-02$'
__version__ = '1.4.5'

# Plotting choice
plottingChoice = True

if plottingChoice is True:
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = '/'

FID_LINEAR_A = 0    # Area = a + b * ppm
FID_LINEAR_B = 1
FID_CH4_LINEAR_A = 0    # Area = a + b * ppm
FID_CH4_LINEAR_B = 1


def getTime(filename):
    '''
    Get file's modified time and created time
    filename: filename
    return:
        mtime: modified time
        ctiem: created time
    '''
    f = filename
    m_time = os.stat(f).st_mtime
    c_time = os.stat(f).st_ctime
    return (m_time, c_time)

def obtainArea(folderName):
    '''
    Return the given folder's FID area data

    folderName: Relative folder path (string)
        Example: folderName = '/001F0101.D'
    Return: (list)
        totalminute (float)
        FID area of toluene (float)
            Retention time: t1 ~ t2 min
        FID area of CO2 (float)
            Retention time: t3 ~ t4 min
    '''
    # Preparation of file position
    path = os.getcwd()
    path += folderName
    position = path + '/RESULTS.CSV'

    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + '/FID1A.ch')[0]
    totalminute = totalsecond / 60.0

    count = 0
    flagCountFID = None # When flagCountFID == 0, begin analysing FID data
    flagStartFID = False # When True: start to collect data from FID

    for line in open(position, 'r'):
        count += 1
        currentLine = line.rstrip()

        # Find the FID signal
        if '.ch]' in currentLine and 'FID' in currentLine:
            flagCountFID = -3
        if flagCountFID == 0:
            flagStartFID = True
        if flagStartFID is True:
            splitting = currentLine.split(',')

            try:
                FID_time = float(splitting[2])
                if 1.55 < FID_time < 1.65:
                    FID_TL_area = float(splitting[-3])
                if 5.35 < FID_time < 5.45:
                    FID_CB_area = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID = False

        if flagCountFID is not None:
            flagCountFID += 1

        if not vars().has_key('FID_TL_area'):
            FID_TL_area = 0
        if not vars().has_key('FID_CB_area'):
            FID_CB_area = 0

    return [totalminute, FID_TL_area, FID_CB_area]


if __name__ == '__main__':
    result = []

    i = 0
    while True:
        try:
            foldersuffix = ('%02d'+'010'+'%02d'+'.D')  % ((i+1), (i+1))
            # foldersuffix += '.D'                 # Example: /0801008.D
            currentPath = folderPrefix + foldersuffix

            time, FID_TL_area, FID_CB_area = obtainArea(currentPath)

            TolueneConcentration = (FID_TL_area - FID_LINEAR_A) / FID_LINEAR_B
            CO2Concentration = (FID_CB_area - FID_CH4_LINEAR_A) / FID_CH4_LINEAR_B

            if i == 0:
                initialTime = time

            result.append([i+1,
                           time - initialTime,
                           FID_TL_area,
                           TolueneConcentration,
                           FID_CB_area,
                           CO2Concentration])

            i += 1
        except IOError:
            print('%d files have been converted!' %i)
            break

    # Save file
    input = open('Result.txt', 'w')
    titleText = ''
    titleText += ('Index     '
                  'Time(min)     '
                  'TolueneArea-FID     '
                  'TolueneConcentration-FID(ppm)     '
                  'ChlorobenzeneArea-FID     '
                  'ChlorobenzeneConcentration-FID(ppm)\n')
    input.write(titleText)
    for item in result:
        dataText = ('%+3s   ' % item[0] +
                    '%4d   ' % item[1] +
                    '%+12s   ' % item[2] +
                    '%+12s   ' % item[3] +
                    '%+12s   ' % item[4] +
                    '%+12s\n' % item[5])
        input.write(dataText)
    input.close()

    # Plotting
    if plottingChoice is True:
        for item in result:
            plt.scatter(item[1], item[3])
        plt.xlabel('Time (min)')
        plt.ylabel('Concentration (ppm)')
        plt.title('FID - Toluene')
        plt.show()

        for item in result:
            plt.scatter(item[1], item[5])
        plt.xlabel('Time (min)')
        plt.ylabel('Concentration (ppm)')
        plt.title('FID - Chlorobenzene')
        plt.show()
