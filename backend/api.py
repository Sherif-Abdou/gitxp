import requests
import json
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

# url = "https://api.github.com/repos/danushsingla/PantryTracker/commits"
url = "https://api.github.com/users/sherif-abdou/events?per_page=50"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

response = requests.get(url, headers=headers)
data = response.json()

with open("response.txt", "w") as file:
    file.write(json.dumps(data, indent=4))

# Iterate through each event in data
for event in data:
    print("Event Type: ", event["type"])
    print("Repo: ", event["repo"]["name"])
    date_time = event["created_at"][:-1].split("T")
    print("Date: ", date_time[1], date_time[0])

    # We can use reaction total count to calculate points
    if event["type"] == "IssueCommentEvent":
        print("Title: ", event["payload"]["issue"]["title"])
        print("Issue: ", event["payload"]["issue"]["body"])
        print("Comment: ", event["payload"]["comment"]["body"])
        print("Reactions: ", event["payload"]["comment"]["reactions"]['total_count'])
    if event["type"] == "IssuesEvent":
        print("Action: ", event["payload"]["action"])
        print("Title: ", event["payload"]["issue"]["title"])
        print("Issue: ", event["payload"]["issue"]["body"])
    if event["type"] == "PushEvent":
        print("Number of Commits: ", event["payload"]["size"])
        for commit in event["payload"]["commits"]:
            print("Commit Message: ", commit["message"])

            # Grab commit URL to get total files/lines changed
            commit_url = commit["url"]
            commit_response = requests.get(commit_url, headers=headers)
            commit_data = commit_response.json()

            added = 0
            removed = 0
            modified = 0

            # Print count of files added, changed, and deleted
            for file in commit_data["files"]:
                print("File: ", file["filename"])
                print("Additions: ", file["additions"])
                print("Deletions: ", file["deletions"])
                print("Changes: ", file["changes"])

                # Keep track of count for additions, modifications, and deletions
                if(file["status"] == "added"):
                    added += 1
                elif(file["status"] == "modified"):
                    modified += 1
                elif(file["status"] == "removed"):
                    removed += 1
                
            print("Total Files Added: ", added)
            print("Total Files Modified: ", modified)
            print("Total Files Removed: ", removed)
    if event["type"] == "PullRequestEvent":
        print("Action: ", event["payload"]["action"])
        print("Title: ", event["payload"]["pull_request"]["title"])
        print("Body: ", event["payload"]["pull_request"]["body"])
        print("Reactions: ", event["payload"]["pull_request"]["reactions"]['total_count'])
    if event["type"] == "PullRequestReviewEvent":
        print("Action: ", event["payload"]["action"])
        print("Review State: ", event["payload"]["review"]["state"])
        print("Body: ", event["payload"]["review"]["body"])
        print("Reactions: ", event["payload"]["review"]["reactions"]['total_count'])

        # Print info about the pull request
        print("Title: ", event["payload"]["pull_request"]["title"])
        print("Body: ", event["payload"]["pull_request"]["body"])
    if event["type"] == "PullRequestReviewCommentEvent":
        print("Action: ", event["payload"]["comment"]["action"])
        print("Comment: ", event["payload"]["comment"]["body"])
        print("Reactions: ", event["payload"]["comment"]["reactions"]['total_count'])

        # Print info about the pull request
        print("Title: ", event["payload"]["pull_request"]["title"])
        print("Body: ", event["payload"]["pull_request"]["body"])
    if event["type"] == "PullRequestReviewThreadEvent":
        # resolved or unresolved
        print("Action: ", event["payload"]["action"])
        print("Comment: ", event["payload"]["comment"]["body"])
        print("Reactions: ", event["payload"]["comment"]["reactions"]['total_count'])

        # Print info about the pull request
        print("Title: ", event["payload"]["pull_request"]["title"])
        print("Body: ", event["payload"]["pull_request"]["body"])
    print('---------------------------------')
# print(data[0])


# Based on recent user activity, get user information, each date, repo name, type of event, and metadata for event (ex. files changed for commit)
# See how far back user activity can get pulled
