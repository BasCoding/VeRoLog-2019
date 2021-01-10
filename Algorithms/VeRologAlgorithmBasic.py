# -*- coding: utf-8 -*-
"""

Purpose:
    Run the basic algorithm that solves the VeRolog problem

Date:
    2019/1/31

"""
###########################################################
### imports
import numpy as np
import timeit as ti
from networkx import nx
from readVeRologfiles import *
from makeSolutionFile import *
import copy
###########################################################
### called in greedyCenter()
def distance(Graph, lVertexes, lSet):
    """
    Purpose:
        Calculate the distance between a point in the graph and the points already included in the centers set such that we can
        determine the next point that will be added to our solution set
    Input:
        Graph, graph with the distances of the complete graph
        lVertexes, list with all the vertices our problem has
        lSet, list with the set of points that are the chosen centers for our solution
    Output:
        fRealMaxV, the vertex with the largest distance to the centers in the set, which will be included next in the set
    """
    fMinV=None
    fRealMax= 0
    fRealMaxV= None
    for v in lVertexes:
        fMinDist= np.inf
        for i in lSet:
            iDistance= Graph[i][v]['weight']
            if iDistance < fMinDist:
                 fMinDist= iDistance
                 fMinV= v  
        if fMinDist > fRealMax:
            fRealMax= fMinDist
            fRealMaxV= fMinV      
    return fRealMaxV
###########################################################
### called in kClusters()
def greedyCenter(Graph, iK, numberLocations):
    """
    Purpose:
        Apply the greedy algorithm to our graph to find a set with iK points, which is the solution of our problem
    Input:
        Graph, matrix with the distances of the complete graph
        iK, integer which represents the k-centers in the k-center problem
        numberLocations, integer with the number of locations in the problem
    Output:
        lSet, list of the points included in our solution for the problem
    """    
    lSet=[1]
    lVertexes=list(range(2,numberLocations+1))
    while len(lSet) < iK+1:
        iMaxDist= distance(Graph, lVertexes, lSet)
        lVertexes.remove(iMaxDist)
        lSet.append(iMaxDist)
    
    lSet.remove(1)
    
    return lSet
###########################################################
### called in main()
def kClusters(iK,Graph,requests,technicians,numberLocations,numberRequests,numberTechnicians):
    """
    Purpose:
        Divide the locations and requests into k-clusters
    Input:
        iK, integer which represents the k-centers in the k-center problem
        Graph, graph with the distances of the complete graph
        requests, matrix with the requests of the problem
        technicians, matrix with the technicians of the problem
        numberLocations, integer with the number of locations for the problem
        numberRequests, integer with the number of requests for the problem
        numberTechnicians, integer with the number of technicians for the problem
    Output:
        clusters, list of lists with a cluster in each list
        clusterRequests, list of lists with the requests clustered in each list, based on clusters
        clusterTech, list of lists with the home location of each technician per cluster
    """  
    kcenters = greedyCenter(Graph, iK, numberLocations)
    lVertices=list(range(2,numberLocations+1))
    clusters =[]
    for i in kcenters:
        lVertices.remove(i)
        clusters.append([i])
        
    for vertex in lVertices:
        minDist = np.inf
        cluster = 0
        for center in kcenters:
            distance = Graph[vertex][center]['weight']
            if distance < minDist:
                minDist = distance
                cluster = center
        index = kcenters.index(cluster)
        clusters[index].append(vertex)

    clusterRequests = [list() for i in range(iK)]
    for i in range(numberRequests):
        location = requests[i][1]
        for k in range(iK):
            if location in clusters[k]:
                clusterRequests[k].append(requests[i][0])
    
    clusterTech = [[1] for i in range(iK)]
    for i in range(numberTechnicians):
        for j in range(len(clusters)): 
            if technicians[i][1] in clusters[j]: 
                clusterTech[j].append(technicians[i][1]) 
            
    return clusters,clusterRequests, clusterTech
###########################################################
### called in decideScheduleDelivery(), decideScheduleTech()
def findReqperLoc(location,requests):
    """
    Purpose:
        Find all the requests for a given location
    Input:
        location, integer for which you want to know the requests
        requests, list of all the requests in a cluster
    Output:
        requestsLocation, list of all the requests in the cluster that are on the location
    """ 
    requestsLocation = []
    for i in range(len(requests)):
        if location == requests[i][1]:
            requestsLocation.append(requests[i][0])
    return requestsLocation
