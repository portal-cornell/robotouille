import React from "react";

const DownloadButton = ({
  href = "#",
  children = "DOWNLOAD",
  className = "",
}) => {
  return (
    <a
      href={href}
      className={`bg-red-600 text-white font-roboto-slab py-2 px-6 rounded-xl text-md hover:bg-red-700 transition duration-300 ${className}`}
    >
      {children}
    </a>
  );
};

export default DownloadButton;
