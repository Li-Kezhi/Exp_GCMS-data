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

__author__ = "LI Kezhi" 
__date__ = "$2018-04-15$"
__version__ = "1.4.7"

# Plotting choice
plottingChoice = True

if plottingChoice is True:
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = '/001'

# Parameters
NAME_FID = (
    'C6H6-FID',
) # The name SHOULD be ended with '-FID'!
RETENTION_TIME_FID = {
    NAME_FID[0]: 3.363,
}
NAME_MS = (
    'Toluene-MS',
    'Chlorobenzene-MS'
) # The name SHOULD be ended with '-MS'!
RETENTION_TIME_MS = {
    NAME_MS[0]: 4.516,
    NAME_MS[1]: 4.865
}
LINEAR_PAR = {
    NAME_FID[0]: {'A':2756138.214, 'B':229347},
    NAME_MS[0]: {'A':0, 'B':1},
    NAME_MS[1]: {'A':0, 'B':1}
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

def getConc(intArea, par_a, par_b):
    '''
    Get concentration from integration area
    Area = a + b * ppm
    return:
        concentration
    '''
    return (intArea - par_a) / par_b

def obtainArea(folderName):
    '''
    Return the given folder's MS and FID area data

    folderName: Relative folder path (string)
        Example: folderName = '/001F0101.D'
    Return: (list)
        totalminute (float)
        MS/FID area of given substances (dict)
            dict: substance -> integration area
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
    flagCountFID, flagCountMS = None, None # When flagCountFID == 0, begin analysing FID data
    flagStartFID, flagStartMS = False, False # When True: start to collect data from FID

    for line in open(position, 'r'):
        count += 1
        currentLine = line.rstrip()

        # Find the MS signal
        if '.ms]' in currentLine:
            flagCountMS = -3
        if flagCountMS == 0:
            flagStartMS = True
            MS_area = {}
        if flagStartMS is True:
            splitting = currentLine.split(',')

            try:
                MS_time = float(splitting[2])
                for substance in NAME_MS:
                    if -0.05 < MS_time - RETENTION_TIME_MS[substance] < 0.05:
                        MS_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartMS = False

        if flagCountMS is not None:
            flagCountMS += 1

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

    output = [totalminute]
    result_area = {}
    for substance in NAME_MS:
        if not MS_area.has_key(substance):
            MS_area[substance] = 0
        result_area[substance] = MS_area[substance]
    for substance in NAME_FID:
        if not FID_area.has_key(substance):
            FID_area[substance] = 0
        result_area[substance] = FID_area[substance]
    output.append(result_area)
    return output


if __name__ == '__main__':
    result = []

    i = 0
    while True:
        try:
            foldersuffix = ('%02d%03d'+'.D')  % ((i+1), (i+1))
            # foldersuffix += '.D'                 # Example: /xxx08008.D
            currentPath = folderPrefix + foldersuffix

            crawled = obtainArea(currentPath)
            time, area = crawled[0], crawled[1]

            FID_area, MS_area = {}, {}
            FID_Conc, MS_Conc = {}, {}
            for substance in NAME_MS:
                MS_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                MS_Conc[substance] = getConc(MS_area[substance], a, b)
            for substance in NAME_FID:
                FID_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID_Conc[substance] = getConc(FID_area[substance], a, b)

            if i == 0:
                initialTime = time

            outLine = [i+1, time - initialTime]
            resultName = []
            for substance in NAME_MS:
                outLine.extend([MS_area[substance], MS_Conc[substance]])
                resultName.append(substance)
            for substance in NAME_FID:
                outLine.extend([FID_area[substance], FID_Conc[substance]])
                resultName.append(substance)
            result.append(outLine)

            i += 1
        except IOError:
            print('%d files have been converted!' %i)
            break

    # Save file
    savedFile = open('Result.txt', 'w')
    titleText = 'Index     Time(min)     '
    for substance in NAME_MS:
        titleText += substance + '-Area     '
        titleText += substance + '-Concentration(ppm)     '
    for substance in NAME_FID:
        titleText += substance + '-Area     '
        titleText += substance + '-Concentration(ppm)     '
    titleText += '\n'
    savedFile.write(titleText)
    for item in result:
        dataText = ('%+3s   ' % item[0] +
                    '%4d   ' % item[1])
        for index, data in enumerate(item):
            if index > 1:
                dataText += '%+12s   ' % item[index]
        dataText += '\n'
        savedFile.write(dataText)
    savedFile.close()

    # Plotting
    if plottingChoice is True:
        allName = NAME_MS + NAME_FID
        for substance in allName:
            for item in result:
                x = item[1]
                y = item[resultName.index(substance) * 2 + 3]
                plt.scatter(x, y)
            plt.xlabel('Time (min)')
            plt.ylabel('Concentration (ppm)')
            plt.title(substance)
            plt.show()