###########################################################
### called in decideScheduleDelivery()
def calculateLoad(clusterRequestMatrix, requests,machines):
    """
    Purpose:
        calculate the total load for a given set of requests
    Input:
        clusterRequestMatrix, matrix with the requests of the cluster
        requests, set of requests for which you want to calculate the total load
        machines, matrix with information on each machine
    Output:
        load, integer of total load for the set of requests
    """     
    load = 0
    for request in requests:
        index = np.where(clusterRequestMatrix[:,0] == request)[0].tolist()[0]
        machineType = clusterRequestMatrix[index][4]
        machineSize = machines[machineType-1][1]
        sizeRequest = clusterRequestMatrix[index][5]
        load += machineSize * sizeRequest
       
    return load
###########################################################
### called in decideScheduleDelivery()
def findIndexReq(request,clusterRequestMatrix):
    """
    Purpose:
        Find the index of the request in the given matrix
    Input:
        request, integer with the request for which you want to find the index
        clusterRequestMatrix, matrix with the requests of the cluster
    Output:
        index, integer with the index of the request in the given matrix
    """ 
    index = np.where(clusterRequestMatrix[:,0] == request)[0].tolist()[0]
    return index
###########################################################
### called in makeDeliveryScheduleClusters()
def decideScheduleDelivery(constraints,clusterRequestMatrix,Graph,machines):
    '''
    Purpose:
        Make a schedule of the deliveries of the request for each day and each truck
    Input:
        constraints, dictionary with the constraints of the problem
        clusterRequestMatrix, matrix with the requests of a specific cluster
        Graph, the graph of the problem
        machines, matrix with the machines of the problem
    Output:
        schedule, list of lists with all the requests in clusterRequestMatrix scheduled for each day, for each truck
        routes, list of lists with the route (locations route) each truck drives on each day
    '''
    schedule = [list() for i in range(constraints['DAYS'])]
    routes = [list() for i in range(constraints['DAYS'])]
    while clusterRequestMatrix.size != 0:
        day = 1
        while day < constraints['DAYS']:
            #find possible requests for day
            possibleRequests = []
            for i in range(len(clusterRequestMatrix)):
                if clusterRequestMatrix[i][2] <= day:
                    possibleRequests.append(clusterRequestMatrix[i][0])
            #find possible locations for day        
            possibleLocations = [1]
            for request in possibleRequests:
                possibleLocations.append(clusterRequestMatrix[findIndexReq(request,clusterRequestMatrix)][1])
            possibleLocations = list(set(possibleLocations)) #remove duplicates
            G = Graph.subgraph(possibleLocations)
            route = [1]
            requestRoute = []
            remainingLoad = constraints['TRUCK_CAPACITY']
            remainingDist = constraints['TRUCK_MAX_DISTANCE']
            if len(sorted(G[1].items(), key=lambda e: e[1]["weight"])) > 1:
                nearest_neighbour = sorted(G[1].items(), key=lambda e: e[1]["weight"])[1]
            possibleLocations.remove(1)
            while possibleLocations != []:        
                G = Graph.subgraph(possibleLocations) #remove neighbour from graph such that it will not appear again in loop
                if nearest_neighbour[0] in possibleLocations:
                    distNN = Graph[nearest_neighbour[0]][1]['weight'] + Graph[nearest_neighbour[0]][route[-1]]['weight'] #distance of adding neighbour
                    if remainingDist < distNN:
                        possibleLocations = []                
                    else:
                        requestsNew = findReqperLoc(nearest_neighbour[0],clusterRequestMatrix)
                        requestsNew = [value for value in requestsNew if value in possibleRequests]
                        totalLoadNewLoc = calculateLoad(clusterRequestMatrix,requestsNew,machines) 
                        if remainingLoad < totalLoadNewLoc: #if not all requests fit, remove latest due date
                            while remainingLoad < totalLoadNewLoc:
                                dueDatesNewLoc = []
                                for request in requestsNew:
                                    dueDatesNewLoc.append(clusterRequestMatrix[findIndexReq(request,clusterRequestMatrix)][3]) 
                                del requestsNew[np.argmax(dueDatesNewLoc)] #removes latest due date
                                totalLoadNewLoc = calculateLoad(clusterRequestMatrix,requestsNew,machines)
                            if totalLoadNewLoc > 0: 
                                removeNew = []
                                for request in requestsNew: #check time window constraint
                                    if day > clusterRequestMatrix[findIndexReq(request,clusterRequestMatrix)][3]:
                                        removeNew.append(request)
                                for request in removeNew:
                                    requestsNew.remove(request)
                                if requestsNew != []:
                                    route.append(nearest_neighbour[0])
                                    remainingLoad = remainingLoad - totalLoadNewLoc
                                    remainingDist = remainingDist - distNN
                                    requestRoute.extend(requestsNew)
                        else:
                            removeNew = []
                            for request in requestsNew:
                                if day > clusterRequestMatrix[findIndexReq(request,clusterRequestMatrix)][3]:
                                    removeNew.append(request)
                            for request in removeNew: 
                                requestsNew.remove(request)
                            if requestsNew != []:
                                remainingLoad = remainingLoad - totalLoadNewLoc
                                route.append(nearest_neighbour[0])
                                remainingDist = remainingDist - distNN
                                requestRoute.extend(requestsNew)
                        
                        possibleLocations.remove(nearest_neighbour[0])
                        if possibleLocations != []:
                            nearest_neighbour = sorted(G[nearest_neighbour[0]].items(), key=lambda e: e[1]["weight"])[1] #find nearest neighbour of current nearest neighbour
                else:
                    if possibleLocations != []:
                        nearest_neighbour = sorted(G[nearest_neighbour[0]].items(), key=lambda e: e[1]["weight"])[1]
            schedule[day-1].append(requestRoute)
            routes[day-1].append(route)
            for request in requestRoute:
                clusterRequestMatrix = np.delete(clusterRequestMatrix,findIndexReq(request,clusterRequestMatrix), axis=0) 
            day += 1
    return schedule,routes
