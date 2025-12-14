import React from 'react';
import { motion } from 'framer-motion';

const PhilosophyPage = () => {
  return (
    <div className="container" style={{ padding: '4rem 2rem', maxWidth: '800px' }}>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.8 }}
      >
        <h1 style={{ fontFamily: 'var(--font-display)', fontSize: '3rem', marginBottom: '3rem', textAlign: 'center' }}>Our Philosophy</h1>
        
        <div style={{ fontSize: '1.1rem', lineHeight: '1.8' }}>
          <p>At Plato, we believe the traditional portfolio is a historical artifact.</p>
          <p>It was designed for a world where information was scarce, careers were linear, and humans were evaluated through titles, timelines, and lists of skills. That world no longer exists.</p>
          <p>Today, AI can write resumes, optimize keywords, and generate “perfect” candidate profiles in seconds. If everyone can look impressive, impressiveness stops meaning anything.</p>
          
          <div style={{ margin: '3rem 0', textAlign: 'center', fontStyle: 'italic' }}>
            <p>So we asked a different question.</p>
            <p>What if AI had always existed?</p>
            <p>What would actually be worth showing then?</p>
          </div>

          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>From representation to interpretation</h2>
          <p>Plato does not create portfolios. It creates interpretations.</p>
          <p>A resume represents what you did. Plato interprets how you think.</p>
          <p>We are not interested in job titles, seniority levels, or exhaustive timelines. Those are proxies — and increasingly bad ones. What actually differentiates people today is not what they have done, but how they consistently approach problems, decisions, uncertainty, and failure.</p>
          <p>That is what Plato is designed to surface.</p>

          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>The professional fingerprint</h2>
          <p>Every person leaves a trace.</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: '1rem 0' }}>
            <li>A way of entering problems.</li>
            <li>A way of making trade-offs.</li>
            <li>A way of failing — and changing because of it.</li>
            <li>A way of working with others that either amplifies or constrains them.</li>
          </ul>
          <p>We call this a professional fingerprint. It cannot be copied. It cannot be optimized away. And it cannot be captured by a CV.</p>
          <p>Plato is built to extract that fingerprint by looking at patterns, not achievements. Decisions, not titles. Friction, not polish.</p>

          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>Why we focus on process, not output</h2>
          <p>Outputs lie. A successful project can hide poor thinking. A failed project can reveal exceptional judgment.</p>
          <p>Plato intentionally shifts the focus:</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: '1rem 0' }}>
            <li>from results to reasoning</li>
            <li>from highlights to trade-offs</li>
            <li>from success stories to decision logs and failures</li>
          </ul>
          <p>Because in real work, especially in complex environments, process predicts outcomes better than past outputs.</p>

          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>Anti-standardization by design</h2>
          <p>Most portfolio tools try to standardize uniqueness. Plato does the opposite.</p>
          <p>Every site generated is structurally similar enough to be readable, but conceptually different enough to be unmistakably personal. The system is designed to:</p>
          <ul style={{ listStyle: 'none', padding: 0, margin: '1rem 0' }}>
            <li>remove job titles entirely</li>
            <li>reject chronological storytelling</li>
            <li>force selection instead of accumulation</li>
            <li>surface boundaries, not just strengths</li>
          </ul>
          <p>We believe clarity comes from subtraction.</p>

          <h2 style={{ fontSize: '1.5rem', marginTop: '3rem', marginBottom: '1rem', fontFamily: 'var(--font-display)' }}>The role of AI in Plato</h2>
          <p>Plato is AI-native — not AI-assisted.</p>
          <p>AI is not used to “enhance” a CV or rewrite a bio. It is used as an analytical instrument: to detect behavioral patterns, to identify contradictions, to infer decision-making styles, to name methods people already use but never articulated.</p>
        </div>
      </motion.div>
    </div>
  );
};

export default PhilosophyPage;
