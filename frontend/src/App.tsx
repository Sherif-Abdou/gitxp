import './App.css';
import { SetStateAction, useEffect, useState } from 'react';
import { useUser } from '@clerk/clerk-react';
import { getPointEventsForUser } from './api/api.ts';
import { CustomSignInButton } from './ClerkButton';
import { SignedIn, SignedOut, UserButton } from "@clerk/clerk-react";
import { PointView } from './PointView';
import ReposTab from './Repos.tsx';
import { Leaderboard } from './Leaderboard.tsx';
import logoImage from './assets/gitxp.png';

function App() {
  const {isSignedIn, user} = useUser();
  const [totalPoints, setTotalPoints] = useState(0);
  const [activeNav, setActiveNav] = useState('home');

/* This function gets the point events for user */
  useEffect(() => {
    if (isSignedIn && user) {
      const name = user.username || user.firstName;
      if (name !== null) {
      console.log(name);
        /* set total points variable based on the events */
        getPointEventsForUser(name).then(events => {
            const total = events.reduce((sum, ev) => sum + ev.points, 0);
            setTotalPoints(total);
        });
      }
    }
  }, [isSignedIn, user]);

  /* Handle page navigation */
  const handleNavClick = (navItem: SetStateAction<string>) => {
    setActiveNav(navItem);
  };

  /* Show point view if user is not signed in */
  const renderContent = () => {
    if (!user) {
      return <PointView />;
    }
    
    const username = user.username!;

    /* the various pages */
    switch (activeNav) {
      case 'home':
        return <PointView />;
      case 'repos':
        return <ReposTab username={username}/>;
      case 'leaderboard':
        return <Leaderboard />;
      default:
        return <PointView />;
    }
  };

  return (
    <div>
      <nav className="navbar">
        <div className="nav-left">
          <div className="logo-container">
            <img src={logoImage} alt="GitXP Logo" className="logo-image" />
          </div>
          {isSignedIn && (<div className="nav-menu">
            <div 
              className={`nav-item ${activeNav === 'home' ? 'active' : ''}`}
              onClick={() => handleNavClick('home')}
            >
              Home
            </div>
            <div 
              className={`nav-item ${activeNav === 'repos' ? 'active' : ''}`}
              onClick={() => handleNavClick('repos')}
            >
              Repos
            </div>
            <div 
              className={`nav-item ${activeNav === 'leaderboard' ? 'active' : ''}`}
              onClick={() => handleNavClick('leaderboard')}
            >
              Leaderboard
            </div>
          </div>)}
        </div>
        
        <div className="nav-right">
          {isSignedIn && (
            <div className="xp-badge-wrapper">
              <div className="xp_badge">
                <span className="xp_text">⭐ {totalPoints}</span>
              </div>
              <div className="xp-tooltip">
                Make commits, issues, pull requests, or start a new repository to gain points!
              </div>
            </div>
          )}
          <SignedOut>
            <CustomSignInButton />
          </SignedOut>
          <SignedIn>
            <UserButton />
          </SignedIn>
        </div>
      </nav>

      <div className="content-container">
        {renderContent()}
      </div>
    </div>
  );
}

export default App;