###########################################################
### called in main
def makeDeliveryScheduleClusters(iK,constraints,requests,clusterRequests,machines,numberRequests,Graph):
    '''
    Purpose:
        make a schedule of the requests and the routes that the truck must take for each cluster
    Input:
        iK, integer with the number of clusters
        constraints, dictionary with the number of days, truck capacity and truck max distance of the problem
        requests, matrix with the requests of the problem
        clusterRequests, the requests of the problem divided over the clusters
        machines, matrix with machines of the problem
        numberRequests, integer with the number of requests
        Graph, the graph for our problem
    Output:
        scheduleClusters, list of lists with the requests scheduled per truck per day per cluster
        routesClusters, list of lists with the locations scheduled per truck per day per cluster  
    '''
    scheduleClusters = []
    routesClusters = []
    for k in range(iK):  
        #duplicate requests for cluster k
        clusterRequestMatrix = np.zeros((len(clusterRequests[k]),6))
        counter = 0
        i=0
        while counter < len(clusterRequests[k]):
            if requests[i][0] == clusterRequests[k][counter]:
                clusterRequestMatrix[counter,:] = requests[i,:]
                counter +=1
            i += 1
        clusterRequestMatrix = clusterRequestMatrix.astype(int)
        deliveryCluster = decideScheduleDelivery(constraints,clusterRequestMatrix,Graph,machines)
        scheduleClusters.append(deliveryCluster[0])
        routesClusters.append(deliveryCluster[1])
    return scheduleClusters,routesClusters
###########################################################
### called in decideScheduleTech()
def findAvailableTechsDay(availableTechSched,day,numberTechnicians,constraints):
    '''
    Purpose:
        make a list with the available technicians for a specific day, considering the maximum consecutive working days
    Input:
        availableTechSched, matrix with a schedule that keeps track of the days a technician works
        day, the day for which we want to check availability
        numberTechnicians, integer with the number of technicians
        constraints, dictionary with the constraints
    Output:
        availableTechs, list of available techs on the day
    '''    
    availableTechs = []
    for tech in range(numberTechnicians): 
        if availableTechSched[day-1][tech] == 0:
            if day > 5:
                if np.sum(availableTechSched[day-6:day,tech]) < 5: 
                    if np.sum(availableTechSched[day-7:day-1,tech]) < 5:
                        if np.sum(availableTechSched[day:day+6,tech]) < 5:
                            availableTechs.append(tech+1)
            else: 
                availableTechs.append(tech+1)
    for tech in availableTechs:
        for j in range(constraints['DAYS']-5):
            if np.sum(availableTechSched[j:j+5,tech-1]) == 4 and np.sum(availableTechSched[j:j+7,tech-1]) > 4:
                try: 
                    availableTechs.remove(tech)
                except ValueError:
                    pass
    return availableTechs
###########################################################
### called in decideScheduleTech(), makeTechSchedule()
def findTechsLoc(locations,technicians,numberTechnicians):
    """
    Purpose:
        Find all the technicians that can work on a set of locations
    Input:
        locations, list of location(s) for which you want to find the technicians
        technicians, matrix with all the technicians
        numberTechnicians, integer with the number of technicians
    Output:
        techsLocation, list of technicians that can work on the locations
    """ 
    techsLocation = []
    for location in locations:
        for i in range(numberTechnicians):
            if location == technicians[i][1]:
                techsLocation.append(technicians[i][0])
    return techsLocation
