import React from "react";
import chefhat from "../assets/chef-hat.png";

const Title = () => {
  return (
    <div className="flex flex-col items-center space-y-2">
      {/* Chef Hat Image */}
      <img
        src={chefhat}
        alt="chef hat"
        className="w-50 h-40 md:w-50 md:h-40 inline-block"
      />

      {/* Robotouille */}
      <h1
        className="text-primary-darkBlue font-nico-moji text-5xl md:text-6xl text-center pb-4"
        style={{ textShadow: "2px 2px 2px rgba(0, 0, 0, 0.5)" }}
      >
        Robotouille
      </h1>
    </div>
  );
};

export default Title;
