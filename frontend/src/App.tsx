import { useState } from 'react';
import reactLogo from './assets/react.svg';
import viteLogo from './assets/vite.svg';
import './App.css';
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/clerk-react";

function App() {
  const [count, setCount] = useState(0);
  const [prev, setPrev] = useState(1);

  const handleClick = () => {
    setCount((current) => {
      const nextFib = current + prev;
      setPrev(current);
      return nextFib;
    });
  };

  return (
    <>
      {/* Authentication Header */}
      <header>
        <SignedOut>
          <SignInButton />
        </SignedOut>
        <SignedIn>
          <UserButton />
        </SignedIn>
      </header>

      <div>
        <a href="https://vite.dev" target="_blank" rel="noreferrer">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank" rel="noreferrer">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>GitXP</h1>
      <div className="card">
        <button onClick={handleClick}>
          count is {count}
        </button>
        <p>
          Click for the next Fibonacci number!
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos for documentation
      </p>
    </>
  );
}

export default App;