###########################################################
### called in decideScheduleTech()
def removeReqID(ID,Routes,k):  
    """
    Purpose:
        Remove a request ID from a truckroute when the technician has completed this request
    Input:
        ID, the id of the request the technician has completed
        Routes, list of list with the route of every truck on every day
        k, cluster for which you need to remove the ID
    Output:
        Routes, list of list with the route of every truck on every day with the ID removed
    """ 
    for day in Routes[k]:
        for truck in day: 
            try: 
                truck.remove(ID)
            except ValueError:
                pass
    return Routes
###########################################################
### called in decideScheduleTech()
def varTechnicians(ID,technicians,numberTechnicians):
    """
    Purpose:
        Find the maximum travelling distance, maximum number of requests, skillset and the home location of technician ID
    Input:
        ID, the id of the technician
        technicians, matrix with the technicians of the problem
        numberTechnicians, integer with the number of technicians
    Output:
        maxDist, integer with the maximum distance of the technician
        maxReq, integer with the maximum number of requests of the technician
        skills, matrix with the skillset of the technician
        location, integer with the home location of the technician
    """ 
    for i in range(numberTechnicians): 
        if ID == technicians[i][0]:
            location = technicians[i][1]
            maxDist = technicians[i][2]
            maxReq = technicians[i][3]
            skills = technicians[i][4:technicians.shape[1]]
    return maxDist, maxReq, skills, location
###########################################################
### called in decideScheduleTech()
def requestInfo(ID,requests,machines,numberRequests,numberMachines):
    """
    Purpose:
        Find the machine type, number of machines, machine penalty and location ID of request ID
    Input:
        ID, the id of the request
        requests, matrix with the requests of the problem
        machines, with the machines of the problem
        numberRequests, integer with the number of requests
        numberMachines, integer with the number of machines
    Output:
        machineType, integer with the machine type of the request
        nrMachines, integer with the number of machines of the request
        machinePenalty, integer with the penalty of the machineType corresponding to the request
        location, integer with the location of the request
    """ 
    for i in range(numberRequests): 
        if ID == requests[i][0]:
            location = requests[i][1]
            machineType = requests[i][4]
            nrMachines = requests[i][5]
            for j in range(numberMachines):
                if machineType == machines[j][0]:
                    machinePenalty = machines[j][2]
    return machineType, nrMachines, machinePenalty, location 
