#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Purpose:
    Preparing the dataset for implemetation of an algorithm which solves the VeRoLog problem. 

Date:
    2019/1/31

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
import csv as csv
###########################################################
###
def calculateEucdist(locations,numberLocations):
    """
        Purpose
            calculate euclidean distance between the different locations by using x and y coordinates
        Input
            locations, np.array with in each line a location (index 0), a x coordinate (index 1) and y coordinate (index 2)
            numberLocations, a integer with the number of locations for the instance
        Output
            graph, a matrix with the distance between every point
    """
    graph = np.zeros((numberLocations,numberLocations))
    for location1 in locations:
        i = location1[0]-1
        x1 = location1[1]
        y1 = location1[2]
        for location2 in locations:
            j = location2[0]-1
            x2 = location2[1]
            y2 = location2[2]
            graph[i][j] = graph[j][i] = np.ceil(np.sqrt((x1-x2)**2+(y1-y2)**2))
            
    return graph

def loadfile(filename,seperator):
    """
        Purpose
            import the data for the given filename
        Input
            filename, name of file that has to be given
            seperator, the seperator of the file, ';' for csv, '\s+' for txt
        Output
            tuple with all the necessary input for the instance in the file
    """
    #import datafile
    data= pd.read_csv(filename, sep=seperator, header=None)
    #read datafile (universal for every instance)
    constraints = data[[0,2]].iloc[2:5]
    constraints = constraints.set_index(0)[2].to_dict()
    constraints = dict((k,int(v)) for k,v in constraints.items())
    costs = data[[0,2]].iloc[5:11]
    costs = costs.set_index(0)[2].to_dict()
    costs = dict((k,int(v)) for k,v in costs.items())    
    numberMachines = int(data.iloc[11][2])
    index= (11+numberMachines+1) #extra step that ensures the right values are taken
    machines = np.array(data[[0,1,2]][12:index].astype(int))
    numberLocations = int(data.iloc[index][2])
    locations = np.array(data[[0,1,2]][index+1:(index+numberLocations+1)].astype(int))
    index += numberLocations+1 #extra step that ensures the right values are taken
    numberRequests = int(data.iloc[index][2])
    requests = np.array(data[[0,1,2,3,4,5]][index+1:(index+numberRequests+1)].astype(int))
    index += numberRequests+1 #extra step that ensures the right values are taken
    numberTechnicians = int(data.iloc[index][2])
    technicians = np.array(data[[i for i in range(0,numberMachines+4)]][index+1:(index+numberTechnicians+1)].astype(int))
    
    return constraints,costs,numberMachines, machines, numberLocations, locations,numberRequests, requests, numberTechnicians, technicians


###########################################################
### main
def main():
  
    return

if __name__ == '__main__':
    main()

