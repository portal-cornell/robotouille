import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { useGoogleLogin } from "@react-oauth/google";
import { Link } from "react-router-dom";
import { useNavigate } from "react-router-dom";
import googlelogo from "../assets/socials/google2.png";

const SignIn = () => {
  const login = useGoogleLogin({
    scope: "openid profile email",
    flow: "implicit",
    onSuccess: async (tokenResponse) => {
      console.log("Google access token:", tokenResponse.access_token);

      try {
        const res = await fetch("http://localhost:8000/api/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ access_token: tokenResponse.access_token }),
        });

        const data = await res.json();
        console.log("Server response:", data);

        if (data.status === "success") {
          alert(`Welcome, ${data.user.name}!`);
          localStorage.setItem("user", JSON.stringify(data.user));
          localStorage.setItem("accessToken", data.access_token);
          navigate("/profile");
        } else {
          alert(`Login failed: ${data.message}`);
        }
      } catch (err) {
        console.error("Login error:", err);
        alert("Failed to connect to backend.");
      }
    },
    onError: (err) => {
      console.error("Login failed:", err);
      alert("Google Sign-In Failed");
    },
  });
  const navigate = useNavigate();
  return (
    <div className="flex items-center justify-center mt-20 mb-24 px-4 pb-20">
      {"          "}
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl w-full max-w-md p-4">
        <div className="bg-white text-black rounded-lg shadow-lg p-10 flex flex-col items-center gap-6">
          <h2 className="text-xl font-semibold text-left w-full px-4">
            Sign In
          </h2>
          <button
            onClick={() => login()}
            className="flex items-center gap-3 bg-red-200 hover:bg-red-300 text-black px-16 py-3 rounded-lg font-roboto transition duration-300"
          >
            <img src={googlelogo} alt="Google logo" className="w-5 h-5" />
            <span>Sign in with Google</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
