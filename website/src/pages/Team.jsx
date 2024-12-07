import React, { useState } from "react";
import teamHeader from "../assets/team-header.png";
//headshots
import az from "../assets/members/ameliaZheng.jpg";
import ll from "../assets/members/linaLiu.png";

import linkedinIcon from "../assets/socials/linkedin.png";
import chefHat from "../assets/chef-hat.png";

const Team = () => {
  const [selectedMember, setSelectedMember] = useState(null);

  const teamMembers = [
    { name: "Gonzalo Gonzalez", role: " " },
    { name: "Alan Chen", role: "Developer" },
    {
      name: "Amelia Zheng",
      role: "Developer",
      hometown: " ",
      interests: " ",
      funFact: " ",
      img: az,
      linkedin: "https://www.linkedin.com/in/amelia-zheng-173933235/",
    },
    { name: "Colin Wu", role: "Developer" },
    { name: "Henry Gao", role: "Developer" },
    { name: "Ian Urquhart", role: "Developer" },
    { name: "Iris Li", role: "Marketer" },
    { name: "Su Yean", role: "Developer" },
    { name: "Tiffany Qiu", role: "Developer" },
    { name: "Grace Jin", role: "Designer" },
    {
      name: "Lina Liu",
      role: "Designer",
      hometown: "",
      interests: "",
      funFact: "",
      img: ll,
      linkedin: "",
    },
    { name: "Ryan Qiu", role: "Designer" },
  ];

  const closeModal = () => setSelectedMember(null);

  return (
    <div className="relative mt-28">
      <div className="absolute inset-x-0 -top-15 flex justify-center">
        <img
          src={teamHeader}
          alt="Meet the Team Header"
          className="w-1/3 h-auto rounded-t-lg"
        />
      </div>
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-3xl mx-auto mb-12 p-6">
        <div className="grid grid-cols-3 gap-2 mt-10">
          {teamMembers.map((member, index) => (
            <div
              key={index}
              className="bg-red-800 text-center p-2 rounded-md cursor-pointer hover:bg-red-900"
              onClick={() => setSelectedMember(member)}
            >
              {/* Image */}
              <div
                className="h-52 w-44 mx-auto mb-2 bg-gray-300 mt-6 overflow-hidden"
                style={{
                  backgroundImage: `url(${
                    member.img || "https://via.placeholder.com/150"
                  })`,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                }}
              ></div>

              {/* Name and Role */}
              <h3 className="text-sm font-semibold mb-1">{member.name}</h3>
              <p className="text-xs">{member.role}</p>
            </div>
          ))}
        </div>
      </div>

      {selectedMember && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
          <div className="bg-white text-black p-10 rounded-lg max-w-max w-full flex flex-col md:flex-row gap-10 relative">
            <div className="relative">
              <img
                src={selectedMember.img || "https://via.placeholder.com/300"}
                alt={selectedMember.name}
                className="rounded-lg w-60 h-72 object-cover"
              />
              <img
                src={chefHat}
                alt="Chef Hat"
                className="absolute -top-20 left-1/2 transform -translate-x-1/2 w-48"
              />
              <div className="flex justify-center mt-4">
                {selectedMember.linkedin && (
                  <a
                    href={selectedMember.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2"
                  >
                    <img
                      src={linkedinIcon}
                      alt="LinkedIn"
                      className="w-8 h-8"
                    />
                  </a>
                )}
              </div>
            </div>

            <div className="font-roboto-slab mt-10">
              <h2 className="text-2xl font-bold">{selectedMember.name}</h2>
              <p className="text-lg italic text-gray-500 mb-6">
                {selectedMember.role}
              </p>
              <p className="text-sm">
                <strong>Hometown: </strong>
                {selectedMember.hometown || " "}
              </p>
              <p className="text-sm mt-2">
                <strong>Interests: </strong>
                {selectedMember.interests || " "}
              </p>
              <p className="text-sm mt-2">
                <strong>Fun Fact: </strong>
                {selectedMember.funFact || " "}
              </p>
            </div>

            <button
              className="absolute top-3 right-3 text-neutral-600 hover:text-gray-800 py-3 px-6  text-2xl font-bold"
              onClick={closeModal}
            >
              &times;
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Team;
