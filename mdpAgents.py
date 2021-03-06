# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

# This class holds the utilities in a 2-D array
class grid():
    
    def __init__(self, state):
        # Required information about the world
        pacmanOrg = api.whereAmI(state)
        self.walls = api.walls(state)
        self.caps = api.capsules(state)
        self.reward = api.food(state)
        self.loss = api.ghosts(state) 
        if(len(self.loss) > 0):
            self.loss[0] = (int(self.loss[0][0]), int(self.loss[0][1]))

        # Ignore scared ghosts
        for ghost in api.ghostStates(state):
            if(ghost[0] in self.loss and ghost[1] == 1):
                self.loss.remove(ghost[0])
        

        # Grid dimentions based on last wall co-ordinate
        self.x1 = self.walls[len(self.walls) - 1][0] + 1
        self.y1 = self.walls[len(self.walls) - 1][1] + 1
       

        self.grid = [[0 for y in range(self.y1)]
                        for x in range(self.x1)]


        #Intialize default utilities will be used as rewards
        for x in range(self.x1):
            for y in range(self.y1):
                closeGhosts = api.distanceLimited(self.loss, state, 4)  
                if (x,y) in self.walls:
                    self.grid[x][y] = None
                elif (x,y) in self.loss:
                    self.grid[x][y] = -20
                elif (x,y) in self.caps:
                    self.grid[x][y] = 10
                # Larger grids        
                elif (self.x1 > 7):
                    # If there are nearby ghosts subtract ghost score divided by distance
                    if(len(closeGhosts) >= 1):
                        if (x,y) in self.reward:
                            self.grid[x][y] = 1  
                        else :
                            self.grid[x][y] = 0
                    else:
                        if (x,y) in self.reward:
                            self.grid[x][y] = 1 
                        else :
                            self.grid[x][y] = 0
                #Smaller Grids
                else:    
                    if (x,y) in self.reward:
                        if(len(self.reward) > 1):
                            if((x,y) == (1,1)):
                                self.grid[x][y] = 5
                            else:
                                self.grid[x][y] = 1
                        else:
                            self.grid[x][y] = 10
                    else :
                        self.grid[x][y] = 0
        # Override rewards for legal spaces near ghosts
        if(self.x1 > 7):
            for y in range(self.y1):
                for x in range(self.x1):
                    if (x,y) in self.loss:
                        if(x + 1, y) not in self.walls:
                            self.grid[x + 1][y] = -15
                            if(x + 2, y) not in self.walls and (x + 2) < self.x1 :
                                self.grid[x + 2][y] = -10                      
                        if(x - 1, y) not in self.walls:
                            self.grid[x - 1][y] = -15
                            if(x - 2, y) not in self.walls and (x - 2) > 0:
                                self.grid[x - 2][y] = -10                   
                        if(x, y + 1) not in self.walls:
                            self.grid[x][y + 1] = -15
                            if(x, y + 2) not in self.walls and (y + 2) < self.y1:
                                self.grid[x][y + 2] = -10
                        if(x, y - 1) not in self.walls:
                            self.grid[x][y - 1] = -15
                            if(x, y - 2) not in self.walls and (y - 2) > 0:
                                self.grid[x][y - 2] = -10
                        if (x + 1, y + 1) not in self.walls :
                            self.grid[x + 1][y + 1] = -10
                        if (x + 1, y - 1) not in self.walls :
                            self.grid[x + 1][y - 1] = -10
                        if (x - 1, y + 1) not in self.walls :
                            self.grid[x - 1][y + 1] = -10
                        if (x - 1, y - 1) not in self.walls :
                            self.grid[x - 1][y - 1] = -10
                        
                        
    #Return the manhattan distance between two points
    def manhattanDistance(self,position, position1):
        return abs(position[0] - position1[0]) + abs(position[1] - position1[1]) 

