import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const agents = [
  "Mood Agent is analyzing your aesthetic resonance...",
  "Content Strategist is extracting your narrative arc...",
  "UX Architect is structuring your digital fingerprint...",
  "Icon Curator is selecting symbolic representations...",
  "React Developer is coding your unique interpretation...",
  "Orchestrator is conducting the final review..."
];

const quotes = [
  { text: "Simplicity is the ultimate sophistication.", author: "Leonardo da Vinci" },
  { text: "Design is not just what it looks like and feels like. Design is how it works.", author: "Steve Jobs" },
  { text: "Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away.", author: "Antoine de Saint-Exupéry" },
  { text: "The details are not the details. They make the design.", author: "Charles Eames" },
  { text: "Less is more.", author: "Mies van der Rohe" }
];

const LoadingScreen = () => {
  const [agentIndex, setAgentIndex] = useState(0);
  const [quoteIndex, setQuoteIndex] = useState(0);

  useEffect(() => {
    const agentInterval = setInterval(() => {
      setAgentIndex((prev) => (prev + 1) % agents.length);
    }, 3000);

    const quoteInterval = setInterval(() => {
      setQuoteIndex((prev) => (prev + 1) % quotes.length);
    }, 5000);

    return () => {
      clearInterval(agentInterval);
      clearInterval(quoteInterval);
    };
  }, []);

  return (
    <div className="container" style={{ 
      height: '80vh', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center',
      textAlign: 'center'
    }}>
      <div style={{ marginBottom: '4rem' }}>
        <div className="spinner" style={{ 
          width: '50px', 
          height: '50px', 
          border: '2px solid rgba(0,0,0,0.1)', 
          borderTop: '2px solid black', 
          borderRadius: '50%', 
          animation: 'spin 1s linear infinite',
          margin: '0 auto 2rem'
        }} />
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
        
        <AnimatePresence mode="wait">
          <motion.div
            key={agentIndex}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.5 }}
            style={{ fontFamily: 'var(--font-display)', fontSize: '1.5rem' }}
          >
            {agents[agentIndex]}
          </motion.div>
        </AnimatePresence>
      </div>

      <div style={{ maxWidth: '600px', padding: '0 2rem' }}>
        <AnimatePresence mode="wait">
          <motion.div
            key={quoteIndex}
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
          >
            <p style={{ fontSize: '1.1rem', fontStyle: 'italic', marginBottom: '1rem' }}>
              "{quotes[quoteIndex].text}"
            </p>
            <p style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              — {quotes[quoteIndex].author}
            </p>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default LoadingScreen;
