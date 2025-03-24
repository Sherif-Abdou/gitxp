interface Event {
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
