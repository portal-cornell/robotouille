// PostList.jsx
import React, { useEffect, useState } from "react";
import PostListItem from "./PostListItem";

const PostList = () => {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/blogposts");
        const data = await res.json();
        if (data.status === "success") {
          setPosts(data.posts);
        } else {
          console.error("Failed to fetch posts:", data.message);
        }
      } catch (err) {
        console.error("Fetch error:", err);
      }
    };

    fetchPosts();
  }, []);

  return (
    <div className="flex flex-col gap-12 mb-8">
      {posts.map((post) => (
        <PostListItem key={post.id} post={post} />
      ))}
    </div>
  );
};

export default PostList;
