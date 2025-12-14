import React from 'react';
import { motion } from 'framer-motion';

const AboutUsPage = () => {
  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '800px' }}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>About Us</h1>
        
        <div style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
          <p>We created Plato because we were terrified.</p>
          <p>We looked around and saw a professional world that was slowly turning into a hall of mirrors. Resumes looked the same. Portfolios looked the same. Even the "personal" bios sounded like they were written by the same low-temperature language model.</p>
          
          <p>Humans are becoming mere duplicates. We are optimizing ourselves for search engines and applicant tracking systems, shaving off the very irregularities that make us valuable.</p>
          
          <p>We believe that in an age of artificial intelligence, the most dangerous thing you can be is average. The most risky strategy is to fit in.</p>
          
          <p>We built this tool to fight the drift toward uniformity. To prove that even in a digital world, the human signal can still cut through the noise—if you know how to amplify it.</p>
          
          <p>We are a small team of designers, engineers, and writers who believe that technology should help us be more human, not less.</p>
        </div>
      </motion.div>
    </div>
  );
};

export default AboutUsPage;
