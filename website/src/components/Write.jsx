import React, { useState } from "react";
import ReactQuill from "react-quill";
import "react-quill/dist/quill.snow.css";
import parse from "html-react-parser";

const Write = () => {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [showPreview, setShowPreview] = useState(false);
  const modules = {
    toolbar: [
      [{ header: [1, 2, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ list: "ordered" }, { list: "bullet" }],
      ["link", "color", "image"],
      [{ "code-block": true }],
      ["clean"],
    ],
  };
  const formats = [
    "header",
    "bold",
    "italic",
    "underline",
    "strike",
    "list",
    "bullet",
    "link",
    "indent",
    "image",
    "code-block",
    "color",
  ];
  return (
    <div className="h-[calc(100vh-64px)] md:h-[calc(100vh-80px)] flex flex-col gap-6 p-9">
      <h1 className="text-xl font-roboto-slab">Create a New Post</h1>
      <form className="flex font-roboto-slab flex-col flex-1 gap-4">
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="border border-gray-300 p-2 rounded-lg"
        />

        <div className="border bg-white border-gray-300 rounded-xl overflow-hidden">
          <ReactQuill
            theme="snow"
            value={content}
            onChange={setContent}
            modules={modules}
            formats={formats}
            className="h-full"
          />
          <style>
            {`
              .ql-container {
                height: 400px !important;  
                overflow-y: auto;  
              }
            `}
          </style>
        </div>

        <div className="flex gap-4">
          <button
            type="button"
            onClick={async () => {
              if (!title.trim() || !content.trim()) {
                alert("Please fill in both title and content.");
                return;
              }

              try {
                const res = await fetch("http://localhost:8000/api/blogposts", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem(
                      "accessToken"
                    )}`,
                  },
                  body: JSON.stringify({
                    title,
                    content,
                  }),
                });

                const data = await res.json();

                if (data.status === "success") {
                  alert("Post published!");
                  window.location.href = "/blog"; // or use navigate("/blog") if using useNavigate()
                } else {
                  alert("Failed to publish post: " + data.message);
                }
              } catch (err) {
                console.error("Error submitting blog:", err);
                alert("Error submitting blog post.");
              }
            }}
            className="w-28 px-2 py-2 bg-primary-darkBlue text-white rounded-lg hover:bg-primary-hoverBlue transition duration-300"
          >
            Save Blog
          </button>

          <button
            type="button"
            onClick={() => {
              console.log("Preview Content:", content); // ✅ Debugging
              setShowPreview(true);
            }}
            className="w-28 px-2 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition duration-300"
          >
            Preview
          </button>
        </div>
      </form>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className=" font-roboto-slab bg-white p-6 rounded-lg w-[80%] max-w-2xl shadow-lg max-h-[80vh] overflow-hidden">
            <h2 className="text-2xl font-bold mb-4">{title || "Untitled"}</h2>
            <div className="border p-4 rounded-lg min-h-[200px] max-h-[60vh] overflow-y-auto">
              <style>
                {`
      h1 {
        font-size: 1.75em;
        font-weight: bold;
      }

      h2 {
        font-size: 1.40em;
        font-weight: bold;
      }

      ol {
        padding-left: 20px;
        list-style-type: decimal;
      }

      ul {
        padding-left: 20px;
        list-style-type: disc; 
      }

      li {
        margin-bottom: 2px;
      }
    `}
              </style>

              {parse(content)}
            </div>
            <div className=" font-roboto-slab flex justify-end gap-4 mt-4">
              <button
                onClick={() => setShowPreview(false)}
                className="px-4 py-2 bg-gray-400 text-white rounded-lg hover:bg-gray-500 transition duration-300"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Write;