class MDPAgent(Agent):

    def __init__(self):
        #Keep track of last ghost location
        self.lastGhost = (4,1)
        self.layout = None
        
    def final(self, state):
        #Reset ghost location and grid object
        self.lastGhost = (4,1)
        self.layout = None

    # Return the optimal move based on value iteration
    def getAction(self, state):
        x = api.whereAmI(state)[0]
        y = api.whereAmI(state)[1]
        l = api.legalActions(state)  
        # Create grid of utilites       
        self.layout = grid(state)


        
        
        if(len(self.layout.grid) < 8 and self.lastGhost != (0,0)):
            self.pathProp(self.lastGhost, self.layout.loss[0], self.legalCo(self.layout.loss[0][0], self.layout.loss[0][1], self.layout.walls), self.layout.walls, 1, 5 , x , y)
            self.layout.grid[self.lastGhost[0]][self.lastGhost[1]] = -20
            self.layout.grid[self.layout.loss[0][0]][self.layout.loss[0][1]] = -20

        reward = self.layout.grid[:]
        
        # Replace intial grid by final converged values
        self.layout.grid = self.bellman(self.layout.grid, reward, self.layout.loss, self.layout.walls)
        
        if Directions.STOP in l:
            l.remove(Directions.STOP)

        scores = {}

        north = Directions.NORTH in l
        east = Directions.EAST in l
        west = Directions.WEST in l
        south = Directions.SOUTH in l
        
        # Calculate expected value of moving north
        if(north and east and west):
            scores[Directions.NORTH] = 0.8 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x - 1][y] 
        elif(not north and east and west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x - 1][y]
        elif(not north and not east and west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x - 1][y]
        elif(not north and not east and not west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(not north and east and not west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(north and not east and not west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(north and east and not west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(north and not east and west):
            scores[Directions.NORTH] =0.8 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x - 1][y]
        
        # Calculate the expected value of moving east
        if(north and east and south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y + 1] + 0.8 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y - 1]
        elif(not north and east and south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y -1]
        elif(not north and not east and south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y - 1]
        elif(not north and not east and not south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(not north and east and not south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(north and not east and not south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y + 1] + 0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(north and east and not south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y + 1] + 0.8 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(north and not east and south):
            scores[Directions.EAST] =0.1 * self.layout.grid[x][y + 1] + 0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y - 1]  
        
        # Calculate the expected value of moving west
        if(north and south and west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y - 1] + 0.8 * self.layout.grid[x - 1][y]
        elif(not north and south and west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y - 1] + 0.8 * self.layout.grid[x - 1][y]
        elif(not north and not south and west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x - 1][y]
        elif(not north and not south and not west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x][y]
        elif(not north and south and not west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y - 1] + 0.8 * self.layout.grid[x][y]
        elif(north and not south and not west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x][y]
        elif(north and south and not west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y - 1] + 0.8 * self.layout.grid[x][y]
        elif(north and not south and west):
            scores[Directions.WEST] =0.1 * self.layout.grid[x][y + 1] + 0.1 * self.layout.grid[x][y] + 0.8 * self.layout.grid[x - 1][y]   
        
        # Calculate expected value of moving south
        if(south and east and west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y - 1] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x - 1][y] 
        elif(not south and east and west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x - 1][y]
        elif(not south and not east and west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x - 1][y]
        elif(not south and not east and not west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(not south and east and not west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(south and not east and not west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y - 1] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x][y]
        elif(south and east and not west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y - 1] + 0.1 * self.layout.grid[x + 1][y] + 0.1 * self.layout.grid[x][y]
        elif(south and not east and west):
            scores[Directions.SOUTH] =0.8 * self.layout.grid[x][y - 1] + 0.1 * self.layout.grid[x][y] + 0.1 * self.layout.grid[x - 1][y]

        bestDirection = max(scores, key = scores.get)
        if(scores[bestDirection] == 0):
            #default movement if there are no utilites
            bestDirection = Directions.WEST
        
        if(bestDirection == Directions.NORTH):
            if(len(self.layout.loss) > 0):
                self.lastGhost = self.layout.loss[0]
            return api.makeMove(Directions.NORTH, l)
        if(bestDirection == Directions.EAST):
            if(len(self.layout.loss) > 0):
                self.lastGhost = self.layout.loss[0]
            return api.makeMove(Directions.EAST, l)
        if(bestDirection == Directions.SOUTH):
            if(len(self.layout.loss) > 0):
                self.lastGhost = self.layout.loss[0]
            return api.makeMove(Directions.SOUTH, l)
        if(bestDirection == Directions.WEST):
            if(len(self.layout.loss) > 0):
                self.lastGhost = self.layout.loss[0]
            return api.makeMove(Directions.WEST, l)
        

    # Implements the bellman equation to perform value iteration
    # @param r default rewards of each state
    # @param g and replaces values untill they converge
    # @return g containing updated utilites
    
    def bellman(self, g, r, loss, walls):
        # index to keep track of number of iterations
        saftey= 0
        # Boolean value to indicate whether values have converged
        flag = True
        while flag and saftey < 1000:
            # Intialize and copy grid to store temporary values
            copyGrid = [[0 for y in range(len(g[0]))]
                          for x in range(len(g))]
            for i in range(len(g)):
                for ii in range(len(g[0])):
                    copyGrid[i][ii] = g[i][ii]

            # Update values in the copied grid
            
            for i in range(len(g)):
                for ii in range(len(g[0])):
                    # Is not terminal state
                    if((i,ii) not in walls):
                        #Add defualt reward of state to the max expected value of state
                        if(len(g) > 7):
                            copyGrid[i][ii] = r[i][ii] + 0.2 * self.maxExpected(i ,ii, self.legalCo(i,ii,walls), g)
                        else :
                            copyGrid[i][ii] = r[i][ii] + 0.82 * self.maxExpected(i ,ii, self.legalCo(i,ii,walls), g)
            flag = False
            for i in range(len(g)):
                for ii in range(len(g[0])):
                    # Values have not converged
                    if(g[i][ii] != copyGrid[i][ii]):
                        flag = True      
            saftey += 1
            g = copyGrid[:]
        return g
        

    def manhattanDistance(self,position, position1):
        return abs(position[0] - position1[0]) + abs(position[1] - position1[1]) 

    # Get the max expected value of a position (x,y)
    def maxExpected(self, x, y, legal, g):
        
        expected = []
        north = (x, y + 1 ) in legal
        east = (x + 1, y) in legal
        west = (x - 1, y) in legal
        south = (x, y - 1) in legal
        
        # Value of moving North 
        if(north and east and west):
            expected.append(0.8 * g[x][y + 1] + 0.1 * g[x + 1][y] + 0.1 * g[x - 1][y]) 
        elif(not north and east and west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x + 1][y] + 0.1 * g[x - 1][y])
        elif(not north and not east and west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x][y] + 0.1 * g[x - 1][y])
        elif(not north and not east and not west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x][y] + 0.1 * g[x][y])
        elif(not north and east and not west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x + 1][y] + 0.1 * g[x][y])
        elif(north and not east and not west):
            expected.append(0.8 * g[x][y + 1] + 0.1 * g[x][y] + 0.1 * g[x][y])
        elif(north and east and not west):
            expected.append(0.8 * g[x][y + 1] + 0.1 * g[x + 1][y] + 0.1 * g[x][y])
        elif(north and not east and west):
            expected.append(0.8 * g[x][y + 1] + 0.1 * g[x][y] + 0.1 * g[x - 1][y])    
        
        # Value of moving East
        if(north and east and south):
            expected.append(0.1 * g[x][y + 1] + 0.8 * g[x + 1][y] + 0.1 * g[x][y - 1]) 
        elif(not north and east and south):
            expected.append(0.1 * g[x][y] + 0.8 * g[x + 1][y] + 0.1 * g[x][y - 1])
        elif(not north and not east and south):
            expected.append(0.1 * g[x][y] + 0.8 * g[x][y] + 0.1 * g[x][y - 1])
        elif(not north and not east and not south):
            expected.append(0.1 * g[x][y] + 0.8 * g[x][y] + 0.1 * g[x][y])
        elif(not north and east and not south):
            expected.append(0.1 * g[x][y] + 0.8 * g[x + 1][y] + 0.1 * g[x][y])
        elif(north and not east and not south):
            expected.append(0.1 * g[x][y + 1] + 0.8 * g[x][y] + 0.1 * g[x][y])
        elif(north and east and not south):
            expected.append(0.1 * g[x][y + 1] + 0.8 * g[x + 1][y] + 0.1 * g[x][y])
        elif(north and not east and south):
            expected.append(0.1 * g[x][y + 1] + 0.8 * g[x][y] + 0.1 * g[x][y - 1])    
        
        # Value of moving West 
        if(north and south and west):
            expected.append(0.1 * g[x][y + 1] + 0.1 * g[x][y - 1] + 0.8 * g[x - 1][y]) 
        elif(not north and south and west):
            expected.append(0.1 * g[x][y] + 0.1 * g[x][y - 1] + 0.8 * g[x - 1][y])
        elif(not north and not south and west):
            expected.append(0.1 * g[x][y] + 0.1 * g[x][y] + 0.8 * g[x - 1][y])
        elif(not north and not south and not west):
            expected.append(0.1 * g[x][y] + 0.1 * g[x][y] + 0.8 * g[x][y])
        elif(not north and south and not west):
            expected.append(0.1 * g[x][y] + 0.1 * g[x][y - 1] + 0.8 * g[x][y])
        elif(north and not south and not west):
            expected.append(0.1 * g[x][y + 1] + 0.1 * g[x][y] + 0.8 * g[x][y])
        elif(north and south and not west):
            expected.append(0.1 * g[x][y + 1] + 0.1 * g[x][y - 1] + 0.8 * g[x][y])
        elif(north and not south and west):
            expected.append(0.1 * g[x][y + 1] + 0.1 * g[x][y] + 0.8 * g[x - 1][y])    

        # Value of moving South
        if(south and east and west):
            expected.append(0.8 * g[x][y - 1] + 0.1 * g[x + 1][y] + 0.1 * g[x - 1][y]) 
        elif(not south and east and west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x + 1][y] + 0.1 * g[x - 1][y])
        elif(not south and not east and west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x][y] + 0.1 * g[x - 1][y])
        elif(not south and not east and not west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x][y] + 0.1 * g[x][y])
        elif(not south and east and not west):
            expected.append(0.8 * g[x][y] + 0.1 * g[x + 1][y] + 0.1 * g[x][y])
        elif(south and not east and not west):
            expected.append(0.8 * g[x][y - 1] + 0.1 * g[x][y] + 0.1 * g[x][y])
        elif(south and east and not west):
            expected.append(0.8 * g[x][y - 1] + 0.1 * g[x + 1][y] + 0.1 * g[x][y])
        elif(south and not east and west):
            expected.append(0.8 * g[x][y - 1] + 0.1 * g[x][y] + 0.1 * g[x - 1][y]) 

        return max(expected)
    
    # Get the legal positions a given postion (x,y) can move to
    # @param w list of walls 
    def legalCo(self, x, y, w):
        legal = []

        # Use w to calculate upper bound
        if x + 1 <= w[len(w) - 1][0] and (x + 1, y) not in w :
            legal.append((x + 1, y))
        if x - 1 >= 0 and (x - 1, y) not in w :
            legal.append((x - 1, y))
        if y + 1 <= w[len(w) - 1][1] and (x, y + 1) not in w:
            legal.append((x, y + 1))
        if y - 1 >= 0 and (x, y - 1) not in w:
            legal.append((x, y - 1))
        return legal

    def pathProp(self, previousMove, currentGhost, legalGhostCo, w, discount, counter, x ,y):

        #Remove ghosts last move legal  
        if(previousMove in legalGhostCo):
            legalGhostCo.remove(previousMove)
        #Reached a junction
        if(len(legalGhostCo) > 1):
            #Check distance of both coordinates to pacman
            d1 = self.manhattanDistance((legalGhostCo[0][0],legalGhostCo[0][1]) , (x,y))
            d2 = self.manhattanDistance((legalGhostCo[1][0],legalGhostCo[1][1]) , (x,y))
            if(d1 > d2):
                #Update utilites 
                self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = 0.2 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                self.layout.grid[legalGhostCo[1][0]][legalGhostCo[1][1]] = 0.8 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                #Legal coordinate 0 is moving into dead end 
                if(legalGhostCo[0][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.1, 1, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.4, 3, x, y)
                    return
                #Legal coordinate 1 is moving into dead end 
                elif(legalGhostCo[1][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.1, 3, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.4, 1, x, y)
                    return
                #Neither coordinate is moving into dead end
                else:
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.1, 5, x,y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.4, 5, x ,y)  
                    return
            elif(d2 > d1):
                self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = 0.8 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                self.layout.grid[legalGhostCo[1][0]][legalGhostCo[1][1]] = 0.2 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                if(legalGhostCo[0][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.4, 1, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.1, 3,x ,y )
                    return
                elif(legalGhostCo[1][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.4, 3, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w,  0.1, 1, x, y)
                    return
                else:
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.4, 5, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.1, 5, x, y)  
                    return
            else:
                self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = 0.5 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                self.layout.grid[legalGhostCo[1][0]][legalGhostCo[1][1]] = 0.5 * discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                if(legalGhostCo[0][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.25, 1, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.25, 3,x ,y )
                    return
                elif(legalGhostCo[1][0] == 4):
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.25, 3, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w,  0.25, 1, x, y)
                    return
                else:
                    self.pathProp(currentGhost, (legalGhostCo[0][0], legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.25, 5, x, y)
                    self.pathProp(currentGhost, (legalGhostCo[1][0], legalGhostCo[1][1]), self.legalCo(legalGhostCo[1][0], legalGhostCo[1][1], w), w, 0.25, 5, x, y)  
                    return
        
        #Base case
        elif(len(legalGhostCo) == 0 or counter <= 0):
            return
        #Not at a junction
        else:
            counter -= 1
            if((legalGhostCo[0][0], legalGhostCo[0][1]) in self.layout.reward):
                if(len(self.layout.reward) == 1):
                    self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = 10 + discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                else:
                    self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = 1 + discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
            else:
                self.layout.grid[legalGhostCo[0][0]][legalGhostCo[0][1]] = discount * self.layout.grid[currentGhost[0]][currentGhost[1]]
                
            self.pathProp(currentGhost, (legalGhostCo[0][0],legalGhostCo[0][1]), self.legalCo(legalGhostCo[0][0], legalGhostCo[0][1], w), w, 0.5, counter, x, y) 
            return