import { useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { getPointEventsForUser, Event } from './api/api.ts';
import "./PointView.css";

export function PointView() {
    const [data, setData] = useState([] as Event[]);
    const { isSignedIn, user, isLoaded } = useUser();

    // Random hi message
    const greetings = ["Howdy", "Welcome back", "Hey", "Hey there", "We've missed you"];
    const [greeting] = useState(() =>
        greetings[Math.floor(Math.random() * greetings.length)]
    );


    useEffect(() => {
        const name = user?.username || user?.firstName || "defaultName";
        getPointEventsForUser(name).then(data => {
            console.log(data);
            setData(data);
        });
    }, [isSignedIn, user]);

    if (!isLoaded) {
        return <div>Loading...</div>; // Clerk loading
    }

    if (!isSignedIn) {
        return (
        <div className="welcome_container">
            <h1 className="welcome_title">Next-level GitHub Visualization</h1>
            <p className="welcome_subtext">Sign in to see your progress and gain XP 🚀</p>
        </div>
        );
    }

    const name = user.firstName?.trim() || user.username?.trim() || "Coder"; // username fallback chain

    const items = data.map(item => (
    <tr className="point_item">
        <td className="point_number"><div className="point_inner">{item.points}</div></td>
        <td className="point_type"><div className="point_inner">{item.point_type}</div></td>
        <td className="point_repo"><div className="point_inner">{item.repository}</div></td>
    </tr>
    ));

    return (
        <>
            <h2 className="greeting wiggle">{greeting}, {name}!</h2>
            <div className="pointlog_container">
                <h3 className="pointlog_title">GitLog</h3>
                <div className="pointlog_scrollbox">
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
                </div>
            </div>
        </>
    );
}
