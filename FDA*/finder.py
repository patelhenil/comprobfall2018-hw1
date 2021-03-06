# -*- coding: utf-8 -*-
import heapq  # used for the so colled "open list" that stores known nodes
import time  # for time limitation
import math

from util import SQRT2
from diagonal_movement import DiagonalMovement
from grid import Grid

# max. amount of tries we iterate until we abort the search
MAX_RUNS = float('inf')
# max. time after we until we abort the search (in seconds)
TIME_LIMIT = float('inf')

# used for backtrace of bi-directional A*
BY_START = 1
BY_END = 2


class ExecutionTimeException(Exception):
    def __init__(self, message):
        super(ExecutionTimeException, self).__init__(message)


class ExecutionRunsException(Exception):
    def __init__(self, message):
        super(ExecutionRunsException, self).__init__(message)


class Finder(object):
    def __init__(self, heuristic=None, weight=1,
                 diagonal_movement=DiagonalMovement.never,
                 weighted=True,
                 time_limit=TIME_LIMIT,
                 max_runs=MAX_RUNS):
        """
        find shortest path
        :param heuristic: heuristic used to calculate distance of 2 points
            (defaults to manhatten)
        :param weight: weight for the edges
        :param diagonal_movement: if diagonal movement is allowed
            (see enum in diagonal_movement)
        :param weighted: the algorithm supports weighted nodes
            (should be True for A* and Dijkstra)
        :param time_limit: max. runtime in seconds
        :param max_runs: max. amount of tries until we abort the search
            (optional, only if we enter huge grids and have time constrains)
            <=0 means there are no constrains and the code might run on any
            large map.
        """
        self.time_limit = time_limit
        self.max_runs = max_runs
        self.weighted = weighted

        self.diagonal_movement = diagonal_movement
        self.weight = weight
        self.heuristic = heuristic

    def calc_cost(self, node_a, node_b):
        """
        get the distance between current node and the neighbor (cost)
        """
        ng = node_a.g
        #if node_b.x - node_a.x == 0 or node_b.y - node_a.y == 0:
            # direct neighbor - distance is 1
        #    ng += 1
        #else:
            # not a direct neighbor - diagonal movement
        #    ng += SQRT2

        ng = math.sqrt((node_a.x-node_b.x)**2 + (node_a.y-node_b.y)**2)

        # weight for weighted algorithms
        if self.weighted:
            ng *= node_b.weight

        return ng

    def apply_heuristic(self, node_a, node_b, heuristic=None):
        """
        helper function to apply heuristic
        """
        if not heuristic:
            heuristic = self.heuristic
        return heuristic(
            abs(node_a.x - node_b.x),
            abs(node_a.y - node_b.y))

    def find_neighbors(self, grid, node, diagonal_movement=None):
        '''
        find neighbor, same for Djikstra, A*, Bi-A*, IDA*
        '''
        if not diagonal_movement:
            diagonal_movement = self.diagonal_movement
        return grid.neighbors(node, diagonal_movement=diagonal_movement)

    def keep_running(self):
        """
        check, if we run into time or iteration constrains.
        :returns: True if we keep running and False if we run into a constraint
        """
        if self.runs >= self.max_runs:
            raise ExecutionRunsException(
                '{} run into barrier of {} iterations without '
                'finding the destination'.format(
                    self.__class__.__name__, self.max_runs))

        if time.time() - self.start_time >= self.time_limit:
            raise ExecutionTimeException(
                '{} took longer than {} seconds, aborting!'.format(
                    self.__class__.__name__, self.time_limit))

    def process_node(self,grid,node, parent, end, open_list, open_value=True):
        '''
        we check if the given node is path of the path by calculating its
        cost and add or remove it from our path
        :param node: the node we like to test
            (the neighbor in A* or jump-node in JumpPointSearch)
        :param parent: the parent node (the current node we like to test)
        :param end: the end point to calculate the cost of the path
        :param open_list: the list that keeps track of our current path
        :param open_value: needed if we like to set the open list to something
            else than True (used for bi-directional algorithms)

        '''
       # print(f'parent ({parent.x},{parent.y})')
        #print(f"Node ({node.x},{node.y})")

        if parent.parent is not None and self.line_of_sight(grid,parent.parent, node):
            # calculate cost from current node (parent) to the next node (neighbor)
            ng = self.calc_cost(parent.parent, node)
            print(f"ng ({ng})")
            print(f"parent.parent.g ({parent.parent.g})")
            print(f"node.g before update ({node.g})")

            if not node.opened or ng + parent.parent.g < node.g:
                node.g = ng + parent.parent.g
                node.h = node.h or \
                         self.apply_heuristic(node, end) * self.weight
                # f is the estimated total cost from start to goal
                node.f = node.g + node.h

                print(f'parent.parent ({parent.parent.x},{parent.parent.y})')
                print(f"node is ({node.x},{node.y}) and f is {node.f}, g is {node.g}, h is {node.h}")


                node.parent = parent.parent

                if not node.opened:
                    heapq.heappush(open_list, node)
                    node.opened = open_value
                else:
                    # the node can be reached with smaller cost.
                    # Since its f value has been updated, we have to
                    # update its position in the open list
                    open_list.remove(node)
                    heapq.heappush(open_list, node)

        else:
            # calculate cost from current node (parent) to the next node (neighbor)
            ng = self.calc_cost(parent, node)

            if not node.opened or ng + parent.g < node.g:
                node.g = ng + parent.g
                node.h = node.h or \
                         self.apply_heuristic(node, end) * self.weight
                # f is the estimated total cost from start to goal
                node.f = node.g + node.h
                node.parent = parent

                print(f'parent ({parent.x},{parent.y})')
                print(f"node is ({node.x},{node.y}) and f is {node.f}, g is {node.g}, h is {node.h}")

                if not node.opened:
                    heapq.heappush(open_list, node)
                    node.opened = open_value
                else:
                    # the node can be reached with smaller cost.
                    # Since its f value has been updated, we have to
                    # update its position in the open list
                    open_list.remove(node)
                    heapq.heappush(open_list, node)

        print("-----------------")


    def line_of_sight(self,grid, s, s_prime):
        x0 = s.x
        y0 = s.y
        x1 = s_prime.x
        y1 = s_prime.y

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        f = 0

        if dx >= dy:
            while x0 != x1:
                f = f + dy

                if f >= dx:
                    if Grid.walkable(grid, int(x0 + (sx - 1) / 2), int(y0 + (sy - 1) / 2)):
                        return False
                    y0 = y0 + sy
                    f = f - dx
                if f != 0 and Grid.walkable(grid,int(x0 + (sx - 1) / 2), int(y0 + (sy - 1) / 2)):
                    return False
                if dy == 0 and Grid.walkable(grid,int(x0 + (sx-1)/2), int(y0)) and Grid.walkable(grid,int(x0 + ((sx-1) / 2)), int(y0-1)):
                    return False
                x0 = x0 + sx

        else:
            while y0 != y1:
                f = f + dx
                if f >= dy:

                    if Grid.walkable(grid,int(x0 + (sx-1) / 2), int(y0 + (sy-1) / 2)):
                        return False
                    x0 = x0 + sx
                    f = f- dy
                if f != 0 and Grid.walkable(grid,int(x0 + (sx-1) / 2), int(y0 + (sy-1) / 2)):
                    return False
                if dx == 0 and Grid.walkable(grid,int(x0), int(y0 + (sy-1) / 2)) and Grid.walkable(grid,int(x0-1), int(y0 + (sy-1) / 2)):
                    return False
                y0 = y0 + sy

        return True


    def find_path(self, start, end, grid):
        """
        find a path from start to end node on grid by iterating over
        all neighbors of a node (see check_neighbors)
        :param start: start node
        :param end: end node
        :param grid: grid that stores all possible steps/tiles as 2D-list
        :return:
        """
        self.start_time = time.time()  # execution time limitation
        self.runs = 0  # count number of iterations
        start.opened = True

        open_list = [start]

        while len(open_list) > 0:
            self.runs += 1
            self.keep_running()

            path = self.check_neighbors(start, end, grid, open_list)
            if path:
                return path, self.runs

        # failed to find path
        return [], self.runs
