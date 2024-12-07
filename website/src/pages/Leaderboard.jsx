import React from "react";
import lbHeader from "../assets/leaderboard-header.png";

const Leaderboard = () => {
  const leaderboardData = [
    { rank: 1, username: "EatSleepRepeat6", score: 12931, badge: "gold" },
    { rank: 2, username: "BurritoASAP", score: 11050, badge: "silver" },
    { rank: 3, username: "burgers_in_my_tummy", score: 10068, badge: "bronze" },
    { rank: 4, username: "user", score: null },
    { rank: 5, username: "user", score: null },
    { rank: 6, username: "user", score: null },
    { rank: 7, username: "user", score: null },
    { rank: 8, username: "user", score: null },
    { rank: 9, username: "user", score: null },
    { rank: 10, username: "user", score: null },
    { rank: 11, username: "user", score: null },
    { rank: 12, username: "user", score: null },
    { rank: 13, username: "user", score: null },
    { rank: 14, username: "user", score: null },
    { rank: 15, username: "user", score: null },
    { rank: 16, username: "user", score: null },
    { rank: 17, username: "user", score: null },
  ];

  const getBadgeStyle = (badge) => {
    switch (badge) {
      case "gold":
        return "bg-yellow-400";
      case "silver":
        return "bg-gray-300";
      case "bronze":
        return "bg-orange-400";
      default:
        return "bg-blue-200";
    }
  };

  return (
    <div className="relative mt-28">
      {/* Header */}
      <div className="absolute inset-x-0 -top-15 flex justify-center">
        <img
          src={lbHeader}
          alt="Leaderboard Header"
          className="w-1/3 max-w-sm md:max-w-md lg:max-w-lg h-auto rounded-t-lg"
        />
      </div>

      {/* Leaderboard Container */}
      <div className="bg-primary-darkRed h-svh w-6/12 text-white font-roboto-slab rounded-lg shadow-2xl max-w-3xl mx-auto mb-12 p-6">
        <div className="bg-white text-black rounded-lg shadow-lg p-4 overflow-y-auto max-h-[680px] mt-8">
          <div>
            {leaderboardData.map((entry, index) => (
              <div
                key={entry.username}
                className={`flex items-center justify-between py-3 px-4 ${
                  index % 2 === 0 ? "bg-gray-50" : "bg-gray-100"
                }`}
              >
                {/* Rank */}
                <div className="flex items-center gap-2">
                  <div
                    className={`h-8 w-8 flex items-center justify-center rounded-full font-bold text-white ${getBadgeStyle(
                      entry.badge
                    )}`}
                  >
                    {entry.rank}
                  </div>
                  <div className="text-sm font-medium">{entry.username}</div>
                </div>

                {/* Score */}
                <div className="text-sm font-bold text-gray-700">
                  {entry.score !== null ? entry.score : "score"}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Leaderboard;
