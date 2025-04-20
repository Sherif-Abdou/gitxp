export interface Event {
    points: number,
    point_type: string,
    repository: string,
}
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


export async function getPointEventsForUser(user: string): Promise<Event[]> {
    try {
        const data = await fetch(`http://127.0.0.1:5000/users/${user}/point_list`);
        return await data.json();
    } catch (e) {
        console.error(`Error loading user data: ${e}`);
        return await Promise.resolve([]);
    }
}

export async function getLeaderboard(): Promise<[string, number][]> {
    try {
        const data = await fetch(`http://127.0.0.1:5000/leaderboard`);
        return await data.json();
    } catch (e) {
        console.error(`Error loading user data: ${e}`);
        return await Promise.resolve([]);
    }
}

export async function getRepos(user: string) : Promise<UserRepoResponse> {
    try {
      const response = await fetch(`http://127.0.0.1:5000/users/${user}/repositories/info`);
  
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
