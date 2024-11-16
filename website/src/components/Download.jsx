import React from "react";

const Download = ({ href, children, className }) => {
  return (
    <a
      href={href}
      className={`bg-black text-white py-2 px-4 rounded ${className}`}
    >
      {children}
    </a>
  );
};

export default Download;
