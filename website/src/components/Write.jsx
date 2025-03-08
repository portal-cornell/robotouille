import React, { useState } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";

const Write = () => {
  return (
    <div className="h-[calc(100vh-64px)] md:h-[calc(100vh-80px)] flex flex-col gap-6 p-9">
      <h1 className="text-xl font-roboto-slab">Create a New Post</h1>
      <form className="flex font-roboto-slab flex-col flex-1 gap-4">
        <input
          type="text"
          placeholder="Title"
          className="border border-gray-300 p-2 rounded-lg"
        />

        <ReactQuill
          theme="snow"
          className="flex-1 rounded-xl bg-white shadow-md"
        />
        <button className="w-28 px-2 py-2 bg-primary-darkBlue text-white rounded-lg hover:bg-primary-hoverBlue transition duration-300">
          Save Blog
        </button>
      </form>
    </div>
  );
};

export default Write;
