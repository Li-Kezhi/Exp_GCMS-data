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
__date__ = '$2017-10-15$'
__version__ = '1.4.6'

# Plotting choice
plottingChoice = True

if plottingChoice is True:
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = '/'

# Parameters
NAME_FID1 = (
    'Toluene-FID1',
    # 'Chlorobenzene-FID1'
) # The name SHOULD be ended with '-FID1'!
RETENTION_TIME_FID1 = {
    NAME_FID1[0]: 2.38,
    # NAME_FID[1]: 5.3984
}
NAME_FID2 = (
    'CO-FID2',
    'CO2-FID2'
) # The name SHOULD be ended with '-FID2'!
RETENTION_TIME_FID2 = {
    NAME_FID2[0]: 0.505,
    NAME_FID2[1]: 1.442
}
LINEAR_PAR = {
    NAME_FID1[0]: {'A':2.281, 'B':1.6003},
    # NAME_FID1[1]: {'A':0, 'B':1},
    NAME_FID2[0]: {'A':0, 'B':1.64},
    NAME_FID2[1]: {'A':-1.3, 'B':0.4526}
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
    Return the given folder's FID area data

    folderName: Relative folder path (string)
        Example: folderName = '/001F0101.D'
    Return: (list)
        totalminute (float)
        FID2/FID area of given substances (dict)
            dict: substance -> integration area
    '''
    # Preparation of file position
    path = os.getcwd()
    path += folderName
    position = path + '/report.txt'

    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + '/FID1A.ch')[0]
    totalminute = totalsecond / 60.0

    count = 0
    flagCountFID1, flagCountFID2 = None, None # When flagCountFID1 == 0, begin analysing FID1 data
    flagStartFID1, flagStartFID2 = False, False # When True: start to collect data from FID1

    for line in open(position, 'r'):
        count += 1
        # currentLine = line.rstrip()
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter
        # print(currentLine)

        # Find the FID2 signal
        if 'FID2' in currentLine:
            flagCountFID2 = -5
        if flagCountFID2 == 0:
            flagStartFID2 = True
            FID2_area = {}
        if flagStartFID2 is True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                FID2_time = float(splitting[1])
                for substance in NAME_FID2:
                    if -0.05 < FID2_time - RETENTION_TIME_FID2[substance] < 0.05:
                        FID2_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID2 = False

        if flagCountFID2 is not None:
            flagCountFID2 += 1

        # Find the FID1 signal
        if 'FID1' in currentLine:
            flagCountFID1 = -5
        if flagCountFID1 == 0:
            flagStartFID1 = True
            FID1_area = {}
        if flagStartFID1 is True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                FID1_time = float(splitting[1])
                for substance in NAME_FID1:
                    if -0.05 < FID1_time - RETENTION_TIME_FID1[substance] < 0.05:
                        FID1_area[substance] = float(splitting[-3])
            except (ValueError, IndexError):     # End the finding
                flagStartFID1 = False

        if flagCountFID1 is not None:
            flagCountFID1 += 1

    output = [totalminute]
    result_area = {}
    for substance in NAME_FID2:
        if not FID2_area.has_key(substance):
            FID2_area[substance] = 0
        result_area[substance] = FID2_area[substance]
    for substance in NAME_FID1:
        if not FID1_area.has_key(substance):
            FID1_area[substance] = 0
        result_area[substance] = FID1_area[substance]
    output.append(result_area)
    return output


if __name__ == '__main__':
    result = []

    i = 0
    while True:
        try:
            foldersuffix = ('001F01'+'%02d'+'.D')  % ((i+1))
            # foldersuffix += '.D'                 # Example: /0801008.D
            currentPath = folderPrefix + foldersuffix

            crawled = obtainArea(currentPath)
            time, area = crawled[0], crawled[1]

            FID1_area, FID2_area = {}, {}
            FID1_Conc, FID2_Conc = {}, {}
            for substance in NAME_FID2:
                FID2_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID2_Conc[substance] = getConc(FID2_area[substance], a, b)
            for substance in NAME_FID1:
                FID1_area[substance] = area[substance]
                a = LINEAR_PAR[substance]['A']
                b = LINEAR_PAR[substance]['B']
                FID1_Conc[substance] = getConc(FID1_area[substance], a, b)

            if i == 0:
                initialTime = time

            outLine = [i+1, time - initialTime]
            resultName = []
            for substance in NAME_FID2:
                outLine.extend([FID2_area[substance], FID2_Conc[substance]])
                resultName.append(substance)
            for substance in NAME_FID1:
                outLine.extend([FID1_area[substance], FID1_Conc[substance]])
                resultName.append(substance)
            result.append(outLine)

            i += 1
        except IOError:
            print('%d files have been converted!' %i)
            break

    # Save file
    savedFile = open('Result.txt', 'w')
    titleText = 'Index     Time(min)     '
    for substance in NAME_FID2:
        titleText += substance + '-Area     '
        titleText += substance + '-Concentration(ppm)     '
    for substance in NAME_FID1:
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
        allName = NAME_FID2 + NAME_FID1
        for substance in allName:
            for item in result:
                x = item[1]
                y = item[resultName.index(substance) * 2 + 2]
                plt.scatter(x, y)
            plt.xlabel('Time (min)')
            plt.ylabel('Concentration (ppm)')
            plt.title(substance)
            plt.show()
