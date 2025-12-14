import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const LandingPage = () => {
  return (
    <div className="container" style={{ 
      minHeight: '80vh', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center',
      textAlign: 'center'
    }}>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1 }}
      >
        <h1 style={{ 
          fontFamily: 'var(--font-main)', 
          fontSize: 'clamp(2rem, 5vw, 4rem)', 
          fontWeight: 'normal',
          marginBottom: '2rem',
          maxWidth: '800px',
          lineHeight: '1.2'
        }}>
          You are not a list of bullet points.<br/>
          <span style={{ fontStyle: 'italic', fontFamily: 'var(--font-display)', fontSize: '1.2em' }}>Stop acting like one.</span>
        </h1>
        
        <p style={{ 
          fontSize: '1.2rem', 
          maxWidth: '600px', 
          margin: '0 auto 3rem', 
          opacity: 0.8 
        }}>
          In a world of AI-generated perfection, the only thing that matters is your unique professional fingerprint. We help you find it.
        </p>

        <Link to="/start" style={{
          display: 'inline-block',
          padding: '1rem 3rem',
          border: '1px solid currentColor',
          borderRadius: '50px',
          fontSize: '1rem',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          transition: 'all 0.3s ease'
        }}>
          Create your interpretation
        </Link>

        <div style={{ 
          marginTop: '4rem', 
          fontFamily: 'var(--font-display)', 
          fontSize: '6rem',
          opacity: 0.9
        }}>
          Plato
        </div>
      </motion.div>
    </div>
  );
};

export default LandingPage;
