#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Purpose:
    Write a solution in an text file, such that the validator can read it

Date:
    2019/1/10

"""
###########################################################
### imports
import pandas as pd
import numpy as np
import numpy.random as rnd
import scipy.stats as stats
import timeit as ti
import matplotlib.pyplot as plt
from networkx import nx
###########################################################
###
def writeSolutionFile(name,testInstance,TRUCK_DISTANCE,NUMBER_OF_TRUCK_DAYS,NUMBER_OF_TRUCKS_USED,TECHNICIAN_DISTANCE,NUMBER_OF_TECHNICIAN_DAYS,
                      NUMBER_OF_TECHNICIANS_USED,IDLE_MACHINE_COSTS,TOTAL_COST,Days,scheduleDelivery,scheduleTechnicians):
    
    """
        Purpose
            write a solution txt file to the workingdirectory for the given solution
        Input
            name, name of the solution file that will be writen
            testInstance, name of file of test instance
            TRUCK_DISTANCE, total truck distance for solution
            NUMBER_OF_TRUCK_DAYS, total number of truckdays for solution
            NUMBER_OF_TRUCKS_USED, total number of trucks used for solution
            TECHNICIAN_DISTANCE, total technician distance for solution
            NUMBER_OF_TECHNICIAN_DAYS, total number of technician days for solution
            NUMBER_OF_TECHNICIANS_USED, total number of technicians used for solution
            IDLE_MACHINE_COSTS, total idle machine costs for solution
            TOTAL_COST, total cost of solution
            Days, list with the day number, the number of trucks on that day and the number of technicians on that day
            scheduleDelivery, schedule with the trucks tours for each day and each truck
            scheduleTechnicians, schedule with technicians tours for each day
        Output
            solution file in working directory
    """
    file= open(name +".txt", 'w')
    file.write('DATASET = VeRoLog solver challenge 2019\n')
    file.write('NAME = ' + testInstance + '\n')
    file.write('TRUCK_DISTANCE = '+ str(TRUCK_DISTANCE) +'\n')
    file.write('NUMBER_OF_TRUCK_DAYS = '+ str(NUMBER_OF_TRUCK_DAYS) +'\n')
    file.write('NUMBER_OF_TRUCKS_USED = '+ str(NUMBER_OF_TRUCKS_USED) +'\n')
    file.write('TECHNICIAN_DISTANCE = '+ str(TECHNICIAN_DISTANCE) +'\n')
    file.write('NUMBER_OF_TECHNICIAN_DAYS = '+ str(NUMBER_OF_TECHNICIAN_DAYS) +'\n')
    file.write('NUMBER_OF_TECHNICIANS_USED = '+ str(NUMBER_OF_TECHNICIANS_USED) +'\n')
    file.write('IDLE_MACHINE_COSTS = '+ str(IDLE_MACHINE_COSTS) +'\n')
    file.write('TOTAL_COST = '+ str(TOTAL_COST) +'\n')
     
    for day in Days:
        file.write('\n')
        file.write('DAY = ' + str(day[0]) +'\n')
        file.write('NUMBER_OF_TRUCKS = ' + str(day[1]) + '\n')
        if day[1] > 0:
            truckID = 0
            for cluster in scheduleDelivery:
                for route in cluster[day[0]-1]:
                    if route != []:
                        Routes = [str(x) for x in route]
                        RoutesString = ' '.join(Routes)
                        truckID += 1
                        file.write(str(truckID)+' '+ RoutesString + '\n')
        file.write('NUMBER_OF_TECHNICIANS = ' + str(day[2]) + '\n')
        if day[2] > 0:
            for cluster in scheduleTechnicians: 
                for route in cluster[day[0]-1]:
                    if route != []:
                        Routes = [str(x) for x in route]
                        RoutesString = ' '.join(Routes)
                        file.write(RoutesString + '\n')
                 
    file.close()
     
    return
###########################################################
### main
def main():

    return

if __name__ == '__main__':
    main()

