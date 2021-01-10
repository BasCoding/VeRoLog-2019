# VeRoLog-2019
My solution to the VeRoLog Solver Challenge 2019. I have removed the names of the fellow students who helped working on this project to protect their privacy.

In the All Instances folder I have provided a folder with all the instances provided by ORTEC for this problem. 

In the Algorithms folder I have provided the algorithms used to solve the problem, as well as files provided by ORTEC to check the validity of the solution:
baseParser.py - code used to check the validity of the solution
InstanceVerolog2019.py - code used to check the validity of the solution
makeSolutionFile.py - code to change the solution calculated by the algorithm into the right format in order to test the solution
readVeRologfiles.py - code to prepare the data from the instance input file such that the algorithm can solve it
SolutionVerolog2019.py - code used to check the validity of the solution
VeRologAlgorithmBasic.py - first attempt to solve the problem
VeRologAlgorithmCombined.py - combination of the ReschedulingByLocation and RestockAtDepot improvements to the Basic algorithm
VeRologAlgorithmReschedulingByLocation.py - improvement where the technician do not have to travel twice to the same location if the due dates allow it
VeRologAlgorithmRestockAtDepot.py - improvement where trucks are allowed to restock at the depot
VeRologAlgorithmSimulatedAnnealing.py - improvement where simulated annealing is used to improve the truck routing (applied to VeRologAlgorithmCombined algorithm)
VSC2019_ORTEC_early_13.csv - instance for which the algorithm(s) provides a feasible solution
VSC2019_ORTEC_early_15.csv - instance for which the algorithm(s) provides a feasible solution
VSC2019_ORTEC_early_19.csv - instance for which the algorithm(s) provides a feasible solution
VSC2019_ORTEC_early_25.csv - instance for which the algorithm(s) provides a feasible solution

