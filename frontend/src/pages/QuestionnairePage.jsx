import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LoadingScreen from '../components/LoadingScreen';
import SuccessScreen from '../components/SuccessScreen';

const questions = [
  {
    id: 'files',
    type: 'file',
    question: "Upload your documents (CV, Slides, etc.)",
    subtext: "We'll read them to understand your background. (Optional)"
  },
  {
    id: 'github',
    type: 'text',
    question: "GitHub URL (Optional)",
    placeholder: "https://github.com/...",
    subtext: "Show us your code."
  },
  {
    id: 'linkedin',
    type: 'text',
    question: "LinkedIn URL (Optional)",
    placeholder: "https://linkedin.com/in/...",
    subtext: "Your professional network."
  },
  {
    id: 'website',
    type: 'text',
    question: "Personal Site / Other (Optional)",
    placeholder: "https://...",
    subtext: "Any other links you want to share."
  },
  {
    id: 'hobbies',
    type: 'textarea',
    question: "Tell us about your Hobbies, passions, and so on",
    placeholder: "I run marathons, I paint, I play chess...",
    subtext: "What do you do when you're not working? (Optional)"
  },
  {
    id: 'love_work',
    type: 'textarea',
    question: "What do you love about your study/work field?",
    placeholder: "The problem solving, the creativity...",
    subtext: "(Optional)"
  },
  {
    id: 'mistake',
    type: 'textarea',
    question: "What is the biggest mistake you've made, and what did it teach you?",
    placeholder: "I once...",
    subtext: "We value scars over medals. (Optional)"
  },
  {
    id: 'identity',
    type: 'textarea',
    question: "Who are you, really? (Beyond the job title)",
    placeholder: "I am a...",
    subtext: "(Optional)"
  },
  {
    id: 'color',
    type: 'text',
    question: "Favorite Color",
    placeholder: "Blue, #0000FF...",
    subtext: "(Optional)"
  },
  {
    id: 'animal',
    type: 'text',
    question: "Animal That Describes You",
    placeholder: "Wolf, Eagle...",
    subtext: "(Optional)"
  },
  {
    id: 'abstract_word',
    type: 'text',
    question: "One Abstract Word That Represents You",
    placeholder: "Resilience, Chaos...",
    subtext: "(Optional)"
  }
];

