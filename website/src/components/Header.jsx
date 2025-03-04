import React from "react";
import { Link } from "react-router-dom";
import DownloadButton from "./Download";
import headerImage from "../assets/header-image.png";

const Header = () => {
  return (
    <header
      className="relative max-w-full z-50"
      style={{
        background: `
      url(${headerImage}) center -60px/cover no-repeat,
      linear-gradient(to bottom, #EAEAEA 30%, #E0F2FA 50%)
    `,
        height: "270px", // Keeps the height fixed
      }}
    >
      <nav className="flex justify-between items-center pt-16 px-20 ">
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
        <Link 
          to = "/blog"
          className = "bg-primary-darkBlue font-roboto-slab text-white py-2 px-4 rounded-lg hover:bg-primary-hoverBlue transition duration-300" 
          >
             Blog 
          </Link>
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
