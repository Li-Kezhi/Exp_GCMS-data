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
__date__ = "$2016-07-30$"
__version__ = "1.4"

# Plotting choice
plottingChoice = True

if plottingChoice == True:
    import numpy as np
    import matplotlib.pyplot as plt

# Preparation
folderPrefix = "\\Example\\cb_GC 2016-09-22 21-03-04\\"

FID_CB_LINEAR_A = 0           # Area = a + b * ppm
FID_CB_LINEAR_B = 1
ECD_CB_LINEAR_A = 0
ECD_CB_LINEAR_B = 1

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
            Retention time: 6.0 ~ 6.4 min?
        ECD area of chlorobenzene (float)
            Retention time: 5.2 ~ 5.6 min?
        ECD area of CO2 (float)
            Retention time: 3.7 ~ 4.1 min?
    '''
    # Preparation of file position
    path = os.getcwd()
    path += folderName
    position = path + "\\report.txt"
    testOpenFile = open(position)
    testOpenFile.close()

    # Record the time
    totalsecond = getTime(path + "\\FID1A.ch")[0]
    totalminute = totalsecond / 60.0

    count = 0
    flagCountFID, flagCountECD = 100, 100 # No flagCouint exists
    flagStartFID_CB = False # When True: start to collect data from FID
    flagStartECD_CB = False # When True: start to collect data from ECD
    flagContinueFID_CB, flagContinueECD_CB = True, True # Omit the unexpected ending

    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Find the FID signal
        if "1: FID1 A" in currentLine:
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
                if 2.0 < FID_CB_time < 3.2:
                    FID_CB_area = float(splitting[-4])
            except ValueError:     # End the finding
                if flagContinueFID_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueFID_CB = False
                else:
                    flagContinueFID_CB = True
                    flagStartFID_CB = False
                    # If FID_area is not attained
                    try:
                        ECD_CB_area
                    except:
                        ECD_CB_area = 0.0
            except IndexError:
                if flagContinueFID_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueFID_CB = False
                else:
                    flagContinueFID_CB = True
                    flagStartFID_CB = False
                    # If FID_area is not attained
                    try:
                        ECD_CB_area
                    except:
                        ECD_CB_area = 0.0

        # Find the ECD signal
        if "ECD2 B" in currentLine:
            flagCountECD = -5
        if flagCountECD == 0:
            flagStartECD_CB = True
        if flagStartECD_CB == True:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting

            try:
                ECD_time = float(splitting[1])
                if 1.7 < ECD_time < 1.83:
                    ECD_CB_area = float(splitting[-4])
            except ValueError:     # End the finding
                if flagContinueECD_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueECD_CB = False
                else:
                    flagContinueECD_CB = True
                    flagStartECD_CB = False
                    # If FID_area is not attained
                    try:
                        ECD_CB_area
                    except:
                        ECD_CB_area = 0.0
            except IndexError:
                if flagContinueECD_CB == True:      # Omit the unexpected ending when meeting the space line
                    flagContinueECD_CB = False
                else:
                    flagContinueECD_CB = True
                    flagStartECD_CB = False
                    # If FID_area is not attained
                    try:
                        ECD_CB_area
                    except:
                        ECD_CB_area = 0.0



        flagCountFID += 1
        flagCountECD += 1

        if vars().has_key('FID_CB_area') == False:
            FID_CB_area = 0
        if vars().has_key('ECD_CB_area') == False:
            ECD_CB_area = 0

    return [totalminute, FID_CB_area, ECD_CB_area]

if __name__ == "__main__":
    result = []

    i = 0
    while(True):
        try:
            foldersuffix = "\\SIG100000"
            foldersuffix += "%02d" % (i+1)
            foldersuffix += ".D"                 # Example: \\SIG10000001.D
            currentPath = folderPrefix + foldersuffix

            [time, FID_CB_area, ECD_CB_area] = obtainArea(currentPath)

            Chlorobenzene_FID_Concentration = (FID_CB_area - FID_CB_LINEAR_A) / FID_CB_LINEAR_B
            Chlorobenzene_ECD_Concentration = (ECD_CB_area - ECD_CB_LINEAR_A) / ECD_CB_LINEAR_B

            if i == 0:
                initialTime = time

            result.append([i+1, time - initialTime, FID_CB_area, Chlorobenzene_FID_Concentration, 
                           ECD_CB_area, Chlorobenzene_ECD_Concentration])

            i += 1
        except IOError:
            print("%d files have been converted!" %i)
            break

    # Save file
    input = open("Result.txt", 'w')
    input.write("Index  Sampling Time (min)  CB Area (FID)  CB Concentration (ppm)  CB Area (ECD)  CB Concentration (ppm)\n")
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
        plt.title("ECD - CB")
        plt.show()

        for item in result:
            plt.scatter(item[1], item[7])
        plt.xlabel("Time (min)")
        plt.ylabel("Concentration (ppm)")
        plt.title("ECD - CO2")
        plt.show()
