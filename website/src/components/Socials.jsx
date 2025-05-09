import React from "react";
import SteamIcon from "../assets/socials/steam.png";
import InstagramIcon from "../assets/socials/instagram.png";
import TwitterIcon from "../assets/socials/twitter.png";

const Socials = () => {
  return (
    <div className="flex justify-center space-x-8 mt-5">
      {/* Instagram */}
      <a
        href="https://www.instagram.com/robotouille_game/?hl=en"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src={InstagramIcon} alt="Instagram" className="w-10 h-10" />
      </a>

      {/* Twitter */}
      <a
        href="https://x.com/RobotouilleGame"
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src={TwitterIcon} alt="Twitter" className="w-10 h-10" />
      </a>

      {/* Steam
      <a href="#" target="_blank" rel="noopener noreferrer">
        <img src={SteamIcon} alt="Steam" className="w-10 h-10" />
      </a> */}
    </div>
  );
};

export default Socials;
