# -*- coding: utf-8 -*-
import math
from util import SQRT2


def null(dx, dy):
    """
    special heuristic for Dijkstra
    return 0, so node.h will always be calculated as 0,
    distance cost (node.f) is calculated only from
    start to current point (node.g)
    """
    return 0


def manhatten(dx, dy):
    """manhatten heuristics"""
    return dx + dy

def euclidean(dx, dy):
    """euclidean distance heuristics"""
    return math.sqrt(dx * dx + dy * dy)


def octile(dx, dy):
    f = SQRT2 - 1
    if dx < dy:
        return f * dx + dy
    else:
        return f * dy + dx
