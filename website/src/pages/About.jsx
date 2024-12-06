import React from "react";
import aboutHeader from "../assets/about-header.png";
import cheeseBurger from "../assets/cheese_burger.gif";
import kitchen from "../assets/kitchen.gif";
import lettucetomatoburger from "../assets/lettuce_tomato_burger.gif";

const About = () => {
  return (
    <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto my-10 p-4 mt-20">
      {/* Section Header */}
      <div className="flex justify-center -translate-y-20">
        <img
          src={aboutHeader}
          alt="About Header"
          className="w-1/2 h-auto rounded-t-lg"
        />
      </div>

      {/* About Text */}
      <div className="p-6">
        <h2 className="text-lg font-semibold text-left mb-4">
          About Robotouille
        </h2>
        <p className="text-white text-left">
          Robots will be involved in every part of our lives in the near future
          so we need to teach them how to perform complex tasks. Humans break
          apart complex tasks like making hamburgers into smaller subtasks like
          cutting lettuce and cooking patties. We can teach robots to do the
          same by showing them how to perform easier tasks subtasks and then
          combine those subtasks to perform harder tasks. We created Robotouille
          so we can stress test this idea through an easily customizable cooking
          environment where the task possibilities are endless!
        </p>
      </div>

      {/* GIF Section */}
      <div className="flex justify-between items-center gap-4 p-6">
        <img
          src={cheeseBurger}
          alt="Cheeseburger"
          className="w-1/3 rounded-lg shadow-lg"
        />
        <img
          src={kitchen}
          alt="Kitchen"
          className="w-1/3 rounded-lg shadow-lg"
        />
        <img
          src={lettucetomatoburger}
          alt="Lettuce Tomato Burger"
          className="w-1/3 rounded-lg shadow-lg"
        />
      </div>
    </div>
  );
};

export default About;
