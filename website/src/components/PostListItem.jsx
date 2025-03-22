import React from "react";
import { Link } from "react-router-dom";

const PostListItem = () => {
  return (
    <div className="w-full border border-gray-300 bg-white rounded-lg p-4 shadow-sm">
      <div className="flex flex-col xl:flex-row gap-8 items-start w-full">
        <div className="flex flex-col gap-4 font-roboto-slab text-left w-full">
          {/* Title */}
          <Link
            to="/blog/1"
            className="text-2xl font-semibold text-black hover:underline"
          >
            Title
          </Link>

          {/* Author */}
          <p className="text-sm text-gray-600">By</p>

          {/* Preview */}
          <p className="text-gray-800 line-clamp-2">preview</p>
        </div>
      </div>
    </div>
  );
};

export default PostListItem;
