import requests
import json
from dotenv import load_dotenv
import os
import points
import database
from datetime import datetime


# load environment variables
load_dotenv()

# url = "https://api.github.com/repos/danushsingla/PantryTracker/commits"
url = "https://api.github.com/users/danushsingla/events"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}


# def get_user_events(url):
#     response = requests.get(url, headers=headers)
#     data = response.json()
#
#     point_events = []
#     
#     for event in data:
#         event_type = event["type"]
#         repo_name = event["repo"]["name"]
#         date_time = event["created_at"][:-1].split("T")
#         time = datetime.strptime(f"{str(date_time[1])} {str(date_time[0])}","%H:%M:%S %Y-%m-%d") 
#
#         if event["type"] == "PushEvent":
#             for commit in event["payload"]["commits"]:
#                 commit_url = commit["url"]
#                 commit_response = requests.get(commit_url, headers=headers)
#                 commit_data = commit_response.json()
#     
#                 added = 0
#                 removed = 0
#                 modified = 0
#     
#                 # Print count of files added, changed, and deleted
#                 for file in commit_data["files"]:
#                     # Keep track of count for additions, modifications, and deletions
#                     if(file["status"] == "added"):
#                         added += file["additions"]
#                     elif(file["status"] == "modified"):
#                         modified += file["changes"]
#                     elif(file["status"] == "removed"):
#                         removed += file["deletions"]
#
#                 commit_event = points.CommitEvent(added + modified, removed)
#                 commit_event.repo = repo_name
#                 commit_event.timestamp = time
#                 point_events.append(commit_event)
#         elif event["type"] == "CreateEvent":
#             issue = points.OpenIssueEvent()
#             issue.repo = repo_name
#             issue.timestamp = time
#             point_events.append(issue);
#         elif event["type"] == "IssuesEvent":
#             issue = points.OpenIssueEvent()
#             issue.repo = repo_name
#             issue.timestamp = time
#             point_events.append(issue);
#         elif event["type"] == "IssueCommentEvent":
#             issue = points.OpenIssueEvent()
#             issue.repo = repo_name
#             issue.timestamp = time
#             point_events.append(issue);
#     return point_events

def get_user_events(username):
    url = f"https://api.github.com/users/{username}/events"
    response = requests.get(url, headers=headers)
    data = response.json()

    point_events = []
    
    for event in data:
        event_type = event["type"]
        repo_name = event["repo"]["name"]
        date_time = event["created_at"][:-1].split("T")
        time = datetime.strptime(f"{str(date_time[1])} {str(date_time[0])}","%H:%M:%S %Y-%m-%d") 

        if event["type"] == "PushEvent":
            for commit in event["payload"]["commits"]:
                commit_url = commit["url"]
                commit_response = requests.get(commit_url, headers=headers)
                commit_data = commit_response.json()
    
                added = 0
                removed = 0
                modified = 0
    
                if "files" in commit_data:
                    # Print count of files added, changed, and deleted
                    for file in commit_data["files"]:
                        # Keep track of count for additions, modifications, and deletions
                        if(file["status"] == "added"):
                            added += file["additions"]
                        elif(file["status"] == "modified"):
                            modified += file["changes"]
                        elif(file["status"] == "removed"):
                            removed += file["deletions"]

                commit_event = points.CommitEvent(added + modified, removed)
                commit_event.repo = repo_name
                commit_event.timestamp = time
                point_events.append(commit_event)
        elif event["type"] == "IssuesEvent":
            issue = points.OpenIssueEvent()
            issue.repo = repo_name
            issue.timestamp = time
            point_events.append(issue);
        elif event["type"] == "IssueCommentEvent":
            issue = points.OpenIssueEvent()
            issue.repo = repo_name
            issue.timestamp = time
            point_events.append(issue);
        elif event["type"] == "CreateEvent":
            issue = points.CreateRepoEvent()
            issue.repo = repo_name
            issue.timestamp = time
            point_events.append(issue);
        elif event["type"] == "PullRequestEvent":
            pr = points.OpenPullRequestEvent()
            pr.repo = repo_name
            pr.timestamp = time
            point_events.append(pr);
    return point_events

def get_repos(username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}
    response = requests.get(url, headers=headers)
    data = response.json()

    repositories = []

    for repo in data:
        name = repo["name"]
        stars = int(repo["stargazers_count"])
        forks = int(repo["forks_count"])
        watchers = int(repo["watchers_count"])
        open_issues = int(repo["open_issues_count"])

        repositories.append(database.Repository(name=name, stars=stars, forks=forks, watchers=watchers, open_issues=open_issues))

    return repositories

# get_recent_events(url)
