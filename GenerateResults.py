#!/usr/bin/python
#coding=utf-8

'''
To convert GC data to a summary txt file

Codes needed to be changed:
1. Change the relative folder position (folderPrefix = "...")
2. Change the end of the data (end = 96)
'''  

import os

__author__ = "LI Kezhi" 
__date__ = "$2016-02-18$"
__version__ = "1.2"


# Preparation
folderPrefix = "\\TEST1_FRANCO 2015-12-10 10-50-15\\001F01"
end = 5        # from ****01.D to ****(end).D

FIDAREA_CONCENTRATION_RATIO = 2212.0 / 1000   # Area / ppm = Ratio
TCD_LINEAR_A = -68.721   # Area = a + b * ppm
TCD_LINEAR_B = 0.7814


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

    count = 0
    flagCountFID, flagCountTCD = 100, 100 # No flagCouint exists
    flagStartFID = False # When True: start to collect data from FID
    flagStartTCD = False # When True: start to collect data from TCD

    for line in open(position, 'r'):
        count +=1
        # Cancle the unexpected \x00 in the file
        currentLine = ""
        for letter in line:
            if not letter == '\x00':
                currentLine += letter

        # Record the time
        if "\xdb\x8f7h\xe5e\x1fg" in currentLine:
            splitting = currentLine.split(' ')
            # Cancle empty entries
            new_splitting = []
            for item in splitting:
                if not item == '':
                    new_splitting.append(item)
            splitting = new_splitting
            date = str2date(splitting[2])
            time = str2time(splitting[3])
            totalminute = date[3] * 24 * 60 + time[4]

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

        flagCountFID += 1
        flagCountTCD += 1

    return [totalminute, FID_area, TCD_area]




result = []

for i in range(end):
    foldersuffix = "%02d" % (i+1)
    foldersuffix += ".D"                 # Example: \\WY-LSCO-HAC 2016-01-26 11-25-08\\001F0101.D
    currentPath = folderPrefix + foldersuffix

    [time, FID_area, TCD_area] = obtainArea(currentPath)

    TolueneConcentration = FID_area / FIDAREA_CONCENTRATION_RATIO
    CO2Concentration = (TCD_area - TCD_LINEAR_A) / TCD_LINEAR_B

    if i == 0:
        initialTime = time

    result.append([i+1, time - initialTime, FID_area, TolueneConcentration, TCD_area, CO2Concentration])
    if i > 1 and result[-1][1] < result[-2][1]:
        result[-1][1] += 60 * 12   # Correct the change from 12:59:00 am to 01:00:00 pm

# Save file
input = open("Result.txt", 'w')
input.write("Index     Sampling Time (min)     Toluene Area     Toluene Concentration (ppm)     CO2 Area     CO2 Concentration (ppm)\n")
for item in result:
    input.write("%3d   %4d   %8.1f   %8.1f   %8.1f   %8.1f\n" %(item[0], item[1], item[2], item[3], item[4], item[5]))
input.close()