###########################################################
### called in makeTechSchedule()
def decideScheduleTech(k,Routes,constraints,requests,machines,numberRequests,numberMachines,numberLocations,technicians,numberTechnicians,techniciansCluster,Graph,availableTechSched):
    '''
    Purpose:
        make a schedule of the requests each technician must do, for cluster k
    Input:
        k, cluster that is evaluated
        Routes, list of lists with the routes the truck drive each day for each cluster (requests not location) 
        constraints, dictionary with the number of days, truck capacity and truck max distance of the problem
        requests, matrix with the requests of the problem
        machines, matrix with the machines of the problem
        numberRequests, integer with the number of requests
        numberMachines, integer with the number of machines
        numberLocations, integer with the number of locations
        technicians, the technicians of the problem
        numberTechnicians, integer with the number of technicians
        techniciansCluster, list of all technicians with home location within cluster k
        Graph, the graph for our problem
        availableTechSched, matrix with availability schedule of each technician, updated with schedule of clusters < k
    Output:
        TechRoutesReq, list of lists with the requests scheduled per technician per day for cluster k
        TechRoutesLoc, list of lists with the locations scheduled per technician per day for cluster k 
        availableTechSched, matrix with availability schedule of each technician, updated with schedule of clusters =< k
    '''
    TechRoutesReq = [list() for i in range(constraints['DAYS'])]
    TechRoutesLoc = [list() for i in range(constraints['DAYS'])]
    day = 1    
    while day <= constraints['DAYS']:
        #the possible requests on a day
        requestsDay = [] 
        for deliveryDay in range(1, constraints['DAYS']+1):
            if day > deliveryDay:
                for route in Routes[k][deliveryDay-1]: 
                    requestsDay += route
        technicianDayCount = -1 #for the indexing of the number of technicians in TechRoutesLoc en TechRoutesReq
        while requestsDay != []:
            penalties = []
            locationsDay = []
            for request in requestsDay:             #find highest penalty request and location
                machinePenalty = requestInfo(request,requests,machines,numberRequests,numberMachines)[2]
                nrMachines = requestInfo(request,requests,machines,numberRequests,numberMachines)[1]
                penaltyRequest = machinePenalty * nrMachines
                penalties.append(penaltyRequest)
                locationsDay.append(requestInfo(request,requests,machines,numberRequests,numberMachines)[3])
            availableTechs = findAvailableTechsDay(availableTechSched,day,numberTechnicians,constraints)  #find the available techs (ID) on day, based on consecutive working days constraint
            if len(availableTechs) == 0:
                requestsDay = [] 
            else:
                highestPenaltyReq = requestsDay[np.argmax(penalties)]
                requestsDay.remove(highestPenaltyReq)
                highestPenaltyLoc = requestInfo(highestPenaltyReq,requests,machines,numberRequests,numberMachines)[3]
                typeMachine = requestInfo(highestPenaltyReq,requests,machines,numberRequests,numberMachines)[0]
                subgraphLocations = [highestPenaltyLoc]
                for tech in availableTechs:
                    subgraphLocations.append(varTechnicians(tech,technicians,numberTechnicians)[3])  #make subgraph of home locations of available techs and highest penalty location
                G = Graph.subgraph(subgraphLocations)
                nearestTechs = sorted(G[highestPenaltyLoc].items(), key=lambda e: e[1]["weight"]) #home locations sorted from nearest to highest penalty location to furthest
                nearestTechLoc = []
                for i in range(len(nearestTechs)):
                    nearestTechLoc.append(nearestTechs[i][0])  
                counter = 0 
                #Find a available technician with the nearest homelocation to highestPenaltyReq
                for location in nearestTechLoc:
                    if counter < 1:
                        locationTechs = findTechsLoc([location],technicians,numberTechnicians)
                        for tech in locationTechs: 
                            if tech in availableTechs:
                                skills = varTechnicians(tech,technicians,numberTechnicians)[2] 
                                if skills[typeMachine-1] == 1 and counter < 1: #constraint skills satisfied
                                    maxDist = varTechnicians(tech,technicians,numberTechnicians)[0]
                                    newDist = G[highestPenaltyLoc][location]['weight']
                                    if maxDist >= newDist*2: #constraint distance satisfied
                                        counter += 1
                                        highestPenaltyTech = tech
                                        remainingReq = varTechnicians(highestPenaltyTech,technicians,numberTechnicians)[1] - 1
                                        remainingDist = maxDist - newDist
                                        availableTechSched[day-1][tech-1] = 1
                                        Routes = removeReqID(highestPenaltyReq,Routes,k)
                                        TechRoutesReq[day-1].append([highestPenaltyTech])
                                        technicianDayCount += 1
                                        TechRoutesReq[day-1][technicianDayCount].append(highestPenaltyReq)
                                        #check for available requests on the location
                                        requestsNewLocation = findReqperLoc(highestPenaltyLoc,requests)
                                        requestsNewLocation.remove(highestPenaltyReq)
                                        for request in requestsNewLocation:  
                                            if request in requestsDay:
                                                typeMachine = requestInfo(request,requests,machines,numberRequests,numberMachines)[0]
                                                if skills[typeMachine-1] == 1:
                                                    if remainingReq - 1 >= 0:
                                                        remainingReq -= 1
                                                        TechRoutesReq[day-1][technicianDayCount].append(request)
                                                        Routes = removeReqID(request,Routes,k)
                                                        requestsDay.remove(request)
                                        TechRoutesLoc[day-1].append([highestPenaltyTech,highestPenaltyLoc])
                                        currentLocation = highestPenaltyLoc
                #In this part the selected technician will complete its tour, if a tech is assigned to highestPenaltyReq
                if counter > 0:
                    maxDist, maxReq, skills, home = varTechnicians(highestPenaltyTech,technicians,numberTechnicians)
                    subgraphLocations = list(locationsDay)
                    subgraphLocations.append(home)
                    while remainingReq > 0: 
                        G = Graph.subgraph(subgraphLocations)
                        nearestNeighbours = sorted(G[currentLocation].items(), key=lambda e: e[1]["weight"])[1:]
                        nearestNeighbour = []
                        for i in range(len(nearestNeighbours)):
                            nearestNeighbour.append(nearestNeighbours[i][0])
                        if home in nearestNeighbour:
                            nearestNeighbour.remove(home)
                        counter = 0
                        if nearestNeighbour != []:
                            for neighbour in nearestNeighbour:
                                if counter < 1: #only check next neighbour if last neighbour could not be installed
                                    newDist = G[currentLocation][neighbour]['weight']
                                    homeDist = G[neighbour][home]['weight']
                                    if remainingDist - newDist - homeDist >= 0:
                                        nearestRequests = findReqperLoc(neighbour,requests)
                                        if nearestRequests == [] and neighbour == nearestNeighbour[len(nearestNeighbour)-1]:
                                            remainingReq = 0
                                        else:
                                            for request in nearestRequests:
                                                if request in requestsDay:
                                                    typeMachine = requestInfo(request,requests,machines,numberRequests,numberMachines)[0]
                                                    if skills[typeMachine-1] == 1:
                                                        if remainingReq -1 >= 0:
                                                            counter += 1
                                                            TechRoutesReq[day-1][technicianDayCount].append(request)
                                                            Routes = removeReqID(request,Routes,k)
                                                            requestsDay.remove(request)
                                                            remainingReq -= 1
                                                            if neighbour not in TechRoutesLoc[day-1][technicianDayCount][1:]: 
                                                                TechRoutesLoc[day-1][technicianDayCount].append(neighbour)
                                                                remainingDist -= newDist
                                                                subgraphLocations.remove(currentLocation)
                                                                currentLocation = neighbour
                                                    elif neighbour == nearestNeighbour[len(nearestNeighbour)-1]:
                                                        remainingReq = 0 #if every neighbour and request has been checked and machinetype is not satisfied, end while loop
                                                elif neighbour == nearestNeighbour[len(nearestNeighbour)-1]:
                                                        remainingReq = 0 #same but for in the case that the request is not released yet      
                                    else:
                                        remainingReq = 0
                        else:
                            remainingReq = 0
        day += 1
    
    return TechRoutesReq,TechRoutesLoc,availableTechSched,Routes
