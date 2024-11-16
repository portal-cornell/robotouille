import Download from "./components/Download";
import Header from "./components/Header";
import Title from "./components/Title";
import Socials from "./components/Socials";
import YoutubeVideo from "./components/YoutubeVideo";
import About from "./components/About";
import Team from "./components/Team";
import Footer from "./components/Footer";

const App = () => {
  return (
    <>
      <div className="pt-[4.75rem] lg:pt-[5.25rem] overflow-hidden min-h-screen bg-primary-blue">
        <Title />
        <main className="px-4">
          <Socials colorClass="text-red-500" />
          <YoutubeVideo />
          <About />
          <Team />
          <Footer />
        </main>
      </div>
    </>
  );
};

export default App;
