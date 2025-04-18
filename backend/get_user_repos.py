from data_structure import Repo, Commit, Repos
import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

# Set github username value, fill with Clerk credentials
github_username = "danushsingla"

# Sift through the repos of the user (just public) and store data in class structure
repos = Repos()

url = f"https://api.github.com/users/{github_username}/repos"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

response = requests.get(url, headers=headers)
data = response.json()

for repo in data:
    # Simply send to Repos class that will take care of everything
    repos.add_repo(repo)

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