###########################################################
### called in main()
def makeTechSchedule(iK,Routes,constraints,requests,machines,numberRequests,numberMachines,numberLocations,technicians,numberTechnicians,clusterTech,Graph):
    '''
    Purpose:
        make a schedule of the requests each technician must do, for each cluster
    Input:
        iK, integer with the number of clusters
        Routes, list of lists with the routes the truck drive each day for each cluster (requests not location) 
        constraints, dictionary with the number of days, truck capacity and truck max distance of the problem
        requests, matrix with the requests of the problem
        machines, matrix with the machines of the problem
        numberRequests, integer with the number of requests
        numberMachines, integer with the number of machines
        numberLocations, integer with the number of locations
        technicians, the technicians of the problem
        numberTechnicians, integer with the number of technicians
        clusterTech, list of lists with the home location of each technician per cluster
        Graph, the graph for our problem
    Output:
        scheduleClusters, list of lists with the requests scheduled per technician per day per cluster
        routesClusters, list of lists with the locations scheduled per technician per day per cluster 
        availableTechSched, matrix with the days on which each technicians works
    '''
    availableTechSched = np.zeros((constraints['DAYS'],numberTechnicians))  
    scheduleClusters = []
    routesClusters = []
    k=0 #because of how the list are set up we need to first specify index 0
    techniciansCluster = list(set(findTechsLoc(clusterTech[k],technicians,numberTechnicians)))
    techCluster = decideScheduleTech(k,Routes,constraints,requests,machines,numberRequests,numberMachines,numberLocations,technicians,numberTechnicians,techniciansCluster,Graph,availableTechSched)
    scheduleClusters.append(techCluster[0])
    routesClusters.append(techCluster[1])
    availableTechSched = techCluster[2]
    Routes = techCluster[3]
    
    return scheduleClusters,routesClusters,availableTechSched
###########################################################
### called in main()
def calcDeliveryCost(scheduleDelivery,costs,Graph,constraints,requests,machines,numberRequests,numberMachines):
    '''
    Purpose:
        Calculate the delivery costs
    Input:
        scheduleDelivery, list of lists with the requests scheduled per truck per day
        costs, dictionary with the costs of the problem
        Graph, the graph of the problem
        constraints, dictionary with the constraints of the problem
        requests, matrix with the requests of the problem
        machines, matrix with the machines of the problem
        numberRequests, integer with number of requests
        numberMachines, integer with number of machines
    Output:
        deliveryCost, total of all the delivery cost
        truckDistance, the total distance the trucks will drive
        numberTrucks, the maximum number of trucks used on one day (number of trucks in the truck fleet)
        truckDays, the total number of trucks days used (total number of trucks each day summed over the whole planning horizon)
        numberTrucksDay, the total number of trucks used for each day
        Days, list per day with the number of trucks 
    '''    
    #calculate the total truck distance of all the clusters combined
    truckDistance = 0
    for day in scheduleDelivery:
        for truck in day:
            truckDistance += calculateDistanceTour(truck,requests,machines,numberRequests,numberMachines,Graph)
    #calculate the total number of trucks for each day
    Days = [[i+1] for i in range(constraints['DAYS'])]   
    numberTrucksDay = [list() for i in range(constraints['DAYS'])]
    for day in range(constraints['DAYS']):
        trucksCountDay = 0
        trucksCountDay += sum(len(truck) > 0 for truck in scheduleDelivery[day])
        numberTrucksDay[day].append(trucksCountDay)
        Days[day].append(trucksCountDay)
    #calculate max nr of trucks used on a single day 
    trucksUsed = max(numberTrucksDay)[0]
    #calculate the total number of trucks days (total number of trucks per day over the whole planning horizon)        
    truckDays = 0
    for day in scheduleDelivery:
        truckDays += sum(len(truck) > 0 for truck in day)
            
    return truckDistance, trucksUsed ,truckDays, Days
