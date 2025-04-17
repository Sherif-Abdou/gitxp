import requests
import json
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

url = "https://api.github.com/users/danushsingla/repos"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

response = requests.get(url, headers=headers)
data = response.json()

# Print each repo name, stats, and collaborators

for repo in data:
    print("Repo Name: ", repo["name"])
    print("Stars: ", repo["stargazers_count"])
    print("Forks: ", repo["forks_count"])
    print("Watchers: ", repo["watchers_count"])
    print("Open Issues: ", repo["open_issues_count"])

    contributors = set()

    # Rather than accessing collaborators, which is private information, get contributors from past commits
    commits_url = repo["commits_url"][:-6]
    commits_response = requests.get(commits_url, headers=headers)
    commits_data = commits_response.json()

    for commit in commits_data:
        if commit["author"] is not None:
            if commit["author"]["login"] not in contributors:
                contributors.add(commit["author"]["login"])
        if commit["committer"] is not None:
            if commit["committer"]["login"] not in contributors:
                contributors.add(commit["committer"]["login"])
    
    print("Contributors: ", contributors)
    print('---------------------------------')
