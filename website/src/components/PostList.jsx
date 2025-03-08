import React from "react";
import PostListItem from "./PostListItem";

const PostList = () => {
  return (
    <div className="flex flex-col gap-12 mb-8">
      <PostListItem />
      <PostListItem />
      <PostListItem />
    </div>
  );
};

export default PostList;
