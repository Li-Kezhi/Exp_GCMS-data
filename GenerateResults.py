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
__version__ = '1.4.6'

# Plotting choice
plottingChoice = True

if plottingChoice is True:
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = '/'

# Parameters
NAME_FID = ('Toluene', 
            'Chlorobenzene'
           )
RETENTION_TIME_FID = {NAME_FID[0]: 1.6,
                      NAME_FID[1]: 5.4
                     }
LINEAR_PAR = {NAME_FID[0]: {'A':0, 'B':1},
              NAME_FID[1]: {'A':0, 'B':1}
             } # Area = a + b * ppm

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

def getConc(area, par_a, par_b):
    '''
    Get concentration from integration area
    Area = a + b * ppm
    return:
        concentration
    '''
    return (area - par_a) / par_b

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
            FID_area = {}
        if flagStartFID is True:
            splitting = currentLine.split(',')

            try:
                FID_time = float(splitting[2])
                for substance in NAME_FID:
                    if -0.05 < FID_time - RETENTION_TIME_FID[substance] < 0.05:
                        FID_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID = False

        if flagCountFID is not None:
            flagCountFID += 1

    result = [totalminute]
    for substance in NAME_FID:
        if not FID_area.has_key(substance):
            FID_area[substance] = 0
        result.append(FID_area[substance])

    return result


if __name__ == '__main__':
    result = []

    i = 0
    while True:
        try:
            foldersuffix = ('%02d'+'010'+'%02d'+'.D')  % ((i+1), (i+1))
            # foldersuffix += '.D'                 # Example: /0801008.D
            currentPath = folderPrefix + foldersuffix

            area = obtainArea(currentPath)
            time = area[0]

            FID_area = {}
            FID_Conc = {}
            for index, substance in enumerate(NAME_FID):
                FID_area[substance] = area[index + 1]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID_Conc[substance] = getConc(FID_area[substance], a, b)

            if i == 0:
                initialTime = time

            outLine = [i+1, time - initialTime]
            for substance in NAME_FID:
                outLine.extend([FID_area[substance], FID_Conc[substance]])
            result.append(outLine)

            i += 1
        except IOError:
            print('%d files have been converted!' %i)
            break

    # Save file
    input = open('Result.txt', 'w')
    titleText = 'Index     Time(min)     '
    for substance in NAME_FID:
        titleText += substance + 'Area-FID     '
        titleText += substance + 'Concentration-FID(ppm)     '
        titleText += '\n'
    input.write(titleText)
    for item in result:
        dataText = ('%+3s   ' % item[0] +
                    '%4d   ' % item[1])
        for index, data in enumerate(item):
            if index > 1:
                dataText += '%+12s   ' % item[index]
        dataText += '\n'
        input.write(dataText)
    input.close()

    # Plotting
    if plottingChoice is True:
        for index, substance in enumerate(NAME_FID):
            for item in result:
                plt.scatter(item[1], item[3 + 2 * index])
            plt.xlabel('Time (min)')
            plt.ylabel('Concentration (ppm)')
            plt.title('FID - ' + substance)
            plt.show()
