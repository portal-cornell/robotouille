import React, { useEffect, useState } from "react";
import header from "../assets/profileHeader.png";
import { useNavigate } from "react-router-dom";
import tmp from "../assets/tempProfilePic.png";

const Profile = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();
  const [newPicture, setNewPicture] = useState("");
  const [newUsername, setNewUsername] = useState("");

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("accessToken");
    window.dispatchEvent(new Event("storage")); // notify Header
    setUser(null);
    navigate("/");
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  if (!user) {
    return <div className="text-center mt-20 text-lg">Loading...</div>;
  }

  return (
    <div className="relative mt-28 px-4">
      <header className="absolute inset-x-0 flex justify-center mt-[-50px]">
        <img
          src={header}
          alt="header"
          className="w-11/12 sm:w-2/3 max-w-lg h-auto rounded-t-lg"
        />
      </header>

      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto mb-12 p-6">
        <div className="bg-white text-black rounded-lg shadow-lg p-4 overflow-y-auto max-h-[600px] h-[500px]">
          <div className="flex justify-between h-full">
            {/* Left */}
            <div className="flex flex-col items-start gap-4 mt-10 ml-10 w-1/2">
              <img
                src={user.picture || tmp}
                alt="Profile"
                className="w-24 h-24 rounded-full border"
              />
              <h2 className="text-2xl font-bold">{user.name}</h2>

              <p>
                <strong>Email:</strong> {user.email}
              </p>

              {/* Logout */}
              <button
                onClick={handleLogout}
                className="mt-6 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition"
              >
                Log Out
              </button>
            </div>

            {/* Right */}
            <div className="flex flex-col gap-4 items-center justify-center w-1/2 pr-10">
              <p className="font-bold">Stats</p>
              <div className="bg-red-200 rounded-lg px-8 py-6 text-center">
                <p className="text-lg font-semibold">{user.stars}</p>
                <p>⭐ Stars</p>
              </div>

              <div className="bg-red-200 rounded-lg px-8 py-6 text-center">
                <p className="text-lg font-semibold">{user.level}</p>
                <p>🏆 Level</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
