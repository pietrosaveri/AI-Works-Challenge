import React from 'react';
import { motion } from 'framer-motion';

const HowWeDoItPage = () => {
  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '800px' }}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>How We Do It</h1>
        
        <div style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
          <p>We use the most advanced artificial intelligence not to replace humanity, but to reveal it.</p>
          
          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>The Paradox of AI</h2>
          <p>Usually, AI is used to smooth out edges, to make everyone sound the same—professional, polished, and predictable. We use it for the opposite purpose: to find the cracks, the quirks, and the unique friction that makes you human.</p>
          
          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>Our Multi-Agent Pipeline</h2>
          <p>Your profile isn't processed by a single algorithm. It travels through a council of specialized AI agents, each looking for something specific:</p>
          
          <div style={{ margin: '2rem 0', paddingLeft: '1rem', borderLeft: '1px solid #ccc' }}>
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>The Content Strategist</h3>
            <p style={{ fontSize: '0.95rem', marginBottom: '1.5rem' }}>Reads between the lines of your history to find the narrative arc you didn't know existed.</p>
            
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>The Mood Architect</h3>
            <p style={{ fontSize: '0.95rem', marginBottom: '1.5rem' }}>Translates your personality into a visual language—colors, spacing, and typography that feel like you.</p>
            
            <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem' }}>The Critic</h3>
            <p style={{ fontSize: '0.95rem', marginBottom: '1.5rem' }}>Challenges the other agents, ensuring the output isn't just flattering, but true.</p>
          </div>

          <p>This dialogue between agents mimics a human editorial board, working tirelessly to distill your essence into a digital format.</p>
          
          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>Turning Back to Human</h2>
          <p>By automating the superficial, we force a focus on the substantial. The result is a site that feels less like a LinkedIn profile and more like a conversation with you at your best.</p>
        </div>
      </motion.div>
    </div>
  );
};

export default HowWeDoItPage;
