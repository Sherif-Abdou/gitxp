from typing import Iterable
from typing_extensions import override
from datetime import datetime
from math import log2

# This class is the base class for all Github events.
class GithubEvent():
    def __init__(self):
        self.timestamp = datetime.now()
        self.repo = ""

    def generate_points(self):
        return 0.0

# Commit, store additions and deletions and generate points from them
class CommitEvent(GithubEvent):
    def __init__(self, additions, deletions):
        super().__init__()
        self.__additions = additions
        self.__deletions = deletions

    def generate_points(self):
        return 0.75 * log2(max(self.__additions, 1)) + 0.25 * log2(max(self.__deletions, 1))

# Open issues, just return 1
class OpenIssueEvent(GithubEvent):
    def __init__(self):
        pass

    def generate_points(self):
        return 1

# Open PR, just return 8
class OpenPullRequestEvent(GithubEvent):
    def __init__(self):
        pass

    def generate_points(self):
        return 8

# Create repo, just return 4
class CreateRepoEvent(GithubEvent):
    def __init__(self):
        super().__init__()
        pass
    def generate_points(self):
        return 4

# Close PR, return based on additions and deletions
class ClosePullRequestEvent(GithubEvent):
    def __init__(self, additions, deletions):
        self.__additions = additions
        self.__deletions = deletions

    def generate_points(self):
        return 3.75 * log2(max(self.__additions, 1)) + 1.25 * log2(max(self.__deletions, 1))

# Calculates the number of days since a given datetime
def days_since(source: datetime):
    return (datetime.now() - source).days

# Attentuates point sources based off of time
def time_attentuation(days):
    if days > 365:
        return 0.0
    return 1.0 / (1.0 + 0.0075 * days)

# Accumulates point sources and weights them based off of time
def calculate_points(point_sources):
    total_points = 0
    for source in point_sources:
        attentuation = time_attentuation(days_since(source.time))
        total_points += round(100 * source.points * attentuation)
    return total_points

