import './App.css';
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";
import { PointView } from './PointView';

function App() {
  return (
    <>
      <nav className="navbar">
      <h1>GitXP</h1>
      <div className="card">
        <SignedOut>
          <SignInButton />
        </SignedOut>
        <SignedIn>
          <UserButton />
        </SignedIn>
      </div>
      </nav>
      <PointView />
    </>
  );
}

export default App;
