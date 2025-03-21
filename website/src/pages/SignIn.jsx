import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { Link } from "react-router-dom";

const SignIn = () => {
  const handleLogin = async (response) => {
    const { credential } = response;
    try {
      // Send the Google OAuth token to your backend for authentication
      const res = await fetch("http://localhost:8000/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ access_token: credential }), // Send the token to your backend
      });

      if (res.ok) {
        const data = await res.json();
        console.log("Logged in successfully:", data);
        // You can redirect the user or update the UI here
      } else {
        console.error("Login failed:", res.statusText);
      }
    } catch (error) {
      console.error("Error during login:", error);
    }
  };

  return (
    <div className="relative mt-28 px-4">
      {/* Sign In Box Section */}
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto mb-12 p-6">
        <div className="flex flex-col justify-center mt-10 ml-10">
          <h2 className="text-2xl font-bold mb-4">Sign In to Robotouille</h2>
          <p className="mb-6">
            Use your Google account to sign in and start using the app.
          </p>

          {/* Google Sign In Button */}
          <GoogleLogin
            onSuccess={handleLogin}
            onError={() => console.error("Login Failed")}
            useOneTap
            theme="filled_blue" // Optional styling choice
            shape="pill" // Optional styling choice for button shape
            width="100%" // Make the button take full width
          />
        </div>
      </div>
    </div>
  );
};

export default SignIn;
