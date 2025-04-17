import requests
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
from data_structure import Repo, Commit, Repos

# load environment variables
load_dotenv()

url = "https://api.github.com/orgs/adobe/repos"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

response = requests.get(url, headers=headers)
data = response.json()

# Go through each repo in the org, print its stars, watches, and forks
# for repo in data:
#     print("Repo Name: ", repo["name"])
#     print("Description: ", repo["description"])
#     print("Stars: ", repo["stargazers_count"])
#     print("Forks: ", repo["forks_count"])
#     print("Watchers: ", repo["watchers_count"])
#     print("Open Issues: ", repo["open_issues_count"])
#     print('---------------------------------')

# Provide weightage for each metric
# stars_weight = 0.4
# forks_weight = 0.3
# watches_weight = 0.2
# issues_weight = 0.1

repos = Repos()

# Calculate the score for each repo
for repo in data:
    # Simply send to Repos class that will take care of everythin
    repos.add_repo(repo)

# print("Popularity Rank:")
# for repo in repos.get_popular_repos_ranked():
#     print(f"Repo Name: {repo.name}")
#     print(f"Description: {repo.description}")
#     print(f"Stars: {repo.stars}")
#     print(f"Forks: {repo.forks}")
#     print(f"Watchers: {repo.watchers}")
#     print(f"Open Issues: {repo.open_issues}")
#     print(f"Last Updated: {repo.last_updated}")
#     print(f"Popularity Score: {repo.popularity_score}")
#     # print(f"Activity Score: {repo.get_activity_score()}")
#     print('---------------------------------')

# print("Oldest Repos:")
# for repo in repos.get_old_repos_ranked():
#     print(f"Repo Name: {repo.name}")
#     print(f"Description: {repo.description}")
#     print(f"Stars: {repo.stars}")
#     print(f"Forks: {repo.forks}")
#     print(f"Watchers: {repo.watchers}")
#     print(f"Open Issues: {repo.open_issues}")
#     print(f"Last Updated: {repo.last_updated}")
#     print(f"Popularity Score: {repo.popularity_score}")
#     print('---------------------------------')

print("Most Active Repos:")
for repo in repos.get_active_repos_ranked():
    print(f"Repo Name: {repo.name}")
    print(f"Description: {repo.description}")
    print(f"Stars: {repo.stars}")
    print(f"Forks: {repo.forks}")
    print(f"Watchers: {repo.watchers}")
    print(f"Open Issues: {repo.open_issues}")
    print(f"Last Updated: {repo.last_updated}")
    print(f"Popularity Score: {repo.popularity_score}")
    print(f"Activity Score: {repo.activity_score}")
    print('---------------------------------')
