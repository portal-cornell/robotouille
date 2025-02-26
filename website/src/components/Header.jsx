import React from "react";
import { Link } from "react-router-dom";
import DownloadButton from "./Download";
import headerImage from "../assets/header-image.png";

const Header = () => {
  return (
    <header
      className="relative bg-neutral-200 max-w-full z-50 shadow-md"
      style={{
        backgroundImage: `url(${headerImage})`,
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundRepeat: "no-repeat",
        height: "180px", // Adjust height to match the image
      }}
    >
      <nav className="flex justify-between items-center pt-10 px-10 ">
        {/* Left Section */}
        <div className="flex space-x-6">
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
        <div className="flex space-x-6">
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
    </header>
  );
};

export default Header;
