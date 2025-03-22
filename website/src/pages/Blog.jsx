import React, { useState } from "react";
import { Link } from "react-router-dom";
import PostList from "../components/PostList";
import blogHeader from "../assets/blog-header2.png";

const Blog = () => {
  return (
    <div className="relative mt-28 px-4">
      <header className="absolute inset-x-0 flex justify-center mt-[-50px]">
        <img
          src={blogHeader}
          alt="blog header"
          className="w-11/12 sm:w-2/3 max-w-lg h-auto rounded-t-lg"
        />
      </header>

      <div className="bg-primary-darkRed text-white font-roboto-slab rounded-lg shadow-2xl max-w-4xl mx-auto mb-12 p-6">
        <div className="bg-white text-black rounded-lg shadow-lg p-4 overflow-y-auto max-h-[800px] h-[700px]">
          <div className="flex flex-col justify-center mt-10 ml-10">
            <Link to="/write">
              <button className="px-4 py-2 bg-primary-darkBlue text-white rounded-lg hover:bg-primary-hoverBlue">
                Add Blog
              </button>
            </Link>
            <PostList />
          </div>{" "}
        </div>
      </div>
    </div>
  );
};

export default Blog;
