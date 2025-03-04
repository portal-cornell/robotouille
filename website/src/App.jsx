import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Title from "./components/Title";
import Socials from "./components/Socials";
import YoutubeVideo from "./components/YoutubeVideo";
import Download from "./components/Download";
import About from "./pages/About";
import Team from "./pages/Team";
import Blog from "./pages/Blog";
import Footer from "./components/Footer";
import Leaderboard from "./pages/Leaderboard";
import FallingItems from "./components/FallingItems";

const App = () => {
  const [animationEnabled, setAnimationEnabled] = useState(true);

  return (
    <Router>
      {/* Header is displayed on all pages */}
      <Header />
      <div className="pt-[7.5rem] lg:pt-[8rem] overflow-hidden min-h-screen bg-primary-blue relative">
        {/* Falling Items */}
        <div className="absolute top-0 left-0 w-full h-full z-0">
          <FallingItems
            key={animationEnabled ? 1 : 0}
            animationEnabled={animationEnabled}
            staggered={true}
          />
        </div>

        {/* Content Above Falling Items */}
        <div className="relative z-10">
          <div className="flex justify-end mr-10 -mt-20">
            <button
            className="border-2 border-primary-darkBlue text-primary-darkBlue px-2 py-1 hover:bg-primary-darkBlue hover:text-white rounded-lg font-roboto transition duration-300"              onClick={() => setAnimationEnabled(!animationEnabled)}
            >
              {animationEnabled ? "Pause Animation" : "Resume Animation"}
            </button>
          </div>
          <Title />
          <Socials />
          <Routes>
            {/* Home Page */}
            <Route
              path="/"
              element={
                <>
                  <main>
                    <div className="flex flex-col items-center justify-center h-64 mt-10">
                      <button className="bg-primary-darkRed text-white px-6 py-3 text-lg rounded-lg cursor-not-allowed">
                        Coming Soon...
                      </button>
                    </div>
                  </main>
                </>
              }
            />
            {/* About Page */}
            <Route path="/about" element={<About />} />
            {/* Team Page */}
            <Route path="/team" element={<Team />} />
            {/* Blog Page */}
            <Route path="/blog" element={<Blog />} />
            {/* Leaderboard Page
            <Route path="/leaderboard" element={<Leaderboard />} /> */}
          </Routes>
        </div>
      </div>
      <Footer />
    </Router>
  );
};

export default App;
