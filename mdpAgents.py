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
        print(self.loss)
        
        # Ignore scared ghosts
        for ghost in api.ghostStates(state):
            if(ghost[0] in self.loss and ghost[1] == 1):
                self.loss.remove(ghost[0])
        
        # Grid dimentions based on last wall co-ordinate
        self.x1 = self.walls[len(self.walls) - 1][0] + 1
        self.y1 = self.walls[len(self.walls) - 1][1] + 1
       

        self.grid = [[0 for y in range(self.y1)]
                        for x in range(self.x1)]

        self.terminal = [[0 for y in range(self.y1)]
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
        else:
            for y in range(self.y1):
                for x in range(self.x1):
                    if (x,y) in self.loss:
                        if(x + 1, y) not in self.walls and len(self.reward) > 1:
                            self.grid[x + 1][y] = -18                   
                        if(x - 1, y) not in self.walls and len(self.reward) > 1:
                            self.grid[x - 1][y] = -18                
                        if(x, y + 1) not in self.walls and len(self.reward) > 1:
                            self.grid[x][y + 1] = -18
                        if(x, y - 1) not in self.walls and len(self.reward) > 1:
                            self.grid[x][y - 1] = -18
                        # if (x + 1, y + 1) not in self.walls and len(self.reward) > 1:
                        #     self.grid[x + 1][y + 1] = -12.8
                        # if (x + 1, y - 1) not in self.walls and len(self.reward) > 1:
                        #     self.grid[x + 1][y - 1] = -12.8
                        # if (x - 1, y + 1) not in self.walls and len(self.reward) > 1:
                        #     self.grid[x - 1][y + 1] = -12.8
                        # if (x - 1, y - 1) not in self.walls and len(self.reward) > 1:
                        #     self.grid[x - 1][y - 1] = -12.8
                        
                        
    # Return Pacmans manhattan distance from the closest food
    def closestFood(self, state, pos): 
        food = api.food(state) 
        score = 100
        for x in food :
            if (self.manhattanDistance(pos, x) < score):                
                score = self.manhattanDistance(pos, x)   
        return score
    
    # Return pacmans distance from the closest Ghost
    def closestGhost(self, loss, pos): 
        retval = loss[0]
        for x in loss :
            if self.manhattanDistance(pos, x) < self.manhattanDistance(pos, retval):
                retval = x      
        return self.manhattanDistance(retval,pos)

    #Return the manhattan distance between two points
    def manhattanDistance(self,position, position1):
        return abs(position[0] - position1[0]) + abs(position[1] - position1[1]) 

class MDPAgent(Agent):

    def __init__(self):
        self.lastGhost = (0,0)
    # def final(self):
    #     self.lastGhost =
    # Return the optimal move based on value iteration
    def getAction(self, state):
        x = api.whereAmI(state)[0]
        y = api.whereAmI(state)[1]
        l = api.legalActions(state)  
        # Create grid of utilites       
        layout = grid(state)
        if(len(layout.grid) < 8):
            print(self.lastGhost[0] , self.lastGhost[1])
            layout.grid[self.lastGhost[0]][self.lastGhost[1]] = 0
            for i in range(len(layout.grid)):
                for ii in range(len(layout.grid[0])):
                    if((i,ii) in layout.loss):
                        ghostLegal = self.legalCo(i,ii, layout.walls)
                        if(self.lastGhost in ghostLegal):
                            ghostLegal.remove(self.lastGhost)
                        if(len(ghostLegal) == 1):
                            layout.grid[ghostLegal[0][0]][ghostLegal[0][1]] = -20 
                        elif(len(ghostLegal) == 2):
                            layout.grid[ghostLegal[0][0]][ghostLegal[0][1]] = -10  
                            layout.grid[ghostLegal[1][0]][ghostLegal[1][1]] = -10  
                        elif(len(ghostLegal) == 3):
                            print("shoudl never go here")
                            # layout.grid[ghostLegal[0][0]][ghostLegal[0][1]] = -6.7  
                            # layout.grid[ghostLegal[1][0]][ghostLegal[1][1]] = -6.7 
                            # layout.grid[ghostLegal[2][0]][ghostLegal[2][1]] = -6.7
                        
        print(layout.grid)
        # Copy inital grid to be used as deafult rewards
        reward = layout.grid[:]
        # Replace intial grid by final converged values
        layout.grid = self.bellman(layout.grid, reward, layout.loss, layout.walls)
        # print(layout.grid[3])
        # print(layout.grid[4])
        # print(layout.grid[5])
        if Directions.STOP in l:
            l.remove(Directions.STOP)

        scores = {}

        north = Directions.NORTH in l
        east = Directions.EAST in l
        west = Directions.WEST in l
        south = Directions.SOUTH in l
        
        # Calculate expected value of moving north
        if(north and east and west):
            scores[Directions.NORTH] = 0.8 * layout.grid[x][y + 1] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x - 1][y] 
        elif(not north and east and west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x - 1][y]
        elif(not north and not east and west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x - 1][y]
        elif(not north and not east and not west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(not north and east and not west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(north and not east and not west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(north and east and not west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y + 1] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(north and not east and west):
            scores[Directions.NORTH] =0.8 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x - 1][y]
        
        # Calculate the expected value of moving east
        if(north and east and south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y + 1] + 0.8 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y - 1]
        elif(not north and east and south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y] + 0.8 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y -1]
        elif(not north and not east and south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y] + 0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y - 1]
        elif(not north and not east and not south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y] + 0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(not north and east and not south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y] + 0.8 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(north and not east and not south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y + 1] + 0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(north and east and not south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y + 1] + 0.8 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(north and not east and south):
            scores[Directions.EAST] =0.1 * layout.grid[x][y + 1] + 0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y - 1]  
        
        # Calculate the expected value of moving west
        if(north and south and west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y - 1] + 0.8 * layout.grid[x - 1][y]
        elif(not north and south and west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y - 1] + 0.8 * layout.grid[x - 1][y]
        elif(not north and not south and west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.8 * layout.grid[x - 1][y]
        elif(not north and not south and not west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.8 * layout.grid[x][y]
        elif(not north and south and not west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y - 1] + 0.8 * layout.grid[x][y]
        elif(north and not south and not west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y] + 0.8 * layout.grid[x][y]
        elif(north and south and not west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y - 1] + 0.8 * layout.grid[x][y]
        elif(north and not south and west):
            scores[Directions.WEST] =0.1 * layout.grid[x][y + 1] + 0.1 * layout.grid[x][y] + 0.8 * layout.grid[x - 1][y]   
        
        # Calculate expected value of moving south
        if(south and east and west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y - 1] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x - 1][y] 
        elif(not south and east and west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x - 1][y]
        elif(not south and not east and west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x - 1][y]
        elif(not south and not east and not west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(not south and east and not west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(south and not east and not west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y - 1] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x][y]
        elif(south and east and not west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y - 1] + 0.1 * layout.grid[x + 1][y] + 0.1 * layout.grid[x][y]
        elif(south and not east and west):
            scores[Directions.SOUTH] =0.8 * layout.grid[x][y - 1] + 0.1 * layout.grid[x][y] + 0.1 * layout.grid[x - 1][y]

        bestDirection = max(scores, key = scores.get)
        if(scores[bestDirection] == 0):
            # print("utilites blocked")
            bestDirection = Directions.WEST
        # for (a,b) in scores.items():
        #     print(a,b)
        # print(" ")
        
        # print(bestDirection)
        

        if(bestDirection == Directions.NORTH):
            self.lastGhost = layout.loss[0]
            return api.makeMove(Directions.NORTH, l)
        if(bestDirection == Directions.EAST):
            self.lastGhost = layout.loss[0]
            return api.makeMove(Directions.EAST, l)
        if(bestDirection == Directions.SOUTH):
            self.lastGhost = layout.loss[0]
            return api.makeMove(Directions.SOUTH, l)
        if(bestDirection == Directions.WEST):
            self.lastGhost = layout.loss[0]
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
                            copyGrid[i][ii] = r[i][ii] + 0.1 * self.maxExpected(i ,ii, self.legalCo(i,ii,walls), g)
                        else :
                            copyGrid[i][ii] = r[i][ii] + 0.8 * self.maxExpected(i ,ii, self.legalCo(i,ii,walls), g)
            flag = False
            for i in range(len(g)):
                for ii in range(len(g[0])):
                    # Values have not converged
                    if(g[i][ii] != copyGrid[i][ii]):
                        flag = True      
            saftey += 1
            g = copyGrid[:]
        return g
        
    
    def closestFood(self, state, pos): 
        food = api.food(state) 
        #closestFood = (0,0)
        score = 100
        for x in food :
            if (util.manhattanDistance(pos, x) < score):
                #closestFood = x  
                score = util.manhattanDistance(pos, x)   
        return score
    
    def closestGhost(self, state, pos): 
        ghost = api.ghosts(state) 
        closestGhost = ghost[0]
        for x in ghost :
            if util.manhattanDistance(pos, x) < util.manhattanDistance(pos, closestGhost):
                closestGhost = x      
        return closestGhost

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

                    
