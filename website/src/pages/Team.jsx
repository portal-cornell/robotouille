import React from "react";
import teamHeader from "../assets/team-header.png";

const Team = () => {
  const teamMembers = [
    { name: "Gonzalo Gonzalez", role: "Ph.D." },
    { name: "Amelia Zheng", role: "Developer" },
    { name: "Lorem ipsum", role: "Developerr" },
    { name: "Lorem ipsum", role: "Developer" },
    { name: "Lorem ipsum", role: "Developer" },
    { name: "Lorem ipsum", role: "Designer" },
    { name: "Lorem ipsum", role: "Designer" },
    { name: "Lorem ipsum", role: "Marketer" },
    { name: "Lorem ipsum", role: "Designer" },
  ];

  return (
    <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto my-10 p-4 mt-20">
      {/* Section Header */}
      <div className="flex justify-center -translate-y-20">
        <img
          src={teamHeader}
          alt="Meet the Team Header"
          className="w-1/2 h-auto rounded-t-lg"
        />
      </div>

      {/* Grid */}
      <div className="grid grid-cols-3 gap-2">
        {teamMembers.map((member, index) => (
          <div key={index} className="bg-red-800 text-center p-2 rounded-md">
            {/* Image */}
            <div className="h-20 w-20 mx-auto mb-2 bg-gray-300 rounded-full"></div>

            {/* Name and Role */}
            <h3 className="text-sm font-semibold mb-1">{member.name}</h3>
            <p className="text-xs">{member.role}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Team;
