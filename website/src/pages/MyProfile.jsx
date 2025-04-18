import React, { useEffect, useState } from "react";
import header from "../assets/profileHeader.png";
import { useNavigate } from "react-router-dom";
import tmp from "../assets/tempProfilePic.png";
import imageCompression from "browser-image-compression";

const Profile = () => {
  const [user, setUser] = useState(null);
  const [editingName, setEditingName] = useState("");
  const [isEditingName, setIsEditingName] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("user");
    localStorage.removeItem("accessToken");
    window.dispatchEvent(new Event("storage"));
    setUser(null);
    navigate("/");
  };

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      const compressedFile = await imageCompression(file, {
        maxSizeMB: 0.2,
        maxWidthOrHeight: 300,
        useWebWorker: true,
      });

      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Image = reader.result;

        const res = await fetch("http://localhost:8000/api/update_picture", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
          body: JSON.stringify({ new_picture: base64Image }),
        });

        const data = await res.json();
        if (data.status === "success") {
          setUser(data.user);
          localStorage.setItem("user", JSON.stringify(data.user));
        } else {
          alert("Image update failed: " + data.message);
        }
      };

      reader.readAsDataURL(compressedFile);
    } catch (err) {
      console.error("Image upload error:", err);
      alert("Failed to upload image.");
    }
  };

  const handleUsernameUpdate = async () => {
    if (!editingName.trim()) {
      alert("Name cannot be empty.");
      return;
    }

    try {
      const res = await fetch("http://localhost:8000/api/update_username", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
        },
        body: JSON.stringify({ new_username: editingName }),
      });

      const data = await res.json();
      if (data.status === "success") {
        setUser(data.user);
        localStorage.setItem("user", JSON.stringify(data.user));
        setIsEditingName(false);
      } else {
        alert("Username update failed: " + data.message);
      }
    } catch (err) {
      console.error("Username update error:", err);
      alert("Failed to update username.");
    }
  };

  useEffect(() => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      const parsed = JSON.parse(storedUser);
      setUser(parsed);
      setEditingName(parsed.name);
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
            {/* Left Side */}
            <div className="flex flex-col items-start gap-4 mt-10 ml-10 w-1/2">
              <div className="relative">
                {/* user picture */}
                <img
                  src={user.picture || tmp}
                  alt="Profile"
                  className="w-24 h-24 rounded-full border object-cover"
                  onError={(e) => (e.target.src = tmp)}
                />
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileChange}
                  className="mt-2 text-sm"
                />
              </div>

              {/* username */}
              <div className="flex items-center gap-2 mt-2">
                {isEditingName ? (
                  <>
                    <input
                      type="text"
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      className="border px-2 py-1 rounded text-sm"
                    />
                    <button
                      onClick={handleUsernameUpdate}
                      className="bg-blue-600 text-white px-3 py-1 text-sm rounded hover:bg-blue-700 transition"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => {
                        setEditingName(user.name); // reset to current
                        setIsEditingName(false);
                      }}
                      className="text-sm text-gray-600 hover:text-black"
                    >
                      Cancel
                    </button>
                  </>
                ) : (
                  <>
                    <p className="text-xl font-semibold">{user.name}</p>
                    <button
                      onClick={() => {
                        setEditingName(user.name);
                        setIsEditingName(true);
                      }}
                      className="text-sm text-blue-600 underline hover:text-blue-800"
                    >
                      Edit
                    </button>
                  </>
                )}
              </div>

              {/* email */}
              <p>
                <strong>Email:</strong> {user.email}
              </p>

              {/* logout */}
              <button
                onClick={handleLogout}
                className="mt-6 bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition"
              >
                Log Out
              </button>
            </div>

            {/* Right Side */}
            <div className="flex flex-col gap-4  justify-center w-1/2 pr-10">
              <p className="font-bold">Stats</p> {/* stats */}
              <div className="flex flex-row gap-6 items-center">
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
    </div>
  );
};

export default Profile;
