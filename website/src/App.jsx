import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Header from "./components/Header";
import Title from "./components/Title";
import Socials from "./components/Socials";
import YoutubeVideo from "./components/YoutubeVideo";
import Download from "./components/Download";
import About from "./pages/About";
import Team from "./pages/Team";
import Footer from "./components/Footer";
import Leaderboard from "./pages/Leaderboard";
import FallingItems from "./components/FallingItems";

const App = () => {
  return (
    <Router>
      {/* Header is displayed on all pages */}
      <Header />
      <div className="pt-[7.5rem] lg:pt-[8rem] overflow-hidden min-h-screen bg-primary-blue">
        <div className="absolute top-0 left-0 w-full h-full z-0">
          <FallingItems />
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
                  <YoutubeVideo />
                  <div className="flex justify-center items-center mt-10 mb-10">
                    <Download />
                  </div>
                </main>
              </>
            }
          />

          {/* About Page */}
          <Route path="/about" element={<About />} />

          {/* Team Page */}
          <Route path="/team" element={<Team />} />

          {/* Leaderboard Page */}
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Routes>
      </div>
      <Footer />
    </Router>
  );
};

export default App;
