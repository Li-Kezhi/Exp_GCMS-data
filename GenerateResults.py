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
__date__ = "$2016-09.24$"
__version__ = "1.4"

# Plotting choice
plottingChoice = True

if plottingChoice == True:
    import numpy as np
    import matplotlib.pyplot as plt


# Preparation
folderPrefix = "\\TEST1_FRANCO 2015-12-10 10-50-15\\001F01"

FIDAREA_CONCENTRATION_RATIO = 2212.0 / 1000   # Area / ppm = Ratio
TCD_LINEAR_A = -68.721   # Area = a + b * ppm
TCD_LINEAR_B = 0.7814


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
        Example: folderName = "\\001F0101.D"
    Return: (list)
        totalminute (float)
        FID area of toluene (float)
            Retention time: 1.8 ~ 1.9 min
        TCD area of CO2 (float)
            Retention time: 1.7 ~ 1.8 min
    '''
    # Preparation of file position
    path = os.getcwd()
    path += folderName
    position = path + "\\Report.TXT"

    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + "\\FID1A.ch")[0]
    totalminute = totalsecond / 60.0
    
    count = 0
    flagCountFID, flagCountTCD = 100, 100 # No flagCouint exists
    flagStartFID = False # When True: start to collect data from FID
    flagStartTCD = False # When True: start to collect data from TCD
    flagContinueFID, flagContinueTCD = True, True # Omit the unexpected ending


    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Find the FID signal
        if "FID" in currentLine:
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
                if 1.8 < FID_time < 1.9:
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

        # Find the TCD signal
        if "TCD" in currentLine:
            flagCountTCD = -5
        if flagCountTCD == 0:
            flagStartTCD = True
        if flagStartTCD == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                TCD_time = float(splitting[1])
                if 1.7 < FID_time < 1.8:
                    TCD_area = float(splitting[-3])
            except ValueError:     # End the finding
                flagStartTCD = False
                # If FID_area is not attained
                try:
                    TCD_area
                except:
                    TCD_area = 0.0
            except IndexError:     # End the finding
                flagStartFID = False
                # If FID_area is not attained
                try:
                    FID_area
                except:
                    FID_area = 0.0
                    
        flagCountFID += 1
        flagCountTCD += 1
        
        if vars().has_key('FID_area') == False:
            FID_area = 0
        if vars().has_key('TCD_area') == False:
            TCD_area = 0 
            
    return [totalminute, FID_area, TCD_area]


if __main__ == "__main__":

    result = []
    
    i = 0
    while(True):
        try:
            foldersuffix = "%02d" % (i+1)
            foldersuffix += ".D"                 # Example: \\WY-LSCO-HAC 2016-01-26 11-25-08\\001F0101.D
            currentPath = folderPrefix + foldersuffix
            
            [time, FID_area, TCD_area] = obtainArea(currentPath)

            TolueneConcentration = FID_area / FIDAREA_CONCENTRATION_RATIO
            CO2Concentration = (TCD_area - TCD_LINEAR_A) / TCD_LINEAR_B

            if i == 0:
                initialTime = time

            result.append([i+1, time - initialTime, FID_area, TolueneConcentration, TCD_area, CO2Concentration])
    
            i += 1
        except IOError:
            print("%d files have been converted!" %i)
            break
        
    # Save file
    input = open("Result.txt", 'w')
    input.write("Index     Sampling Time (min)     Toluene Area     Toluene Concentration (ppm)     CO2 Area     CO2 Concentration (ppm)\n")
    for item in result:
        input.write("%3d   %4d   %8.1f   %8.1f   %8.1f   %8.1f\n" %(item[0], item[1], item[2], item[3], item[4], item[5]))
    input.close()
    
    # Plotting
    if plottingChoice == True:
        for item in result:
            plt.scatter(item[1], item[3])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("FID - CB")
        plt.show()

        for item in result:
            plt.scatter(item[1], item[5])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("MS - CB")
        plt.show()

        for item in result:
            plt.scatter(item[1], item[7])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("MS - CO2")
        plt.show()
