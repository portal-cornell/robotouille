import React from "react";
import lbHeader from "../assets/leaderboard-header.png";

const Leaderboard = () => {
  return (
    <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto my-10 p-4 mt-20">
      {/* Section Header */}
      <div className="flex justify-center -translate-y-20">
        <img
          src={lbHeader}
          alt="Leaderboard Header"
          className="w-1/2 h-auto rounded-t-lg"
        />
      </div>
    </div>
  );
};

export default Leaderboard;
