import React from 'react';
import { motion } from 'framer-motion';

const SuccessScreen = ({ url }) => {
  return (
    <div className="container" style={{ 
      height: '80vh', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      alignItems: 'center',
      textAlign: 'center'
    }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.8 }}
      >
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '4rem', marginBottom: '1rem' }}>
          It is finished.
        </h1>
        
        <p style={{ fontSize: '1.2rem', maxWidth: '600px', margin: '0 auto 3rem', opacity: 0.8 }}>
          Your interpretation has been generated. It is no longer just data; it is a fingerprint.
        </p>

        <a 
          href={url} 
          target="_blank" 
          rel="noopener noreferrer"
          style={{
            display: 'inline-block',
            padding: '1rem 3rem',
            backgroundColor: 'black',
            color: 'white',
            border: '1px solid black',
            borderRadius: '50px',
            fontSize: '1.1rem',
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            transition: 'all 0.3s ease',
            cursor: 'pointer'
          }}
        >
          View Your Site
        </a>
        
        <div style={{ marginTop: '2rem' }}>
          <button 
            onClick={() => window.location.reload()}
            style={{
              background: 'transparent',
              border: 'none',
              textDecoration: 'underline',
              cursor: 'pointer',
              opacity: 0.6,
              fontSize: '0.9rem'
            }}
          >
            Create another
          </button>
        </div>
      </motion.div>
    </div>
  );
};

export default SuccessScreen;
