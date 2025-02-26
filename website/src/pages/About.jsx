import React from "react";
import aboutHeader from "../assets/about-header.png";
import cheeseBurger from "../assets/cheese_burger.gif";
import kitchen from "../assets/kitchen.gif";
import lettucetomatoburger from "../assets/lettuce_tomato_burger.gif";
import gif from "../assets/all_tasks.gif";

const About = () => {
  return (
    <div className="relative mt-28">
      {/* Section Header */}
      <div className="absolute inset-x-0 -top-15 flex justify-center">
        <img
          src={aboutHeader}
          alt="About Header"
          className="w-1/3 max-w-sm md:max-w-md lg:max-w-lg h-auto rounded-t-lg"
        />
      </div>

      {/* Main Content */}
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-3xl mx-auto mb-12 p-6">
        <div>
          <p className="text-white text-left mt-6">
            Robots will be involved in every part of our lives in the near
            future so we need to teach them how to perform complex tasks. Humans
            break apart complex tasks like making hamburgers into smaller
            subtasks like cutting lettuce and cooking patties. We can teach
            robots to do the same by showing them how to perform easier tasks
            subtasks and then combine those subtasks to perform harder tasks. We
            created Robotouille so we can stress test this idea through an
            easily customizable cooking environment where the task possibilities
            are endless!
          </p>
        </div>
        {/* Research Papers Section */}
        <div className="mt-8">
          <h2 className="text-l text-left">
            Check out the following papers where we've used Robotouille!
          </h2>
          <ul className="mt-4 text-l list-disc pl-6">
            <li>
              <a
                href="https://portal-cornell.github.io/robotouille/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-blue hover:text-blue-400"
              >
                Robotouille: An Asynchronous Planning Benchmark for LLM Agents
              </a>
            </li>
            <li>
              <a
                href="https://portal-cornell.github.io/demo2code/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-blue hover:text-blue-400"
              >
                Demo2Code: From Summarizing Demonstrations to Synthesizing Code
                via Extended Chain-of-Thought
              </a>
            </li>
            <li>
              <a
                href="https://portal-cornell.github.io/llms-for-planning/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-blue hover:text-blue-400"
              >
                Query-Efficient Planning with Language Models
              </a>
            </li>
          </ul>
        </div>

        {/* GIFs */}
        <div className="flex justify-center items-center gap-6 p-6 ">
          <img
            src={gif}
            alt="all tasks"
            className="w-8/12 rounded-lg shadow-lg"
          />
        </div>
      </div>
    </div>
  );
};

export default About;
