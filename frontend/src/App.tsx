import './App.css';
import { useEffect, useState } from 'react'
import { useUser } from '@clerk/clerk-react'
import { getPointEventsForUser} from './api/api.ts';
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { PointView } from './PointView';
import logoImage from './assets/gitxp.png';

function App() {
  const {isSignedIn, user} = useUser();
  const [totalPoints, setTotalPoints] = useState(0);

  useEffect(() => {
    if (isSignedIn && user) {
      const name = user.username || user.firstName || "defaultName";
      getPointEventsForUser(name).then(events => {
        const total = events.reduce((sum, ev) => sum + ev.points, 0);
        setTotalPoints(total);
      });
    }
  }, [isSignedIn, user]);

  return (
    <div>
      <nav className="navbar">
        <div className="nav-left">
          <div className="logo-container">
            <img src={logoImage} alt="GitXP Logo" className="logo-image" />
          </div>
        </div>
        
        {isSignedIn && (
          <div className="xp_badge">
            <span className="xp_text">⭐ {totalPoints} XP</span>
          </div>
        )}

        <div className="nav-right">
          <SignedOut>
            <SignInButton />
          </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
      </nav>
      <PointView />
    </div>
  );
}

export default App;
