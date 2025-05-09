import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import DownloadButton from "./Download";
import { FiMenu, FiX } from "react-icons/fi";
import headerImage from "../assets/header-image.png";

const Header = () => {
  const [user, setUser] = useState(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [bgPosition, setBgPosition] = useState(
    window.innerWidth > 768 ? "-70px" : "-30px"
  );
  const [bgSize, setBgSize] = useState("auto 120px");

  useEffect(() => {
    const loadUser = () => {
      const storedUser = localStorage.getItem("user");
      setUser(storedUser ? JSON.parse(storedUser) : null);
    };

    loadUser();

    const interval = setInterval(() => {
      loadUser(); // check every 500ms
    }, 500);

    const handleStorageChange = () => {
      loadUser();
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768 && window.innerWidth <= 1440) {
        setBgPosition("-60px");
      } else {
        setBgPosition("-30px");
      }

      if (window.innerWidth >= 1600) {
        setBgSize("auto 300px");
      } else {
        setBgSize("cover");
      }
    };

    window.addEventListener("resize", handleResize);
    handleResize();

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  return (
    <div className="relative w-full aspect-[18/4]">
      {" "}
      {/* Background Image */}
      <div className="absolute inset-0 bg-gradient-to-b from-[#EAEAEA] via-[#E0F2FA] to-[#E0F2FA] " />
      <div
        className="absolute inset-0 w-full h-full bg-no-repeat bg-top overflow-visible z-10"
        style={{
          backgroundImage: `url(${headerImage})`,
          backgroundSize: bgSize,
          backgroundPosition: `center ${bgPosition}`,
        }}
      ></div>
      <nav className="relative flex justify-between items-center pt-16 px-20 md:px-20 z-20">
        <button
          className="md:hidden text-primary-darkBlue text-3xl focus:outline-none absolute top-6 left-6"
          onClick={() => setMenuOpen(!menuOpen)}
        >
          {menuOpen ? <FiX /> : <FiMenu />}
        </button>
        {/* Left Section */}
        <div className="hidden md:flex space-x-6">
          <Link
            to="/"
            className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
          >
            Home
          </Link>
          <Link
            to="/about"
            className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
          >
            About
          </Link>
          <Link
            to="/team"
            className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
          >
            Team
          </Link>
        </div>

        {/* Right Section */}
        <div className="hidden md:flex space-x-6">
          {
            <Link
              to="/blog"
              className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
            >
              Blog
            </Link>
          }
          {user ? (
            <Link
              to="/profile"
              className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300 flex items-center gap-2"
            >
              {user.picture && (
                <img
                  src={user.picture}
                  alt="Profile"
                  className="w-6 h-6 rounded-full border"
                />
              )}
              <span>{"My Profile"}</span>
            </Link>
          ) : (
            <Link
              to="/signin"
              className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
            >
              Sign In
            </Link>
          )}
          {/* <Link
            to="/leaderboard"
            className="bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300"
          >
            Leaderboard
          </Link> */}
          {/* <DownloadButton
            href="/download"
            className="bg-red-600 text-white py-2 px-4 rounded-lg hover:bg-red-700 transition duration-300"
          >
            DOWNLOAD
          </DownloadButton> */}
        </div>
      </nav>
      {/* mobile view */}
      {menuOpen && (
        <div className="z-40 fixed top-0 left-0 w-full bg-primary-blue bg-opacity-5 backdrop-blur-md shadow-md flex flex-col items-center space-y-4 py-4 transition-all duration-500 ease-in-out max-h-[250px] overflow-hidden border-b border-gray-300">
          {" "}
          {/* Close Button */}
          <button
            className="absolute top-6 left-6 text-3xl text-primary-darkBlue focus:outline-none"
            onClick={() => setMenuOpen(false)}
          >
            <FiX />
          </button>
          {/* Menu Links */}
          <Link
            to="/"
            className="nav-link font-roboto-slab text-xl"
            onClick={() => setMenuOpen(false)}
          >
            Home
          </Link>
          <Link
            to="/about"
            className="nav-link font-roboto-slab text-xl"
            onClick={() => setMenuOpen(false)}
          >
            About
          </Link>
          <Link
            to="/team"
            className="nav-link font-roboto-slab  text-xl"
            onClick={() => setMenuOpen(false)}
          >
            Team
          </Link>
          <Link
            to="/blog"
            className="nav-link font-roboto-slab  text-xl"
            onClick={() => setMenuOpen(false)}
          >
            Blog
          </Link>
          {user ? (
            <Link
              to="/profile"
              className="nav-link font-roboto-slab text-xl"
              onClick={() => setMenuOpen(false)}
            >
              My Profile
            </Link>
          ) : (
            <Link
              to="/signin"
              className="nav-link font-roboto-slab  text-xl"
              onClick={() => setMenuOpen(false)}
            >
              Sign In
            </Link>
          )}
        </div>
      )}
    </div>
  );
};

export default Header;
