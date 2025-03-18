from typing import Iterable
from database import PointSource
from enum import Enum
from datetime import datetime
from math import log2

def GithubEvent():
    def generate_points(self):
        pass

def CommitEvent(GithubEvent):
    def __init__(self, additions, deletions):
        self.__additions = additions
        self.__deletions = deletions

    def generate_points(self):
        return 0.75 * log2(self.__additions) + 0.25 * log2(self.__deletions)

def OpenIssueEvent(GithubEvent):
    def __init__(self):
        pass

    def generate_points(self):
        return 1

def OpenPullRequestEvent(GithubEvent):
    def __init__(self):
        pass

    def generate_points(self):
        return 8

def ClosePullRequestEvent(GithubEvent):
    def __init__(self, additions, deletions):
        self.__additions = additions
        self.__deletions = deletions

    def generate_points(self):
        return 3.75 * log2(self.__additions) + 1.25 * log2(self.__deletions)

# Calculates the number of days since a given datetime
def days_since(source: datetime):
    return (datetime.now() - source).days

# Attentuates point sources based off of time
def time_attentuation(days):
    if days > 365:
        return 0.0
    return 1.0 / (1.0 + 0.02 * days)

# Accumulates point sources and weights them based off of time
def calculate_points(point_sources: Iterable[PointSource]):
    total_points = 0
    for source in point_sources:
        attentuation = time_attentuation(source.time)
        total_points += source.points * attentuation
    return total_points

