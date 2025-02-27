import React, { useState } from "react";
import teamHeader from "../assets/team-header.png";

// Headshots
import az from "../assets/members/ameliaZheng.jpg";
import ll from "../assets/members/linaLiu.png";
import rq from "../assets/members/RyanQiu.png";
import tq from "../assets/members/TiffanyQiu.jpg";
import gj from "../assets/members/GraceJin.jpg";
import iq from "../assets/members/IanUrquhart.jpeg";
import lsy from "../assets/members/LeongSuYean.png";
import gg from "../assets/members/Gonzalo Gonzalez-Pumariega.webp";

import linkedinIcon from "../assets/socials/linkedin.png";
import chefHat from "../assets/chef-hat.png";
import emailIcon from "../assets/socials/email.png";

const Team = () => {
  const [selectedMember, setSelectedMember] = useState(null);

  const teamMembers = [
    {
      name: "Gonzalo Gonzalez",
      year: "Ph.D.",
      role: "Project Lead",
      img: gg,
      hometown: "Miami, Fl",
      interests: "Video games, Movies",
      funfact: "Playing Overcooked stresses me now",
      linkedin: "https://www.linkedin.com/in/gonzalogonzalez2000/",
      email: "gg387@cornell.edu",
    },
    {
      name: "Amelia Zheng",
      year: 2027,
      role: "Developer",
      img: az,
      hometown: "Chicago, IL",
      interests: "Photography, Matcha, Music ",
      funfact: "My favorite app is Beli",
      linkedin: "https://www.linkedin.com/in/amelia-zheng-173933235/",
      email: "ayz23@cornell.edu",
    },
    {
      name: "Grace Jin",
      year: 2027,
      role: "Developer & Designer",
      img: gj,
      hometown: "San Jose, CA",
      interests: "Table tennis, Drawing",
      funfact: "I have 17k followers on Instagram",
      linkedin: "https://www.linkedin.com/in/grace-jin-9654a826b/",
      email: "gdj33@cornell.edu",
    },
    {
      name: "Henry Gao",
      role: "Developer",
    },
    {
      name: "Ian Urquhart",
      year: 2027,
      role: "Developer",
      img: iq,
      hometown: "Westchester, NY",
      interests: "Basketball, Cooking",
      funfact: "There's a castle in Scotland named after my last name",
      linkedin: "https://www.linkedin.com/in/ian-urquhart-112522279/",
      email: "iju2@cornell.edu",
    },
    {
      name: "Leong Su Yean",
      year: 2026,
      role: "Developer",
      img: lsy,
      hometown: "Singapore",
      interests: "Jiu Jitsu, Magic, Music",
      funfact: "I can drive a tank",
      linkedin: "https://www.linkedin.com/in/leong-su-yean-88266969/",
      email: "sl2658@cornell.edu",
    },
    {
      name: "Lina Liu",
      year: 2025,
      role: "Designer",
      img: ll,
      hometown: "Queens, NY",
      interests: "Snowboarding, Cooking",
      funfact: "I've reviewed over 500+ locations on Yelp",
      linkedin: "https://www.linkedin.com/in/lliu6907",
      email: "ll669@cornell.edu",
    },
    {
      name: "Ryan Qiu",
      year: 2028,
      role: "Developer & Designer",
      img: rq,
      hometown: "Houston, TX",
      interests: "Music, Movies",
      funfact: "I'm trying to double major in music",
      linkedin: "https://www.linkedin.com/in/ryan-qiu-194041297",
      email: "rwq3@cornell.edu",
    },
    {
      name: "Tiffany Qiu",
      year: 2028,
      role: "Developer",
      img: tq,
      hometown: "Long Island, NY",
      interests: "Badminton, Dance",
      funfact: "I like watching Japanese cooking videos",
      linkedin: "https://www.linkedin.com/in/tiffanyqiu22/",
      email: "tq52@cornell.edu",
    },
  ];

  const closeModal = () => setSelectedMember(null);

  return (
    <div className="relative mt-28">
      {/* Header Banner */}
      <header className="absolute inset-x-0 flex justify-center mt-[-50px]">
        <img
          src={teamHeader}
          alt="Meet the Team Header"
          className="w-2/3 max-w-md md:max-w-lg h-auto rounded-t-lg"
        />
      </header>

      {/* Team Members Grid */}
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto mb-12 p-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 justify-center mt-10">
          {teamMembers.map((member, index) => (
            <div
              key={index}
              className="bg-red-800 text-center p-6 rounded-md cursor-pointer hover:bg-red-900 transition duration-300"
              onClick={() => setSelectedMember(member)}
            >
              {/* Image (No Fixed Size in Grid) */}
              <div
                className="h-52 w-52 mx-auto bg-gray-300 rounded-lg overflow-hidden"
                style={{
                  backgroundImage: `url(${
                    member.img || "https://via.placeholder.com/150"
                  })`,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                }}
              ></div>

              {/* Name & Role */}
              <h3 className="text-sm font-semibold mt-2">{member.name}</h3>
              <p className="text-xs">{member.role}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Popup */}
      {selectedMember && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50 ">
          <div className="bg-white text-black p-6 rounded-lg max-w-3xl w-full flex flex-col md:flex-row gap-6 relative">
            {/* Left Side - Image (Fixed Size for Consistency) */}
            <div className="relative w-full md:w-1/3 flex flex-col items-center">
              <img
                src={selectedMember.img || "https://via.placeholder.com/300"}
                alt={selectedMember.name}
                className="w-56 h-56 object-cover rounded-lg"
              />
              <img
                src={chefHat}
                alt="Chef Hat"
                className="absolute -top-10 left-1/2 transform -translate-x-1/2 w-20 md:w-24"
              />

              {/* LinkedIn & Email Icons */}
              <div className="flex gap-4 mt-4">
                {selectedMember.linkedin && (
                  <a
                    href={selectedMember.linkedin}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <img
                      src={linkedinIcon}
                      alt="LinkedIn"
                      className="w-8 h-8"
                    />
                  </a>
                )}
                {selectedMember.email && (
                  <a href={`mailto:${selectedMember.email}`}>
                    <img src={emailIcon} alt="Email" className="w-8 h-8" />
                  </a>
                )}
              </div>
            </div>

            {/* Member Info */}
            <div className="font-roboto-slab flex-1">
              <h2 className="text-2xl font-bold">
                {selectedMember.name}{" "}
                {selectedMember.year && (
                  <span className="text-gray-500 text-xl">
                    {"- " + selectedMember.year}
                  </span>
                )}
              </h2>
              <p className="text-lg italic text-gray-500 mb-6">
                {selectedMember.role}
              </p>

              <div className="space-y-3">
                <p className="text-md">
                  <strong>Hometown:</strong> {selectedMember.hometown}
                </p>
                <p className="text-md">
                  <strong>Interests:</strong> {selectedMember.interests}
                </p>
                <p className="text-md">
                  <strong>Fun Fact:</strong> {selectedMember.funfact}
                </p>
              </div>
            </div>
            {/* Close Button */}
            <button
              className="absolute top-3 right-3 text-neutral-600 hover:text-gray-800 text-2xl font-bold"
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
