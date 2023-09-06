from queue import PriorityQueue
import Map
import numpy as np
import pandas as pd
from PIL import Image
from typing import Union

#Global variables for some of the methods 
map_height = len(Map.Map_Obj(task=1).int_map)
map_width = len(Map.Map_Obj(task=1).int_map[0]) 


#A helping class for the my version of nodes used in the A* algorithm
class Node():

    def __init__(self) -> None:
        self.y = 0 #Just a base line
        self.x = 0 #Just a base line
        self.value = -1 #Makes everyone not walkable at first
        self.h = 0 #The initial heuritic value
        self.neighbors = [] #Makes a list for neithbors or childeren

    #A helping methed for setting the values for the algorithm
    def set_startStates(self, y: int, x: int, value: int):
        self.y = y #The Y position
        self.x = x #The x position
        self.value = value #The cost of the node


    #The method for setting neithbors or childeren of the nodes
    def set_neighbors(self,node_map) -> None:
        #Checks if it an wall and therfore not of intrest 
        if self.value == -1:
            pass

        #Makes sure the checks are in the range of the map and not to make OutOfIndex problem
        if self.y >= 0+1 and self.y < map_height-1 and self.x >= 0+1 and self.x < map_width-1:
            if node_map[self.y-1][self.x].value != -1:
                self.neighbors.append(node_map[self.y-1][self.x])
                # Noth position
            if node_map[self.y+1][self.x].value != -1:
                self.neighbors.append(node_map[self.y+1][self.x])
                # South position
            if node_map[self.y][self.x-1].value != -1:
                self.neighbors.append(node_map[self.y][self.x-1])
                # East position
            if node_map[self.y][self.x+1].value != -1:
                self.neighbors.append(node_map[self.y][self.x+1])
                # West position

#A helper class to fix an bug with PriorityQueue when there was to equal values of the lenth of the path
class PriorityEntry(object):

    def __init__(self, priority, data):
        self.data = data
        self.priority = priority

    def __lt__(self, other):
        return self.priority < other.priority

#The Master class it the main klass and ment to be a shell for the A* algorithm with the other classes and varibles
class Master():

    def __init__(self, task: int = 1) -> None:
        self.node_map = [[Node() for _ in range(map_width)] for _ in range(map_height)] #Generetes the nessesery 2D matrix for later use
        self.int_map = Map.Map_Obj(task).int_map #Gets the int map from Map
        self.map= Map.Map_Obj(task) #Sets the map after what task it is

        #Converts the 2D matrix with values to a 2D matrix with nodes
        for y in range(map_height):
            for x in range(map_width):
                self.node_map[y][x].set_startStates(y,x,self.int_map[y][x])

        self.start = self.node_map[self.map.get_start_pos()[0]][self.map.get_start_pos()[1]] #Sets the start node
        self.goal = self.node_map[self.map.get_goal_pos()[0]][self.map.get_goal_pos()[1]] #Sets the goal node

    #Calculats the Heuristic value of the node compared to the goal
    def heuristic(self, goal_node:Node, this_node: Node) -> None:
        this_node.h = abs(this_node.y - goal_node.y) + abs(this_node.x - goal_node.x)

    #Sets the goal node 
    def set_goal_node(self, goal_node: Node) -> None:
        self.node_map[goal_node.y][goal_node.x].set_goal_state()

    #A help methode to conect the nodes to each other 
    def set_neighbors(self) -> None:
        for y in range(map_height):
            for x in range(map_width):
                self.node_map[y][x].set_neighbors(self.node_map)


    def a_star(self) -> list:
        self.set_neighbors() #Conects the nodes together

        frontier = PriorityQueue()
        frontier.put(PriorityEntry(0,self.start))
        came_from = dict()
        cost_so_far = dict()
        came_from[self.start] = None
        cost_so_far[self.start] = 0
        

        while not frontier.empty():
            current: Node = frontier.get().data

            #Early exit check 
            if current == self.goal:
                break
            

            next: Node #Defines the next as a Node class
            for next in current.neighbors:
                new_cost: int = cost_so_far[current] + next.value #Calculats the cost at this point
                if (next not in cost_so_far) or new_cost < cost_so_far[next]: #Compares cost and if its been check out before 
                    cost_so_far[next] = new_cost
                    self.heuristic(self.goal,next) #Calculats the heuristic 
                    priority:int = new_cost + next.h
                    frontier.put(PriorityEntry(priority,next))
                    came_from[next] = current

        #Records the path the algorithm did take
        current = self.goal
        path = []
        while current != self.start:
            path.append(current)
            current = came_from[current]
        path.append(self.start)
        path.reverse() #To make it start at the start point

        #Prints the nodes (tiles) that the algorithm whent trogh and the total value it "Spent"
        i:Node
        tot = 0
        for i in path:
            tot += i.value
            print(f"Y: {i.y} X: {i.x}")
        print(f"Total value the path cost: {tot}")

        return path

    def show_map(self)-> None:
        tempMap = [[0 for _ in range(map_width)] for _ in range(map_height)]
        for y in range(map_height):
            for x in range(map_width):
                tempMap[y][x] = self.int_map[y][x]
        answerList = self.a_star()
        for node in answerList:
            tempMap[node.y][node.x] = -2
        
        scale = 20
        image = Image.new('RGB', (map_width * scale, map_height * scale),
                          (255, 255, 0))
        pixels = image.load()

        colors = {
            -1 : (211, 33, 45),  # redish
            1 : (215, 215, 215),  # whiteish
            2 : (166, 166, 166),  # lightgrey
            3 : (96, 96, 96),   # darkgrey
            4 : (36, 36, 36),   # blackish
            -2 : (0, 128, 255),  # blå
            ' G ': (0, 128, 255)   # cyan
        }

        for y in range(map_height):
            for x in range(map_width):
                if self.int_map[y][x] not in colors:
                    continue
                for i in range(scale):
                    for j in range(scale):
                        pixels[x * scale + i, y * scale + j] = colors[tempMap[y][x]]

        image.show()

# Starts A* with the task number in the Master(task)
test = Master(4)
# Prints the result
print(test.show_map())

#Creds in this assignment to to sourses for inspiration for the solution
#First: https://www.redblobgames.com/pathfinding/a-star/introduction.html (Was given in the assignment extra class)
#Second: https://stackoverflow.com/questions/40205223/priority-queue-with-tuples-and-dicts (To help with the PriorytiQueue problem)
