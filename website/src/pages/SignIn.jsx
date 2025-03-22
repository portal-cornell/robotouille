import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { Link } from "react-router-dom";
import googleLogo from "../assets/socials/google.png";
const SignIn = () => {
  return (
    <div className="flex items-center justify-center mt-20 mb-12 px-4">
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl w-full max-w-md p-6">
        <div className="bg-white text-black rounded-lg shadow-lg p-8 flex flex-col items-center gap-6">
          <h2 className="text-2xl font-semibold">Sign In</h2>
          <GoogleLogin
            onSuccess={(credentialResponse) => {
              console.log("Google Sign-In Success:", credentialResponse);
            }}
            onError={() => {
              console.log("Google Sign-In Failed");
            }}
          />
          {/* <button
            // onClick={() => login()}
            className="flex items-center gap-3 bg-white border border-gray-300 text-black px-4 py-2 rounded-lg shadow hover:bg-gray-100 transition"
          >
            <img src={googleLogo} alt="Google" className="w-5 h-5" />
            <span>Sign in with Google</span>
          </button> */}

          <p className="text-sm text-gray-600">
            Don’t have an account?{" "}
            <Link to="/signup" className="text-primary-darkRed hover:underline">
              Sign Up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