###########################################################
### called in calcDeliveryCost()
def calculateDistanceTour(truck,requests,machines,numberRequests,numberMachines,Graph):
    '''
    Purpose:
        Calculate the total distance of a tour (of requests)
    Input:
        truck, the tour for which we want to find the total distance
        requests, matrix with the requests of the problem
        machines, matrix with the machines of the problem
        numberRequests, integer with the number of requests
        numberMachines, integer with the number of machines
        Graph, the graph of the problem
    Output:
        tourDist, integer with total distance of tour
    '''
    tourDist = 0
    lastLocation = 1
    for request in truck:
        if request == 0:
            tourDist += Graph[1][lastLocation]['weight']
            lastLocation = 1
        else:
            location = requestInfo(request,requests,machines,numberRequests,numberMachines)[3]
            tourDist += Graph[location][lastLocation]['weight']
            lastLocation = location
    tourDist += Graph[lastLocation][1]['weight']
    return tourDist
###########################################################
### called in main()
def calcInstalCost(scheduleTechnicians,techniciansRoutes,workingSchedulePerDay,costs,Graph,constraints,numberTechnicians,Days,technicians):
    '''
    Purpose:
        Calculate the installation costs
    Input:
        numberTechnicians, int for number of technicians in problem
        scheduleTechnicians, list of lists with the requests scheduled per tech per day per cluster
        techniciansRoutes, list of lists with the locations scheduled per tech per day per cluster
        workingSchedulePerDay, list of lists per day with a dummy variable for each tech, 1 being working and 0 for rest
        costs, dictionary with the costs of the problem
        Graph, the graph of the problem
        constraints, dictionary with the constraints of the problem
    Output:
        techDistance, total distance of all technicians
        numberTechUsed, total number of technicians used
        numberTechDays, the total number of technician days used
        Days, list per day with nr of trucks and nr of tech
    '''   
    #techDistance
    techDistance = 0
    for cluster in techniciansRoutes: 
        for day in cluster:
            for techRoute in day:
                homeLocation = varTechnicians(techRoute[0],technicians,numberTechnicians)[3]
                techDistance += Graph[homeLocation][techRoute[1]]['weight']
                currentLocation = techRoute[1]
                for location in techRoute[2:]:
                    techDistance += Graph[currentLocation][location]['weight']
                    currentLocation = location
                techDistance += Graph[techRoute[-1]][homeLocation]['weight']
    #numberTechUsed
    numberTechUsed = np.zeros(numberTechnicians)
    for cluster in scheduleTechnicians:
        for day in cluster:
            for tech in day: 
                for i in range(numberTechnicians):
                    if i == tech[0]-1:
                        numberTechUsed[i] = 1
    numberTechUsed = sum(numberTechUsed)  
    #numberTechDays
    totalnumberTechDays = 0
    for day in range(constraints['DAYS']):
        Days[day].append(int(sum(workingSchedulePerDay[day])))
        totalnumberTechDays += sum(workingSchedulePerDay[day])
    
    return techDistance, totalnumberTechDays, numberTechUsed, Days
###########################################################
### called in main()
def calcIdleMachineCost(scheduleDelivery,scheduleTechnicians,constraints,requests, machines,numberRequests,numberMachines):
    '''
    Purpose:
        Calculate the idle machine cost
    Input:
        scheduleDelivery, list of lists with the requests scheduled per truck per day per cluster
        scheduleTechnicians, list of lists with the requests scheduled per tech per day per cluster
        constraints, dictionary with the constraints of the problem
        requests, matrix with the requests of the problem
        machines, with the machines of the problem
        numberRequests, integer with the number of requests
        numberMachines, integer with the number of machines
    Output:
        idleMachineCost, integer with total cost of all machines being idle
    '''     
    deliveryDate = np.zeros(numberRequests)
    installDate = np.zeros(numberRequests)
    for cluster in scheduleDelivery:
        for day in range(constraints['DAYS']):
            for route in cluster[day]:
                for request in route:
                    deliveryDate[request-1] = day+1
    for cluster in scheduleTechnicians:
        for day in range(constraints['DAYS']):
            for route in cluster[day]:
                for request in route[1:]:
                    installDate[request-1] = day+1  
    daysIdle = installDate - deliveryDate
    idleMachineCost = 0
    for requestID in range(numberRequests):
        machineType, nrMachines, machinePenalty, location = requestInfo(requestID+1,requests,machines,numberRequests,numberMachines)
        idleMachineCost += nrMachines * machinePenalty * (daysIdle[requestID]-1)
    
    return idleMachineCost
