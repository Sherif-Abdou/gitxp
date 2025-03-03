import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import { useUser } from '@clerk/clerk-react'
import { getPointEventsForUser } from './api/api.ts';

export function PointView() {
    const [data, setData] = useState([] as Event[]);
    const {isSignedIn, user, isLoaded} = useUser();

    if (!isSignedIn) {
        return (<div></div>);
    }

    useEffect(() => {
        const name = "tester";
        getPointEventsForUser(name).then(data => {
            console.log(data);
            setData(data);
        });
    }, [isSignedIn]);


    return (
        <div>
        </div>
    );
}
