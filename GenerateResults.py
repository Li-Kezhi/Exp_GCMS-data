#!/usr/bin/python
#coding=utf-8

'''
To convert GC data to a summary txt file

Codes needed to be changed:
1. Change the relative folder position (folderPrefix = "...")
'''

from __future__ import print_function
import os
import time

__author__ = "LI Kezhi" 
__date__ = "$2018-04-15$"
__version__ = "1.4.7"

# Plotting choice
plottingChoice = True

if plottingChoice == True:
    import numpy as np
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = "/001F01"

# Parameters
NAME_FID = (
    'Toluene',
    # 'Chlorobenzene-FID'
) # The name SHOULD be ended with '-FID'!
RETENTION_TIME_FID = {
    NAME_FID[0]: 2.385,
    # NAME_FID[1]: 5.3984
}
NAME_FID_CH4 = (
    'CO2',
    # 'Chlorobenzene-FID'
) # The name SHOULD be ended with '-FID'!
RETENTION_TIME_FID_CH4 = {
    NAME_FID_CH4[0]: 1.42,
    # NAME_FID_CH4[1]: 5.3984
}
LINEAR_PAR = {
    NAME_FID[0]: {'A':0, 'B':1 / 0.188},
    # NAME_FID[1]: {'A':0, 'B':1},
    NAME_FID_CH4[0]: {'A':0, 'B':1 / 0.54},
    # NAME_FID_CH4[1]: {'A':0, 'B':1}
} # Area = a + b * ppm


def getTime(filename):
    """
    Get file's modified time and created time
    filename: filename
    return:
        mtime: modified time
        ctiem: created time
    """
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
    position = path + "/Report.TXT"

    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + "/FID1A.ch")[0]
    totalminute = totalsecond / 60.0

    count = 0
    flagCountFID, flagCountFID_CH4 = None, None # When flagCountFID == 0, begin analysing FID data
    flagStartFID, flagStartFID_CH4 = False, False # When True: start to collect data from FID

    FID_area = {}
    FID_CH4_area = {}
    for line in open(position, 'r'):
        count +=1
        currentLine = line.replace('\x00', '').rstrip()
        if 'FID1' in currentLine: # 'FID1'
            flagCountFID = -5
        if flagCountFID == 0:
            flagStartFID = True
            FID_area = {}
        if flagStartFID == True:
            splitting = currentLine.split(' ')
            while '' in splitting:
                splitting.remove('')

            try:
                FID_time = float(splitting[1])
                for substance in NAME_FID:
                    if -0.1 < FID_time - RETENTION_TIME_FID[substance] < 0.1:
                        FID_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID = False

        if flagCountFID is not None:
            flagCountFID += 1

        # Find the FID_CH4 signal
        if "FID2" in currentLine:
            flagCountFID_CH4 = -5
        if flagCountFID_CH4 == 0:
            flagStartFID_CH4 = True
            FID_CH4_area = {}
        if flagStartFID_CH4 == True:
            splitting = currentLine.split(' ')
            while '' in splitting:
                splitting.remove('')

            try:
                FID_CH4_time = float(splitting[1])
                for substance in NAME_FID_CH4:
                    if -0.15 < FID_CH4_time - RETENTION_TIME_FID_CH4[substance] < 0.10:
                        FID_CH4_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID_CH4 = False

        if flagCountFID_CH4 is not None:
            flagCountFID_CH4 += 1

    output = [totalminute]
    result_area = {}
    for substance in NAME_FID_CH4:
        if not FID_CH4_area.has_key(substance):
            FID_CH4_area[substance] = 0
        result_area[substance] = FID_CH4_area[substance]
    for substance in NAME_FID:
        if not FID_area.has_key(substance):
            FID_area[substance] = 0
        result_area[substance] = FID_area[substance]
    output.append(result_area)
    return output


if __name__ == "__main__":
    result = []

    i = 0
    while(True):
        try:
            foldersuffix = "%02d" % (i+1)
            foldersuffix += ".D"                 # Example: /001F0101.D
            currentPath = folderPrefix + foldersuffix

            crawled = obtainArea(currentPath)
            time, area = crawled[0], crawled[1]

            FID_area, FID_CH4_area = {}, {}
            FID_Conc, FID_CH4_Conc = {}, {}
            for substance in NAME_FID_CH4:
                FID_CH4_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID_CH4_Conc[substance] = getConc(FID_CH4_area[substance], a, b)
            for substance in NAME_FID:
                FID_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID_Conc[substance] = getConc(FID_area[substance], a, b)

            if i == 0:
                initialTime = time

            outLine = [i+1, time - initialTime]
            resultName = []
            for substance in NAME_FID_CH4:
                outLine.extend([FID_CH4_area[substance], FID_CH4_Conc[substance]])
                resultName.append(substance)
            for substance in NAME_FID:
                outLine.extend([FID_area[substance], FID_Conc[substance]])
                resultName.append(substance)
            result.append(outLine)

            i += 1
        except IOError:
            print("%d files have been converted!" %i)
            break

    # Save file
    savedFile = open("Result.txt", 'w')
    titleText = 'Index     Time(min)     '
    for substance in NAME_FID_CH4:
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
    if plottingChoice == True:
        allName = NAME_FID_CH4 + NAME_FID
        for substance in allName:
            for item in result:
                x = item[1]
                y = item[resultName.index(substance) * 2 + 3]
                plt.scatter(x, y)
            plt.xlabel('Time (min)')
            plt.ylabel('Concentration (ppm)')
            plt.title(substance)
            plt.show()
