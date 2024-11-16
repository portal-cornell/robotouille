import React from "react";
import steam from "../assets/socials/steam.png";
import instagram from "../assets/socials/instagram.png";
import twitter from "../assets/socials/twitter.png";

const Socials = ({ colorClass }) => {
  return (
    <div className="flex justify-center space-x-8 mt-5">
      {/* Instagram */}
      <a
        href="https://www.instagram.com/robotouille_game/?hl=en"
        className={`flex items-center justify-center ${colorClass}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <img
          src={instagram}
          alt="Instagram"
          className={`w-8 h-8 ${colorClass}`}
        />
      </a>

      {/* Twitter */}
      <a
        href="https://x.com/RobotouilleGame"
        className={`flex items-center justify-center ${colorClass}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src={twitter} alt="Twitter" className={`w-8 h-8 ${colorClass}`} />
      </a>

      {/* Steam */}
      <a
        href="#"
        className={`flex items-center justify-center ${colorClass}`}
        target="_blank"
        rel="noopener noreferrer"
      >
        <img src={steam} alt="Steam" className={`w-8 h-8 ${colorClass}`} />
      </a>
    </div>
  );
};

export default Socials;
