import React, { useEffect, useState } from 'react';
import { getRepos } from './api/api';

type Repo = {
    name: string;
    stars: number;
    forks: number;
    watchers: number;
    open_issues: number;
    contributors: number;
    commits: number;
    prs: number;
    issues: number;
  };

type Props = {
    username: string;
};

const RepoTab: React.FC<Props> = ({ username }) => {
    const [repos, setRepos] = useState<Repo[]>([]);

    useEffect(() => {
        async function fetchData() {
            const result = await getRepos(username);
            setRepos(result.repositories); // adjust for new payload shape
        }
    
        fetchData();
    }, [username]);

    return (
        <div>
        <h2>Your Repositories</h2>
        <ul>
            {repos.map((repo) => (
            <li key={repo.name}>
            <strong>{repo.name}</strong><br />
            ⭐ Stars: {repo.stars}<br />
            🍴 Forks: {repo.forks}<br />
            👀 Watchers: {repo.watchers}<br />
            🐛 Open Issues: {repo.open_issues}<br />
            👥 Contributors: {repo.contributors}<br />
            🔁 Commits: {repo.commits}<br />
            📦 PRs: {repo.prs}<br />
            🧩 Issues: {repo.issues}
          </li>
            ))}
        </ul>
        </div>
    );
};

export default RepoTab;
