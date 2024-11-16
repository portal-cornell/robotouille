import React from "react";
import chefhat from "../assets/chef-hat.png";

const Title = () => {
  return (
    <div className="relative flex flex-col items-center">
      <img src={chefhat} alt="chef hat" className="w-50 h-40" />

      <h1 className="text-primary-darkBlue font-nico-moji text-6xl text-center ">
        Robotouille
      </h1>
    </div>
  );
};

export default Title;
