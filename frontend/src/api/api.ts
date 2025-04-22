export interface Event {
    points: number,
    point_type: string,
    repository: string,
}

/* This interface is used to represent the information of a repository. Makes life simpler */
export interface RepoInfo {
    name: string;
    stars: number;
    watchers: number;
    open_issues: number;
    forks: number;
    contributors: number;
    commits: number;
    prs: number;
    issues: number;
}
  
export interface UserRepoResponse {
    user: string;
    repositories: RepoInfo[];
}

/* This function gets the point events for user */
export async function getPointEventsForUser(user: string): Promise<Event[]> {
    try {
        const data = await fetch(`http://127.0.0.1:5000/users/${user}/point_list`);
        return await data.json();
    } catch (e) {
        console.error(`Error loading user data: ${e}`);
        return await Promise.resolve([]);
    }
}

/* This function gets leaderboard stats */
export async function getLeaderboard(): Promise<[string, number][]> {
    try {
        const data = await fetch(`http://127.0.0.1:5000/leaderboard`);
        return await data.json();
    } catch (e) {
        console.error(`Error loading user data: ${e}`);
        return await Promise.resolve([]);
    }
}

/* This function gets repos based on rankings */
export async function getRepos(user: string, sorted: string = 'popularity') : Promise<UserRepoResponse> {
    try {
        if (sorted === 'oldest') {
            const response = await fetch(`http://127.0.0.1:5000/users/${user}/repositories/info/oldest`);
            if (!response.ok) {
                throw new Error('Failed to fetch repository data');
            }
            console.log(response);
            return await response.json();
        }
        if (sorted === 'activity') { /* Needs a new path */
            const response = await fetch(`http://127.0.0.1:5000/users/${user}/repositories/info/activity`);
            if (!response.ok) {
                throw new Error('Failed to fetch repository data');
            }
            console.log(response);
            return await response.json();
        }
        // Default sort by popularity
        const response = await fetch(`http://127.0.0.1:5000/users/${user}/repositories/info/popular`);
        if (!response.ok) {
            throw new Error('Failed to fetch repository data');
        }
        console.log(response);
        return await response.json();

    } catch (error) {
        console.error('Error getting repositories:', error);
        return { user: "", repositories: [] };
    }
}
