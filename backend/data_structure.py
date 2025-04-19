import requests
import os
import time
from datetime import datetime, timezone
from dotenv import load_dotenv

class Commit:
    def __init__(self, message, date, name, url):
        self.message = message
        self.date = date
        self.name = name
        self.url = url

    # Get additions, deletions, and changes as stats
    def get_stats(self):
        headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

        commit_response = requests.get(self.url, headers=headers)
        commit_data = commit_response.json()

        added = 0
        removed = 0
        modified = 0
        files = len(commit_data["files"])

        # Print count of files added, changed, and deleted
        for file in commit_data["files"]:
            # Keep track of count for additions, modifications, and deletions
            if(file["status"] == "added"):
                added += 1
            elif(file["status"] == "modified"):
                modified += 1
            elif(file["status"] == "removed"):
                removed += 1

        return added, modified, removed, files
    
    def get_score(self):
        # Get additions, deletions, and changes as stats
        added, modified, removed, files = self.get_stats()

        # Recency (in seconds since commit)
        commit_time = datetime.strptime(self.date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
        now = time.time()
        age_in_seconds = now - commit_time

        # Exponential decay to get recency score
        recency_score = 1 / (1 + age_in_seconds / (60 * 60 * 24))  # Decay over days

        # Total lines affected
        changes = added + modified + removed

        # Calculate score based on the number of lines changed
        score = changes + files + (recency_score * 100)
        return score
    
class Repo:
    def __init__(self, name, description, stars, forks, watchers, open_issues, 
                 last_updated,
                 last_updated_timestamp,
                 commits_url,
                 popularity_score):
        self.name = name
        self.description = description
        self.stars = stars
        self.forks = forks
        self.watchers = watchers
        self.open_issues = open_issues
        self.last_updated = last_updated
        self.last_updated_timestamp = last_updated_timestamp
        self.commits_url = commits_url
        self.commits = []
        self.contributors = []
        self.popularity_score = popularity_score

        self.store_commits()

        self.activity_score = self.get_activity_score()

    def store_commits(self):
        contributors_temp = set()
        headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}

        # Rather than accessing collaborators, which is private information, get contributors from past commits
        commits_response = requests.get(self.commits_url, headers=headers)
        commits_data = commits_response.json()

        for commit in commits_data:
            if commit["author"] is not None:
                if commit["author"]["login"] not in contributors_temp:
                    contributors_temp.add(commit["author"]["login"])
            if commit["committer"] is not None:
                if commit["committer"]["login"] not in contributors_temp:
                    contributors_temp.add(commit["committer"]["login"])
        self.contributors = list(contributors_temp)

        # Store commit messages, dates, and authors in the commits list
        for commit in commits_data:
            commit_object = Commit(commit["commit"]["message"],
                                   commit["commit"]["author"]["date"],
                                    commit["commit"]["author"]["name"],
                                    commit["url"])
            self.commits.append(commit_object)

    def get_prs_score(self):
        # Add all additions, deletions, changes, commits for each pull request, average them, and decay over time
        # Get pull request data from GitHub API
        headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}
        prs_url = f"https://api.github.com/repos/{self.name}/pulls?state=all&per_page=5"
        prs_response = requests.get(prs_url, headers=headers)
        prs_data = prs_response.json()

        score = 0
        len(prs_data) # Number of pull requests

        index = 0

        for prs in prs_data:
            # Get number of commits, files changed, and lines added/deleted for each pull request
            prs_specific_url = prs["url"]
            prs_specific_response = requests.get(prs_specific_url, headers=headers)
            prs_specific_data = prs_specific_response.json()

            additions = prs_specific_data["additions"]
            deletions = prs_specific_data["deletions"]
            changed_files = prs_specific_data["changed_files"]
            commits = prs_specific_data["commits"]
            
            changes = additions + deletions + changed_files + commits

            # Recency (in seconds since commit)
            pull_request_time = datetime.strptime(prs["updated_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
            now = time.time()
            age_in_seconds = now - pull_request_time

            # Exponential decay to get recency score
            recency_score = 1 / (1 + age_in_seconds / (60 * 60 * 24))  # Decay over days

            # Calculate score
            score += (changes + (recency_score * 100))

            index += 1
            if index == 5:
                break
        
        average_score = 0

        if len(prs_data) == 0:
            average_score = 0
        elif len(prs_data) > 0 and len(prs_data) < 5:
            average_score = score / len(prs_data)
        else:
            # Get average score for first 100 pull requests
            average_score = score / 5

        return average_score

    def get_issues_score(self):
        # Just return total number of issues
        # Get issues data from GitHub API
        headers = {"Authorization": f"token {os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')}"}
        issues_url = f"https://api.github.com/repos/{self.name}/issues?state=all"
        issues_response = requests.get(issues_url, headers=headers)
        issues_data = issues_response.json()
        return len(issues_data)

    def get_activity_score(self):
        # Calculate the activity score based on the number of commits and their recency ( get first 100 only)
        total_score = 0
        index = 0
        for commit in self.commits:
            total_score += commit.get_score()
            if index == 10:
                break
            index += 1

        average_commit_score = 0

        if (len(self.commits) == 0):
            average_commit_score = 0
        elif (len(self.commits) > 0 and len(self.commits) < 10):
            average_commit_score = total_score / len(self.commits)
        else:
            average_commit_score = total_score / 10

        print("Average Commit Score: ", average_commit_score)

        # Get activity score from pull requests
        pull_request_score = self.get_prs_score()

        print("Pull Request Score: ", pull_request_score)

        # Get activity score from issues
        issues_score = self.get_issues_score()

        print("Issues Score: ", issues_score)

        # Combine all scores
        total_score = (average_commit_score * 0.7) + (pull_request_score * 0.2) + (issues_score * 0.1)
        return total_score

class Repos:
    def __init__(self):
        self.repos = []

        # Provide weightage for each metric
        self.stars_weight = 0.4
        self.forks_weight = 0.3
        self.watches_weight = 0.2
        self.issues_weight = 0.1

    def add_repo(self, repo):
        popularity_score = (repo["stargazers_count"] * self.stars_weight +
                repo["forks_count"] * self.forks_weight +
                repo["watchers_count"] * self.watches_weight +
                repo["open_issues_count"] * self.issues_weight)
        
        # Convert the last updated date to a datetime object
        last_updated = datetime.strptime(repo["updated_at"], "%Y-%m-%dT%H:%M:%SZ")

        # Set date to UTC and convert to Unix timestamp
        last_updated_timestamp = last_updated.replace(tzinfo=timezone.utc).timestamp()

        repo_object =  Repo(repo["full_name"],
                            repo["description"],
                            repo["stargazers_count"],
                            repo["forks_count"],
                            repo["watchers_count"],
                            repo["open_issues_count"],
                            last_updated,
                            last_updated_timestamp,
                            repo["commits_url"][:-6],
                            popularity_score)

        self.repos.append(repo_object)

    def get_repos(self):
        return self.repos

    def get_repo_by_name(self, name):
        for repo in self.repos:
            if repo.name == name:
                return repo
        return None

    def get_all_contributors(self):
        contributors = set()
        for repo in self.repos:
            contributors.update(repo.contributors)
        return list(contributors)
    
    def get_all_commits(self):
        all_commits = []
        for repo in self.repos:
            all_commits.extend(repo.commits)
        return all_commits
    
    def get_popular_repos_ranked(self):
        # Sort repos by popularity score in descending order
        sorted_repos = sorted(self.repos, key=lambda x: x.popularity_score, reverse=True)
        return sorted_repos
    
    def get_old_repos_ranked(self):
        # Sort repos by last updated date in ascending order
        sorted_repos = sorted(self.repos, key=lambda x: x.last_updated_timestamp)
        return sorted_repos
    
    def get_active_repos_ranked(self):
        # Sort repos by activity score in descending order
        sorted_repos = sorted(self.repos, key=lambda x: x.activity_score, reverse=True)
        return sorted_repos