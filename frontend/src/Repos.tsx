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
    const [sortBy, setSortBy] = useState<string>('popularity'); // Default sorting is by popularity

    const handleSortChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        setSortBy(event.target.value);
    };

    useEffect(() => {
        async function fetchData() {
            const result = await getRepos(username, sortBy);
            setRepos(result.repositories); // adjust for new payload shape
        }
    
        fetchData();
    }, [username, sortBy]);

    return (
        <div className="repo-container">
            <div className="repo-header">
                <h2>Your Repositories</h2>
                <select className="sort-dropdown" value={sortBy} onChange={handleSortChange}>
                    <option value="popularity">Popularity</option>
                    <option value="oldest">Oldest</option>
                    <option value="activity">Activity</option>
                </select>
            </div>
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
