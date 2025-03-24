import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { useUser } from '@clerk/clerk-react'
import { getPointEventsForUser, Event } from './api/api.ts';
import "./PointView.css"

export function PointView() {
    const [data, setData] = useState([] as Event[]);
    const { isSignedIn, user, isLoaded } = useUser();


    useEffect(() => {
        const name = "sherif";
        getPointEventsForUser(name).then(data => {
            console.log(data);
            setData(data);
        });
    }, [isSignedIn]);


    if (!isSignedIn) {
        return (<div>
                Please sign in to see points
                </div>);
    }
    const items = data.map(item =>
    (<tr className="point_item">
     <td className="point_number">{item.points}</td>
     <td className="point_type">{item.point_type.toUpperCase()}</td>
     <td className="point_repo">{item.repository}</td>
    </tr>)
    );
    return (
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
    );
}
