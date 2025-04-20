export interface Event {
    points: number,
    point_type: string,
    repository: string,
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

export async function getRepos(username: string) {
    try {
      const [pointsResponse, metadataResponse] = await Promise.all([
        fetch(`http://localhost:5000/users/${username}/repositories`),
        fetch(`http://localhost:5000/repositories`)
      ]);
  
      if (!pointsResponse.ok || !metadataResponse.ok) {
        throw new Error('Failed to fetch repository data');
      }
  
      const pointsData = await pointsResponse.json();
      const metadata = await metadataResponse.json();
  
      const enriched = metadata.map((repo: any) => ({
        ...repo,
        points: pointsData.repositories[repo.name] || 0
      }));
  
      return enriched;
    } catch (error) {
      console.error('Error enriching repositories:', error);
      return [];
    }
  }
