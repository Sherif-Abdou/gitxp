import React, { useEffect, useState } from 'react';
import { getRepos } from './api/api';
import './Repos.css'

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
        <div className="repo-container">
            <h2>Your Repositories</h2>
            {repos.map((repo) => (
                <div className="repo-box" key={repo.name}>
                <strong>{repo.name}</strong>
                <div className="repo-grid">
                    <div>⭐ Stars: {repo.stars}</div>
                    <div>🔁 Commits: {repo.commits}</div>
                    <div>🧩 Issues: {repo.issues}</div>
                    <div>🐛 Open Issues: {repo.open_issues}</div>
                    <div>📦 PRs: {repo.prs}</div>
                    <div>🍴 Forks: {repo.forks}</div>
                    <div>👥 Contributors: {repo.contributors}</div>
                    <div>👀 Watchers: {repo.watchers}</div>
                </div>
                </div>
            ))}
        </div>
    );
};

export default RepoTab;
