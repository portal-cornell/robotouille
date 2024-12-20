import React, { useEffect, useState } from "react";
import apple from "../assets/food/apple.png";
import hamburger from "../assets/food/hamburger.png";
import banana from "../assets/food/banana.png";
import cherries from "../assets/food/cherries.png";
import lettuce from "../assets/food/lettuce.png";
import onion from "../assets/food/onion.png";
import pear from "../assets/food/pear.png";
import pizza from "../assets/food/bakedpizza.png";
import orange from "../assets/food/cut_orange.png";
import potato from "../assets/food/fried_potato.png";
import tomato from "../assets/food/tomato.png";
import strawberry from "../assets/food/slicedstrawberry.png";
import watermelon from "../assets/food/watermelon.png";
import "./FallingItems.css";

const FallingItems = () => {
  const [animationEnabled, setAnimationEnabled] = useState(true);

  const items = [
    apple,
    hamburger,
    banana,
    cherries,
    lettuce,
    onion,
    pear,
    pizza,
    orange,
    potato,
    tomato,
    strawberry,
    watermelon,
  ];

  useEffect(() => {
    const fallingItems = document.querySelectorAll(".falling-item");
    fallingItems.forEach((item) => {
      item.style.setProperty("--random-position", Math.random());
      item.style.setProperty("--random-duration", Math.random() * 2 + 3 + "s");
      item.style.setProperty("--random-delay", Math.random() * 3 + "s");
    });
  }, []);

  return (
    <div className="relative w-full h-full overflow-hidden">
      {/* Toggle Button */}
      <div className="absolute top-20 z-10 bg-white shadow-md w-full">
        <button
          className="mx-auto my-2 block p-2 text-sm font-roboto-slab bg-blue-500 text-white rounded-md shadow-md"
          onClick={() => setAnimationEnabled(!animationEnabled)}
        >
          {animationEnabled ? "Pause" : "Play"}
        </button>
      </div>

      {/* Falling Items */}
      <div
        className={`falling-items ${animationEnabled ? "active" : "paused"}`}
        style={{ pointerEvents: "none" }}
      >
        {items.map((item, index) => (
          <img
            key={index}
            src={item}
            alt={`item-${index}`}
            className={`falling-item ${!animationEnabled ? "paused" : ""}`}
            style={{
              position: "absolute",
              top: "-100px", // Start above the viewport
              animation: "fall linear infinite",
              animationDuration: "calc(3s + var(--random-duration))",
              animationDelay: "var(--random-delay)", // Apply the random delay
              left: `calc(100% * var(--random-position))`,
              width: "70px", // Customize size
              height: "auto", // Maintain aspect ratio
            }}
          />
        ))}
      </div>
    </div>
  );
};

export default FallingItems;
