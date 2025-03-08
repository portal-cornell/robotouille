import React from "react";
import { Link } from "react-router-dom";

const PostListItem = () => {
  return (
    <div className="flex flex-col xl:flex-row gap-8 mt-5 items-start w-full">
      <div className="flex flex-col gap-4 font-roboto-slab text-left w-full">
        {/* Title */}
        <Link to="/blog/1" className="text-2xl font-semibold">
          Title
        </Link>

        {/* Author */}
        <p className="text-sm text-gray-200">By </p>

        {/* Preview */}
        <p className="text-gray-100 line-clamp-2"> preview </p>
      </div>
    </div>
  );
};

export default PostListItem;
