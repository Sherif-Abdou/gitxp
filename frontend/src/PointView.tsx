import { useEffect, useState } from 'react'
import { useUser } from '@clerk/clerk-react'
import { getPointEventsForUser, Event } from './api/api.ts';
import "./PointView.css"

export function PointView() {
    const [data, setData] = useState([] as Event[]);
    const { isSignedIn, user, isLoaded } = useUser();

    // Random hi message
    const greetings = ["Howdy", "Welcome back", "Hey", "Hey there", "We've missed you"];
    const [greeting] = useState(() =>
        greetings[Math.floor(Math.random() * greetings.length)]
    );

    useEffect(() => {
        const name = "sherif";
        getPointEventsForUser(name).then(data => {
            console.log(data);
            setData(data);
        });
    }, [isSignedIn]);

    if (!isLoaded) {
        return <div>Loading...</div>; // Clerk loading
    }

    if (!isSignedIn) {
        return (
        <div className="welcome_container">
            <h1 className="welcome_title">Next-level GitHub Visualization</h1>
            <p className="welcome_subtext">Please sign in to see your progress and gain XP 🚀</p>
        </div>
        );
    }

    const name = user.firstName?.trim() || user.username?.trim() || ""; // username fallback chain

    const items = data.map(item =>
    (<tr className="point_item">
     <td className="point_number">{item.points}</td>
     <td className="point_type">{item.point_type.toUpperCase()}</td>
     <td className="point_repo">{item.repository}</td>
    </tr>)
    );
    return (
        <>
            <h2 className="greeting wiggle">{greeting}, {name}!</h2>
            <table className="point_view">
                <thead>
                <tr>
                    <th>Points</th>
                    <th>Point Type</th>
                    <th>Repository</th>
                </tr>
                </thead>
                <tbody>
                {items}
                </tbody>
            </table>
        </>
    );
}
