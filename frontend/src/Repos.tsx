import React, { useEffect, useState } from 'react';
import { getRepos } from './api/api';

type Repo = {
    name: string;
    stars: number;
    forks: number;
    watchers: number;
    open_issues: number;
    points: number;
};

type Props = {
    username: string;
};

const RepoTab: React.FC<Props> = ({ username }) => {
    const [repos, setRepos] = useState<Repo[]>([]);

    useEffect(() => {
        async function fetchData() {
        const result = await getRepos(username);
        setRepos(result);
        }

        fetchData();
    }, [username]);

    return (
        <div>
        <h2>Your Repositories</h2>
        <ul>
            {repos.map((repo) => (
            <li key={repo.name}>
                <strong>{repo.name}</strong> - ⭐ {repo.stars}, 🍴 {repo.forks}, 👀 {repo.watchers}, 🐛 {repo.open_issues}, 🔢 Points: {repo.points}
            </li>
            ))}
        </ul>
        </div>
    );
};

export default RepoTab;
