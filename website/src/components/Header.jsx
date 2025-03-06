import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import DownloadButton from "./Download";
import { FiMenu, FiX } from "react-icons/fi";
import headerImage from "../assets/header-image.png";

const Header = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [bgPosition, setBgPosition] = useState(
    window.innerWidth > 768 ? "-70px" : "-30px"
  );
  useEffect(() => {
    const handleResize = () => {
      setBgPosition(window.innerWidth > 768 ? "-70px" : "-30px");
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);
  return (
    <header
      className="relative max-w-full z-50 bg-cover bg-center md:h-[270px] h-[170px]"
      style={{
        background: `
          url(${headerImage}) center ${bgPosition}/cover no-repeat,
          linear-gradient(to bottom, #EAEAEA 30%, #E0F2FA 50%)
        `,
      }}
    >
      <nav className="flex justify-between items-center pt-16 px-20 md:px-20">
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
          {/* <Link 
          to = "/blog"
          className = "bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300" 
          >
             Blog 
          </Link> */}
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
        <div className="fixed top-0 left-0 w-full bg-primary-blue bg-opacity-5 backdrop-blur-md shadow-md flex flex-col items-center space-y-4 py-4 transition-all duration-500 ease-in-out max-h-[250px] overflow-hidden border-b border-gray-300">
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
        </div>
      )}
    </header>
  );
};

export default Header;
