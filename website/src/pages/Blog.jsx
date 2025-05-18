import React, { useState } from "react";
import { Link } from "react-router-dom";
import PostList from "../components/PostList";
import blogHeader from "../assets/blog-header2.png";
import cat from "../assets/cat.png";

const dummyPost = {
  title: "Title",
  date: "06/11/25",
  author: "Lorem ipsum",
  content:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. ".repeat(
      10
    ),
};

const dummySidebarPosts = Array(7).fill({
  title: "Title",
  preview:
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt...",
  img: cat,
});

const Blog = () => {
  const [selectedPost, setSelectedPost] = useState(dummyPost);

  return (
    <div className="relative mt-10 px-4  bg-cover min-h-screen pb-32">
      <div className="relative z-0 flex flex-col md:flex-row max-w-7xl mx-auto px-4">
        {/* Main Blog Content */}
        <div className="bg-primary-darkRed border-4 border-red-700 rounded-lg shadow-lg p-2 w-full md:w-2/3">
          <div className="bg-white rounded-md p-6 max-h-[600px] overflow-y-auto">
            <h2 className="text-xl font-bold mb-2">{selectedPost.title}</h2>
            <p className="text-sm text-gray-600 mb-1">
              By {selectedPost.author}
            </p>
            <p className="text-sm text-gray-500 mb-4">{selectedPost.date}</p>
            <p className="text-base text-gray-800 whitespace-pre-line">
              {selectedPost.content}
            </p>
          </div>
        </div>
        {/* Sidebar */}

        <aside className="w-full md:w-1/3 mt-6 md:mt-0 md:ml-6">
          {/* Add Blog Button */}
          <Link to="/write">
            <div className="flex justify-end mb-4">
              <button className="w-full px-6 py-2 bg-primary-darkBlue text-white rounded-lg font-roboto-slab hover:bg-primary-hoverBlue">
                (+) Add Blog
              </button>
            </div>
          </Link>

          {/* Sidebar Content  */}
          <div className="rounded-lg shadow-md">
            <h3 className="bg-primary-darkRed text-white text-lg font-roboto-slab px-4 py-2 rounded-t-md flex justify-between items-center">
              Latest Posts{" "}
            </h3>

            <div className="flex flex-col">
              {dummySidebarPosts.map((post, index) => {
                const isEven = index % 2 === 0;
                return (
                  <div
                    key={index}
                    onClick={() => setSelectedPost(post)}
                    className={`flex gap-3 items-start cursor-pointer p-2 transition duration-200 ${
                      isEven ? "bg-white" : "bg-gray-100"
                    } hover:bg-gray-200`}
                  >
                    <img
                      src={post.img}
                      alt="post preview"
                      className="w-14 h-14 rounded object-cover"
                    />
                    <div>
                      <p className="text-sm font-bold text-gray-800 leading-tight">
                        {post.title}
                      </p>
                      <p className="text-xs text-gray-600 leading-tight">
                        {post.preview}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
};

export default Blog;
