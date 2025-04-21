import { useClerk } from "@clerk/clerk-react";
import './App.css';

export function CustomSignInButton() {
  const { openSignIn } = useClerk();

  const handleSignInClick = () => {
    // Open the sign-in modal but force GitHub as the only provider
    openSignIn({
      signInUrl: "/sign-in/oauth/github",
    });
  };

  return (
    <button className="custom-signin-button" onClick={handleSignInClick}>
      Sign In with GitHub
    </button>
  );
}