const QuestionnairePage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [formData, setFormData] = useState({
    files: [],
    github: '',
    linkedin: '',
    website: '',
    hobbies: '',
    love_work: '',
    mistake: '',
    identity: '',
    color: '',
    animal: '',
    abstract_word: ''
  });
  const [status, setStatus] = useState('idle'); // idle, submitting, success, error
  const [resultUrl, setResultUrl] = useState('');

  const handleNext = () => {
    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleSubmit();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    setFormData(prev => ({ ...prev, files: Array.from(e.target.files) }));
  };

  const handleSubmit = async () => {
    setStatus('submitting');
    
    const data = new FormData();
    
    // Process URLs
    const urlList = [formData.github, formData.linkedin, formData.website].filter(u => u && u.trim() !== '');
    data.append('urls', JSON.stringify(urlList));
    
    // Combine text inputs into the main text_input field for the backend
    const combinedText = `
    Identity: ${formData.identity}
    Hobbies/Passions: ${formData.hobbies}
    Love about work: ${formData.love_work}
    Biggest Mistake: ${formData.mistake}
    Favorite Color: ${formData.color}
    Animal: ${formData.animal}
    Abstract Word: ${formData.abstract_word}
    `;
    data.append('text_input', combinedText);
    
    // Pass structured answers
    const answers = {
      who_are_you: formData.identity,
      hobbies: formData.hobbies,
      love_work: formData.love_work,
      mistake: formData.mistake,
      color: formData.color,
      animal: formData.animal,
      abstract_word: formData.abstract_word
    };
    data.append('answers', JSON.stringify(answers));
    
    // Vibe derived from abstract word and color
    const vibe = {
      style: 'Minimalist', // Default base
      color_preference: formData.color,
      abstract_concept: formData.abstract_word,
      animal_archetype: formData.animal
    };
    data.append('vibe', JSON.stringify(vibe));

    formData.files.forEach(file => {
      data.append('files', file);
    });

    try {
      // Use relative path if proxied, or absolute if dev
      // Assuming standard setup where backend is on 8000
      const response = await fetch('http://127.0.0.1:8000/api/analyze', {
        method: 'POST',
        body: data,
      });
      
      if (response.ok) {
        const result = await response.json();
        // The backend returns website_url, usually /portfolio/
        // We construct the full URL for the user
        const fullUrl = `http://127.0.0.1:8000${result.website_url}`;
        setResultUrl(fullUrl);
        setStatus('success');
      } else {
        console.error('Server error');
        setStatus('error');
      }
    } catch (error) {
      console.error('Error:', error);
      setStatus('error');
    }
  };

  if (status === 'submitting') {
    return <LoadingScreen />;
  }

  if (status === 'success') {
    return <SuccessScreen url={resultUrl} />;
  }

  if (status === 'error') {
    return (
      <div className="container" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <h2>Something went wrong.</h2>
        <p>Please try again.</p>
        <button onClick={() => setStatus('idle')}>Retry</button>
      </div>
    );
  }

  const currentQ = questions[currentStep];

  return (
    <div className="container" style={{ 
      height: '80vh', 
      display: 'flex', 
      flexDirection: 'column', 
      justifyContent: 'center', 
      maxWidth: '800px' 
    }}>
      <div style={{ marginBottom: '2rem', fontSize: '0.9rem', opacity: 0.5 }}>
        {currentStep + 1} / {questions.length}
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
        >
          <h2 style={{ 
            fontFamily: 'var(--font-main)', 
            fontSize: '2.5rem', 
            marginBottom: '1rem' 
          }}>
            {currentQ.question}
          </h2>
          
          {currentQ.subtext && (
            <p style={{ marginBottom: '2rem', opacity: 0.7 }}>{currentQ.subtext}</p>
          )}

          <div style={{ marginBottom: '3rem' }}>
            {currentQ.type === 'text' && (
              <input
                type="text"
                name={currentQ.id}
                value={formData[currentQ.id]}
                onChange={handleChange}
                placeholder={currentQ.placeholder}
                autoFocus
                style={{
                  width: '100%',
                  border: 'none',
                  borderBottom: '1px solid #ccc',
                  background: 'transparent',
                  fontSize: '1.5rem',
                  padding: '0.5rem 0',
                  outline: 'none',
                  fontFamily: 'var(--font-main)'
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') handleNext();
                }}
              />
            )}

            {currentQ.type === 'textarea' && (
              <textarea
                name={currentQ.id}
                value={formData[currentQ.id]}
                onChange={handleChange}
                placeholder={currentQ.placeholder}
                autoFocus
                rows={4}
                style={{
                  width: '100%',
                  border: 'none',
                  borderBottom: '1px solid #ccc',
                  background: 'transparent',
                  fontSize: '1.5rem',
                  padding: '0.5rem 0',
                  outline: 'none',
                  fontFamily: 'var(--font-main)',
                  resize: 'none'
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleNext();
                  }
                }}
              />
            )}

            {currentQ.type === 'file' && (
              <input
                type="file"
                multiple
                onChange={handleFileChange}
                style={{
                  fontSize: '1.2rem'
                }}
              />
            )}
          </div>

          <div style={{ display: 'flex', gap: '1rem' }}>
            {currentStep > 0 && (
              <button 
                onClick={handlePrev}
                style={{
                  padding: '0.8rem 2rem',
                  border: 'none',
                  background: 'transparent',
                  cursor: 'pointer',
                  fontSize: '1rem',
                  opacity: 0.6
                }}
              >
                Back
              </button>
            )}
            <button 
              onClick={handleNext}
              style={{
                padding: '0.8rem 3rem',
                border: '1px solid currentColor',
                background: 'black',
                color: 'white',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '1.1rem'
              }}
            >
              {currentStep === questions.length - 1 ? 'Finish' : 'Next'}
            </button>
          </div>
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default QuestionnairePage;
