import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import PhilosophyPage from './pages/PhilosophyPage';
import HowWeDoItPage from './pages/HowWeDoItPage';
import AboutUsPage from './pages/AboutUsPage';
import QuestionnairePage from './pages/QuestionnairePage';
import Navigation from './components/Navigation';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Navigation />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/philosophy" element={<PhilosophyPage />} />
          <Route path="/how-we-do-it" element={<HowWeDoItPage />} />
          <Route path="/about-us" element={<AboutUsPage />} />
          <Route path="/start" element={<QuestionnairePage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
