import requests
import json
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()

url = "https://api.github.com/orgs/adobe/repos"
headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

response = requests.get(url, headers=headers)
data = response.json()

# Go through each repo in the org, print its stars, watches, and forks

for repo in data:
    print("Repo Name: ", repo["name"])
    print("Description: ", repo["description"])
    print("Stars: ", repo["stargazers_count"])
    print("Forks: ", repo["forks_count"])
    print("Watchers: ", repo["watchers_count"])
    print("Open Issues: ", repo["open_issues_count"])
    print('---------------------------------')