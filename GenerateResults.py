#!/usr/bin/python
#coding=utf-8

'''
To convert GC-MS data to a summary txt file

Codes needed to be changed:
1. Change the relative folder position (folderPrefix = "...")
2. Change the end of the data (end = 96)
'''  

import os

__author__ = "LI Kezhi" 
__date__ = "$2016-04-14$"
__version__ = "1.2"


# Preparation
folderPrefix = "\\20160413_CO2 Standard Curve\\6500 ppm\\"
end = 10        # from ****01.D to ****(end).D

FID_CB_LINEAR_A = 3164192   # Area = a + b * ppm
FID_CB_LINEAR_B = 115420
MS_CB_LINEAR_A = 898878
MS_CB_LINEAR_B = 88643
MS_CO2_LINEAR_A = 25214000
MS_CO2_LINEAR_B = 6712.3

def str2date(strDate):
    '''
    Convert string date to int

    strDate: (str)
        Example: 2016-02-18
    Return: (list: int)[year, month, day, totalDay]
        totalDay = 1 when it is 2016-01-01
    '''

    splitting = strDate.split('-')
    year = int(splitting[0])
    month = int(splitting[1])
    day = int(splitting[2])

    totalDay = day                # totalDay = 1 when it is 2016-01-01

    # Leap Year
    def leapYear(year):
        LeapYear = False
        if year % 4 == 0:
            LeapYear = True
            if year % 100 == 0:
                LeapYear = False
                if year % 400 == 0:
                    LeapYear = True
        return LeapYear

    LeapYear = leapYear(year)

    # Year
    for countYear in range(2016, year):
        if leapYear(countYear) == True:
            totalDay += 366
        else:
            totalDay += 365 

    # Month
    if month > 1:
        totalDay += 31
    if month > 2:
        if LeapYear == True:
            totalDay += 29
        else:
            totalDay += 28
    if month > 3:
        totalDay += 31
    if month > 4:
        totalDay += 30
    if month > 5:
        totalDay += 31
    if month > 6:
        totalDay += 30
    if month > 7:
        totalDay += 31
    if month > 8:
        totalDay += 31
    if month > 9:
        totalDay += 30
    if month > 10:
        totalDay += 31
    if month > 11:
        totalDay += 30
    
    return [year, month, day, totalDay]

def str2time(strTime):
    '''
    Convert string time to data

    strTime: (str)
        Example: 21:43:05
    Return: (list)[hour, minute, second, totalhour, totalminute, totalsecond]
        totalsecond = 0 when 00:00:00
    '''
    splitting = strTime.split(':')
    hour = int(splitting[0])
    minute = int(splitting[1])
    second = int(splitting[2])
    totalsecond = 3600 * hour + 60 * minute + second
    totalminute = totalsecond / 60.0
    totalhour = totalminute / 60.0
    return [hour, minute, second, totalhour, totalminute, totalsecond]

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
    position = path + "\\rteres.txt"

    count = 0
    flagCountFID, flagCountMS = 100, 100 # No flagCouint exists
    flagStartFID_CB = False # When True: start to collect data from FID
    flagStartMS_CB, flagStartMS_CO2 = False, False # When True: start to collect data from MS

    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Record the time
        if "\xb2\xc9\xbc\xaf" in currentLine:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting
            #date = str2date(splitting[2])                       # Currently unresolved
            date = str2date("2016-01-01")
            time = str2time(splitting[5] + ":00")
            totalminute = date[3] * 24 * 60 + time[4]

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
                if 5.2 < MS_time < 5.6:
                    MS_CB_area = float(splitting[-3])
            except IndexError:     # End the finding
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
                flagStartMS_CO2 = False
                # If FID_area is not attained
                try:
                    MS_CO2_area
                except:
                    MS_CO2_area = 0.0

        # Find the FID signal
        if "FID2A.ch" in currentLine:
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
                if 6.0 < FID_CB_time < 6.4:
                    FID_CB_area = float(splitting[-3])
            except IndexError:     # End the finding
                flagStartFID_CB = False
                # If FID_area is not attained
                try:
                    FID_CB_area
                except:
                    FID_CB_area = 0.0



        flagCountFID += 1
        flagCountMS += 1

    return [totalminute, FID_CB_area, MS_CB_area, MS_CO2_area]




result = []

for i in range(end):
    foldersuffix = "%02d" % (i+1)
    foldersuffix += "010"
    foldersuffix += "%02d" % (i+1)
    foldersuffix += ".D"                 # Example: \\20160413_blank\\0101001.D
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
    if i > 1 and result[-1][1] < result[-2][1]:
        result[-1][1] += 60 * 12   # Correct the change from 12:59:00 am to 01:00:00 pm

# Save file
input = open("Result.txt", 'w')
input.write("Index  Sampling Time (min)  Toluene Area (FID)  Toluene Concentration (ppm)  Toluene Area (MS)  Toluene Concentration (ppm)  CO2 Area  CO2 Concentration (ppm)\n")
for item in result:
    input.write("%3d   %4d   %8.1f   %8.1f   %8.1f   %8.1f   %8.1f   %8.1f\n" %(item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))
input.close()
