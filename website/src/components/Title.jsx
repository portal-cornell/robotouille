import React from "react";
import chefhat from "../assets/chef-hat.png";

const Title = () => {
  return (
    <div className="flex flex-col items-center space-y-4">
      {/* Image */}
      <img src={chefhat} alt="chef hat" className="w-50 h-40 inline-block" />

      {/* Text */}
      <h1
        className="text-primary-darkBlue font-nico-moji text-6xl text-center"
        style={{ textShadow: "2px 2px 2px rgba(0, 0, 0, 0.5)" }}
      >
        Robotouille
      </h1>
    </div>
  );
};

export default Title;
