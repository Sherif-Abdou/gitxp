interface Event {
    points: number,
    point_type: string,
    repository: string,
}


export function getPointEventsForUser(user: string): Promise<Event[]> {
    return fetch(`127.0.0.1:5000/${user}/point_list`)
        .then(data => data.json());
}
