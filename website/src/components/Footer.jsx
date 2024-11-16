import React from "react";
import SteamIcon from "../assets/socials/steam.svg";
import InstagramIcon from "../assets/socials/instagram.svg";
import TwitterIcon from "../assets/socials/twitter.svg";
import tile from "../assets/tile.png";
import footerLogo from "../assets/footer-logo.png";
import DownloadButton from "./Download";

const Footer = () => {
  return (
    <div
      className="w-full bg-cover px-0 py-10 flex flex-col justify-between items-center relative"
      style={{
        backgroundImage: `url(${tile})`, // Background image
      }}
    >
      {/* Main Content: Left and Right Sections */}
      <div className="flex justify-between items-center w-full max-w-6xl">
        {/* Left Section: Footer Logo */}
        <div className="flex flex-col items-start">
          <img
            src={footerLogo}
            alt="Footer Logo"
            style={{ width: "200px", height: "auto" }}
          />
        </div>

        {/* Right Section: Download Button and Follow Us */}
        <div className="flex flex-col items-end space-y-4">
          {/* Download Button */}
          <DownloadButton />

          {/* Follow Us */}
          <div className="flex flex-col ">
            <p className="text-lg font-roboto-slab text-neutral-600">
              Follow Us!
            </p>
            <div className="flex space-x-4 mt-2">
              <a
                href="https://www.instagram.com/robotouille_game/?hl=en"
                target="_blank"
                rel="noopener noreferrer"
              >
                <img src={InstagramIcon} alt="Instagram" className="w-8 h-8" />
              </a>

              {/* Twitter */}
              <a
                href="https://x.com/RobotouilleGame"
                target="_blank"
                rel="noopener noreferrer"
              >
                <img src={TwitterIcon} alt="Twitter" className="w-8 h-8" />
              </a>

              {/* Steam */}
              <a href="#" target="_blank" rel="noopener noreferrer">
                <img src={SteamIcon} alt="Steam" className="w-8 h-8" />
              </a>
            </div>
          </div>
        </div>
      </div>

      {/* Copyright Text: Bottom Center */}
      <div className="absolute bottom-2 w-full text-center">
        <p className="text-neutral-500">© Robotouille 2024</p>
      </div>
    </div>
  );
};

export default Footer;
