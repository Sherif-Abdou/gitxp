import { useClerk } from "@clerk/clerk-react";
import './App.css';

export function CustomSignInButton() {
  const { openSignIn } = useClerk();

  return (
    <button className="custom-signin-button" onClick={() => openSignIn()}>
      Sign In
    </button>
  );
}