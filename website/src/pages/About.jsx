import React from "react";
import aboutHeader from "../assets/about-header.png";
import gif from "../assets/all_tasks.gif";

const About = () => {
  return (
    <div className="relative mt-28">
      {/* Header Banner (Smaller & Well-Aligned) */}
      <header className="absolute inset-x-0 flex justify-center mt-[-50px]">
        <img
          src={aboutHeader}
          alt="About Header"
          className="w-2/3 max-w-md md:max-w-lg h-auto rounded-t-lg"
        />
      </header>

      {/* Main Content Box */}
      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto mb-12 p-6">
        {/* Introduction */}
        <div>
          <p className="text-white text-left mt-6">
            Robots will be involved in every part of our lives in the near
            future, so we need to teach them how to perform complex tasks.
            Humans break apart complex tasks like making hamburgers into smaller
            subtasks, such as cutting lettuce and cooking patties. We can teach
            robots to do the same by showing them how to perform easier subtasks
            and then combine those subtasks to perform harder tasks. We created
            Robotouille to stress test this idea through an easily customizable
            cooking environment where the task possibilities are endless!
          </p>
        </div>

        {/* Research Papers Section */}
        <div className="mt-6">
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

        {/* GIF Section */}
        <div className="flex justify-center items-center p-6">
          <img
            src={gif}
            alt="All tasks in Robotouille"
            className="w-8/12 max-w-lg rounded-lg shadow-lg"
          />
        </div>
      </div>
    </div>
  );
};

export default About;
