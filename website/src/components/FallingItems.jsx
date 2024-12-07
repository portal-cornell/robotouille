import React, { useEffect } from "react";
import apple from "../assets/food/apple.png";
import hamburger from "../assets/food/hamburger.png";
import banana from "../assets/food/banana.png";
import cherries from "../assets/food/cherries.png";
import lettuce from "../assets/food/lettuce.png";
import onion from "../assets/food/onion.png";
import pear from "../assets/food/pear.png";
import "./FallingItems.css";

const FallingItems = () => {
  const items = [apple, hamburger, banana, cherries, lettuce, onion, pear]; // Array of item images

  useEffect(() => {
    const fallingItems = document.querySelectorAll(".falling-item");
    fallingItems.forEach((item) => {
      item.style.setProperty("--random-position", Math.random());
      item.style.setProperty("--random-duration", Math.random() * 2 + 3 + "s"); // Random duration between 3s and 5s
    });
  }, []);

  return (
    <div className="falling-items">
      {items.map((item, index) => (
        <img
          key={index}
          src={item}
          alt={`item-${index}`}
          className="falling-item"
        />
      ))}
    </div>
  );
};

export default FallingItems;