###########################################################
### main
def main():
    #import instance
    start = ti.default_timer()
    filename = 'VSC2019_ORTEC_early_13.csv'
    constraints,costs,numberMachines, machines, numberLocations, locations, \
        numberRequests, requests, numberTechnicians, technicians = loadfile(filename,';') #function from readVeRologfiles
    
    #set the distances of the graph in a nx.Graph()
    Graph = nx.Graph()
    distancegraph = calculateEucdist(locations,numberLocations) #function from readVeRologfiles
    for i in range(0,numberLocations):
        for j in range(0,numberLocations):
            Graph.add_edge(i+1,j+1,weight=distancegraph[i,j])
    #number of clusters 
    iK = 3
    #kclusters
    clusterLocations,clusterRequests,clusterTech = kClusters(iK,Graph,requests,technicians,numberLocations,numberRequests,numberTechnicians)
    #create Delivery Schedule
    scheduleDelivery, deliveryRoutes = makeDeliveryScheduleClusters(iK,constraints,requests,clusterRequests,machines,numberRequests,Graph)
    #put the request route in one list with all the clusters combined
    scheduleCombined = copy.deepcopy(scheduleDelivery[0])
    for i in range(1,iK):
        for j in range(constraints['DAYS']):
            for truck in scheduleDelivery[i][j]:
                scheduleCombined[j].append(truck)
    scheduleDeliveryCombinedCopy = [copy.deepcopy(scheduleCombined)]   
    #create Technician Schedule
    scheduleTechnicians, techniciansRoutes,workingSchedulePerDay = makeTechSchedule(iK,scheduleDeliveryCombinedCopy,constraints,requests,machines,numberRequests,numberMachines,numberLocations,technicians,numberTechnicians,clusterTech,Graph)
    #SolutionFile
    truckDistance, trucksUsed ,truckDays, Days = calcDeliveryCost(scheduleCombined,costs,Graph,constraints,requests,machines,numberRequests,numberMachines)
    techDistance, numberTechDays, numberTechUsed, Days = calcInstalCost(scheduleTechnicians,techniciansRoutes,workingSchedulePerDay,costs,Graph,constraints,numberTechnicians,Days,technicians)
    idleMachine = calcIdleMachineCost(scheduleDelivery,scheduleTechnicians,constraints,requests, machines,numberRequests,numberMachines)
    
    name = 'TestSolutionFileBasic'
    testInstance = filename
    TRUCK_DISTANCE = int(truckDistance)
    NUMBER_OF_TRUCK_DAYS = truckDays
    NUMBER_OF_TRUCKS_USED = trucksUsed
    TECHNICIAN_DISTANCE = int(techDistance)
    NUMBER_OF_TECHNICIAN_DAYS = int(numberTechDays)
    NUMBER_OF_TECHNICIANS_USED = int(numberTechUsed)
    IDLE_MACHINE_COSTS = int(idleMachine)
    TOTAL_COST = int(truckDistance * costs['TRUCK_DISTANCE_COST'] + trucksUsed * costs['TRUCK_COST'] \
             + truckDays * costs['TRUCK_DAY_COST'] + techDistance * costs['TECHNICIAN_DISTANCE_COST'] + \
             numberTechUsed * costs['TECHNICIAN_COST']  + numberTechDays * costs['TECHNICIAN_DAY_COST'] \
             + idleMachine)
    
    writeSolutionFile(name,testInstance,TRUCK_DISTANCE,NUMBER_OF_TRUCK_DAYS,NUMBER_OF_TRUCKS_USED,TECHNICIAN_DISTANCE,NUMBER_OF_TECHNICIAN_DAYS,
                      NUMBER_OF_TECHNICIANS_USED,IDLE_MACHINE_COSTS,TOTAL_COST,Days,[scheduleCombined],scheduleTechnicians) #function from makeSolutionFile

    stop = ti.default_timer()
    print(stop - start)
    
    #run the following line in command prompt when in the correct folder path to check if the solution is correct
    #python SolutionVerolog2019.py -i VSC2019_ORTEC_early_13.txt -s TestSolutionFileBasic.txt
    return

if __name__ == '__main__':
    main()













