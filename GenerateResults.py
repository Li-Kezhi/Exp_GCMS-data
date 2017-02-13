#!/usr/bin/python
#coding=utf-8

'''
To convert GC data to a summary txt file

Codes needed to be changed:
1. Change the relative folder position (folderPrefix = "...")
'''

import os
import time

__author__ = "LI Kezhi" 
__date__ = "$2017-02-13$"
__version__ = "1.4.3"

# Plotting choice
plottingChoice = True

if plottingChoice == True:
    import numpy as np
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = "/NV-F01"

FID_LINEAR_A = 0    # Area = a + b * ppm
FID_LINEAR_B = 1 / 0.1881
FID_CH4_LINEAR_A = 0    # Area = a + b * ppm
FID_CH4_LINEAR_B = 1 / 0.5618


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

def obtainArea(folderName):
    '''
    Return the given folder's FID area data
    
    folderName: Relative folder path (string)
        Example: folderName = "/001F0101.D"
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
    position = path + "/Report.TXT"

    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + "/FID1A.ch")[0]
    totalminute = totalsecond / 60.0
    
    count = 0
    flagCountFID, flagCountFID_CH4 = 100, 100 # No flagCouint exists
    flagStartFID = False # When True: start to collect data from FID
    flagStartFID_CH4 = False # When True: start to collect data from FID_CH4
    flagContinueFID, flagContinueFID_CH4 = True, True # Omit the unexpected ending


    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Find the FID signal
        if "FID1" in currentLine:
            flagCountFID = -5
        if flagCountFID == 0:
            flagStartFID = True
        if flagStartFID == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                FID_time = float(splitting[1])
                if 2.33 < FID_time < 2.43:
                    FID_area = float(splitting[-3])
            except ValueError:     # End the finding
                flagStartFID = False
                # If FID_area is not attained
                try:
                    FID_area
                except:
                    FID_area = 0.0
            except IndexError:     # End the finding
                flagStartFID = False
                # If FID_area is not attained
                try:
                    FID_area
                except:
                    FID_area = 0.0                    

        # Find the FID_CH4 signal
        if "FID2" in currentLine:
            flagCountFID_CH4 = -5
        if flagCountFID_CH4 == 0:
            flagStartFID_CH4 = True
        if flagStartFID_CH4 == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                FID_CH4_time = float(splitting[1])
                if 1.55 < FID_CH4_time < 1.65:
                    FID_CH4_area = float(splitting[-3])
            except ValueError:     # End the finding
                flagStartFID_CH4 = False
                # If FID_area is not attained
                try:
                    FID_CH4_area
                except:
                    FID_CH4_area = 0.0
            except IndexError:     # End the finding
                flagStartFID = False
                # If FID_area is not attained
                try:
                    FID_CH4_area
                except:
                    FID_CH4_area = 0.0
                    
        flagCountFID += 1
        flagCountFID_CH4 += 1
        
        if vars().has_key('FID_area') == False:
            FID_area = 0
        if vars().has_key('FID_CH4_area') == False:
            FID_CH4_area = 0 
            
    return [totalminute, FID_area, FID_CH4_area]


if __name__ == "__main__":
    result = []

    i = 0
    while(True):
        try:
            foldersuffix = "%02d" % (i+1)
            foldersuffix += ".D"                 # Example: /001F0101.D
            currentPath = folderPrefix + foldersuffix
            
            [time, FID_area, FID_CH4_area] = obtainArea(currentPath)

            TolueneConcentration = (FID_area - FID_LINEAR_A) / FID_LINEAR_B
            CO2Concentration = (FID_CH4_area - FID_CH4_LINEAR_A) / FID_CH4_LINEAR_B

            if i == 0:
                initialTime = time

            result.append([i+1, time - initialTime, FID_area, TolueneConcentration, FID_CH4_area, CO2Concentration])

            i += 1
        except IOError:
            print("%d files have been converted!" %i)
            break
        
    # Save file
    input = open("Result.txt", 'w')
    input.write("Index     SamplingTime(min)     TolueneArea     TolueneConcentration(ppm)     CO2Area     CO2Concentration(ppm)\n")
    for item in result:
        input.write("%3d   %4d   %8.1f   %8.1f   %8.1f   %8.1f\n" %(item[0], item[1], item[2], item[3], item[4], item[5]))
    input.close()

    # Plotting
    if plottingChoice == True:
        for item in result:
            plt.scatter(item[1], item[3])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("FID - Toluene")
        plt.show()

        for item in result:
            plt.scatter(item[1], item[5])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("FID_CH4 - CO2")
        plt.show()
