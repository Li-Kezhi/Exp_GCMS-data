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
folderPrefix = "\\20160608_Co_Cube\\Adsorption\\"

FID_CB_LINEAR_A = 3164192   # Area = a + b * ppm
FID_CB_LINEAR_B = 115420
MS_CB_LINEAR_A = 898878
MS_CB_LINEAR_B = 88643
MS_CO2_LINEAR_A = 25214000
MS_CO2_LINEAR_B = 6712.3

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
        Example: folderName = "\\0101001.D"
    Return: (list)
        totalminute (float)
        FID area of chlorobenzene (float)
            Retention time: 6.0 ~ 6.4 min
        MS area of chlorobenzene (float)
            Retention time: 5.2 ~ 5.6 min
        MS area of CO2 (float)
            Retention time: 3.7 ~ 4.1 min
    '''
    # Preparation of file position
    path = os.getcwd()
    path += folderName
    position = path + "\\Report.txt"
    
    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + "\\FID1A.ch")[0]
    totalminute = totalsecond / 60.0
    
    count = 0
    flagCountFID, flagCountMS = 100, 100 # No flagCouint exists
    flagStartFID_CB = False # When True: start to collect data from FID
    flagStartMS_CB, flagStartMS_CO2 = False, False # When True: start to collect data from MS
    flagContinueFID_CB, flagContinueMS_CB, flagContinueMS_CO2 = True, True, True # Omit the unexpected ending

    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Find the MS signal
        if "data.ms" in currentLine:
            flagCountMS = -5
        if flagCountMS == 0:
            flagStartMS_CB, flagStartMS_CO2 = True, True
        if flagStartMS_CB == True or flagStartMS_CO2 == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                MS_time = float(splitting[1])
                if 4.85 < MS_time < 5.15:
                    MS_CB_area = float(splitting[-3])
            except IndexError:     # End the finding
                if flagContinueMS_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueMS_CB = False
                else:
                    flagContinueMS_CB = True
                    flagStartMS_CB = False
                    # If FID_area is not attained
                    try:
                        MS_CB_area
                    except:
                        MS_CB_area = 0.0

            try:
                MS_time = float(splitting[1])
                if 3.7 < MS_time < 4.1:
                    MS_CO2_area = float(splitting[-3])
            except IndexError:     # End the finding
                if flagContinueMS_CO2 == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueMS_CO2 = False
                else:
                    flagContinueMS_CO2 = True
                    flagStartMS_CO2 = False
                    # If FID_area is not attained
                    try:
                        MS_CO2_area
                    except:
                        MS_CO2_area = 0.0

        # Find the FID signal
        if "FID1A.ch" in currentLine:
            flagCountFID = -5
        if flagCountFID == 0:
            flagStartFID_CB = True
        if flagStartFID_CB == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                FID_CB_time = float(splitting[1])
                if 4.95 < FID_CB_time < 5.25:
                    FID_CB_area = float(splitting[-3])
            except IndexError:     # End the finding
                if flagContinueFID_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueFID_CB = False
                else:
                    flagContinueFID_CB = True
                    flagStartFID_CB = False
                    # If FID_area is not attained
                    try:
                        FID_CB_area
                    except:
                        FID_CB_area = 0.0

        flagCountFID += 1
        flagCountMS += 1

        if vars().has_key('FID_CB_area') == False:
            FID_CB_area = 0
        if vars().has_key('MS_CB_area') == False:
            ECD_CB_area = 0
        if vars().has_key('MS_CO2_area') == False:
            ECD_CB_area = 0            
            
    return [totalminute, FID_CB_area, MS_CB_area, MS_CO2_area]


if __name__ == "__main__":
    result = []

    i = 0
    while(True):
        try:
            foldersuffix = "%02d" % (i+1)
            foldersuffix += "010"
            foldersuffix += "%02d" % (i+1)
            foldersuffix += ".D"                 # Example: \\SIG10000001.D
            currentPath = folderPrefix + foldersuffix

            [time, FID_CB_area, MS_CB_area, MS_CO2_area] = obtainArea(currentPath)

            Chlorobenzene_FID_Concentration = (FID_CB_area - FID_CB_LINEAR_A) / FID_CB_LINEAR_B
            Chlorobenzene_MS_Concentration = (MS_CB_area - MS_CB_LINEAR_A) / MS_CB_LINEAR_B
            CO2_MS_Concentration = (MS_CO2_area - MS_CO2_LINEAR_A) / MS_CO2_LINEAR_B

            if i == 0:
                initialTime = time

            result.append([i+1, time - initialTime, FID_CB_area, Chlorobenzene_FID_Concentration, 
                           MS_CB_area, Chlorobenzene_MS_Concentration,
                           MS_CO2_area, CO2_MS_Concentration])

            i += 1
        except IOError:
            print("%d files have been converted!" %i)
            break

    # Save file
    input = open("Result.txt", 'w')
    input.write("Index  Sampling Time (min)  Toluene Area (FID)  Toluene Concentration (ppm)  Toluene Area (MS)  Toluene Concentration (ppm)  CO2 Area  CO2 Concentration (ppm)\n")
    for item in result:
        input.write("%3d   %4d   %8.1f   %8.1f   %8.1f   %8.1f   %8.1f   %8.1f\n" %(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
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
