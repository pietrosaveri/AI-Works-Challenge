import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();
  
  const isActive = (path) => location.pathname === path;

  return (
    <nav style={{ 
      padding: '2rem 0', 
      display: 'flex', 
      justifyContent: 'space-between', 
      alignItems: 'center',
      maxWidth: '1200px',
      margin: '0 auto',
      paddingLeft: '2rem',
      paddingRight: '2rem'
    }}>
      <Link to="/" style={{ 
        fontFamily: 'var(--font-display)', 
        fontSize: '2.5rem',
        textDecoration: 'none'
      }}>
        Plato
      </Link>
      
      <div style={{ display: 'flex', gap: '2rem', fontSize: '0.9rem', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
        <Link to="/philosophy" style={{ opacity: isActive('/philosophy') ? 1 : 0.6 }}>Philosophy</Link>
        <Link to="/how-we-do-it" style={{ opacity: isActive('/how-we-do-it') ? 1 : 0.6 }}>Method</Link>
        <Link to="/about-us" style={{ opacity: isActive('/about-us') ? 1 : 0.6 }}>About</Link>
        <Link to="/start" style={{ 
          border: '1px solid currentColor', 
          padding: '0.5rem 1.5rem', 
          borderRadius: '50px',
          opacity: isActive('/start') ? 1 : 0.8
        }}>Begin</Link>
      </div>
    </nav>
  );
};

export default Navigation;
