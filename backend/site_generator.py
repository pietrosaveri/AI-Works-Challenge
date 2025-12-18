import os
import shutil
import json
import subprocess

# Directories
GENERATED_SITE_DIR = os.path.abspath("generated_site")


def generate_dynamic_website(react_components: dict, user_name: str, image_paths: list = None, site_data: dict = None) -> bool:
    """
    Professional Site Generator: Creates a standalone Node.js/React/Vite project.
    
    Args:
        react_components: Dictionary with React component code (App.jsx, etc.) or string (legacy HTML)
        user_name: User's name for directory/file naming
        image_paths: List of paths to uploaded images
        site_data: Dictionary containing the site data (design_dna, content_strategy, etc.)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print(f"\n{'='*80}")
        print(f"🏗️  CREATING STANDALONE NODE.JS PROJECT FOR: {user_name}")
        print(f"{'='*80}\n")
        
        # Clean output directory
        if os.path.exists(GENERATED_SITE_DIR):
            print("🧹 Cleaning old generated_site directory...")
            shutil.rmtree(GENERATED_SITE_DIR)
        os.makedirs(GENERATED_SITE_DIR)
        
        # Create project structure
        src_dir = os.path.join(GENERATED_SITE_DIR, "src")
        public_dir = os.path.join(GENERATED_SITE_DIR, "public")
        assets_dir = os.path.join(public_dir, "assets")
        components_dir = os.path.join(src_dir, "components")
        data_dir = os.path.join(src_dir, "data")
        
        for dir_path in [src_dir, public_dir, assets_dir, components_dir, data_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        print("✅ Created project structure")
        
        # Generate package.json
        package_json = {
            "name": f"portfolio-{user_name.lower().replace(' ', '-')[:30]}",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "framer-motion": "^10.16.0"
            },
            "devDependencies": {
                "@vitejs/plugin-react": "^4.2.1",
                "vite": "^5.0.0"
            }
        }
        
        with open(os.path.join(GENERATED_SITE_DIR, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        print("✅ Generated package.json")
        
        # Generate vite.config.js
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})
"""
        with open(os.path.join(GENERATED_SITE_DIR, "vite.config.js"), "w") as f:
            f.write(vite_config)
        print("✅ Generated vite.config.js")
        
        # Generate index.html
        design_dna = site_data.get('design_dna', {}) if site_data else {}
        typography = design_dna.get('typography_pair', {})
        heading_font = typography.get('heading', 'Inter')
        body_font = typography.get('body', 'Inter')
        
        index_html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{user_name} - Professional Portfolio</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={heading_font.replace(' ', '+')}:wght@400;700;900&family={body_font.replace(' ', '+')}:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
        with open(os.path.join(GENERATED_SITE_DIR, "index.html"), "w") as f:
            f.write(index_html)
        print("✅ Generated index.html")
        
        # Generate index.css
        index_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

* {
  box-sizing: border-box;
}
"""
        with open(os.path.join(src_dir, "index.css"), "w") as f:
            f.write(index_css)
        print("✅ Generated index.css")
        
        # Save site data
        if site_data:
            data_path = os.path.join(data_dir, "site_data.json")
            with open(data_path, 'w', encoding='utf-8') as f:
                json.dump(site_data, f, indent=2)
            print(f"✅ Saved site data")
        
        # Copy images to assets
        copied_images = []
        if image_paths:
            for img_path in image_paths:
                if os.path.exists(img_path):
                    filename = os.path.basename(img_path)
                    dest_path = os.path.join(assets_dir, filename)
                    shutil.copy2(img_path, dest_path)
                    copied_images.append(filename)
            print(f"📸 Copied {len(copied_images)} images")
        
        # Copy frontend assets (fonts, etc.)
        frontend_assets = os.path.join("frontend", "src", "assets")
        if os.path.exists(frontend_assets):
            try:
                for item in os.listdir(frontend_assets):
                    s = os.path.join(frontend_assets, item)
                    d = os.path.join(assets_dir, item)
                    if os.path.isdir(s):
                        if os.path.exists(d):
                            shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                print(f"✅ Copied frontend assets")
            except Exception as e:
                print(f"⚠️  Failed to copy frontend assets: {e}")
        
        # Generate React components
        if isinstance(react_components, dict):
            # Write main.jsx
            main_jsx = react_components.get('main.jsx', _default_main_jsx())
            with open(os.path.join(src_dir, "main.jsx"), "w") as f:
                f.write(main_jsx)
            
            # Write App.jsx
            app_jsx = react_components.get('App.jsx', _default_app_jsx(site_data))
            with open(os.path.join(src_dir, "App.jsx"), "w") as f:
                f.write(app_jsx)
            
            # Write additional components
            comp_count = 0
            for comp_name, comp_code in react_components.items():
                if comp_name not in ['main.jsx', 'App.jsx']:
                    comp_path = os.path.join(components_dir, comp_name)
                    with open(comp_path, "w") as f:
                        f.write(comp_code)
                    comp_count += 1
            print(f"✅ Generated React components ({comp_count} additional)")
        else:
            # Use default components
            with open(os.path.join(src_dir, "main.jsx"), "w") as f:
                f.write(_default_main_jsx())
            with open(os.path.join(src_dir, "App.jsx"), "w") as f:
                f.write(_default_app_jsx(site_data))
            print("✅ Generated default React components")
        
        # Install dependencies
        print("\n📦 Installing npm dependencies...")
        print("⏳ This may take a minute...")
        try:
            result = subprocess.run(
                ["npm", "install", "--legacy-peer-deps"],
                cwd=GENERATED_SITE_DIR,
                capture_output=True,
                text=True,
                timeout=180
            )
            if result.returncode == 0:
                print("✅ npm install completed successfully")
            else:
                print(f"⚠️  npm install had issues (but continuing): {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            print("⚠️  npm install timed out (but might still complete)")
        except Exception as e:
            print(f"⚠️  npm install error: {e}")
        
        # Create README
        readme_content = f"""# {user_name} - Professional Portfolio

This is a standalone React/Vite project generated by Plato.

## Quick Start

### Development
\`\`\`bash
npm run dev
\`\`\`

Visit: http://localhost:3000

### Build for Production
\`\`\`bash
npm run build
\`\`\`

### Preview Production Build
\`\`\`bash
npm run preview
\`\`\`

## Tech Stack
- React 18
- Vite
- Framer Motion
- Tailwind CSS

## Structure
- \`src/App.jsx\` - Main application component
- \`src/components/\` - React components
- \`src/data/site_data.json\` - Content and configuration
- \`public/assets/\` - Images and static assets
"""
        with open(os.path.join(GENERATED_SITE_DIR, "README.md"), "w") as f:
            f.write(readme_content)
        
        print(f"\n{'='*80}")
        print(f"✅ SUCCESS! Standalone project created")
        print(f"{'='*80}")
        print(f"\n📝 To run the site:")
        print(f"   cd {GENERATED_SITE_DIR}")
        print(f"   npm run dev")
        print(f"\n🌐 Then visit: http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Site generation error: {e}")
        import traceback
        traceback.print_exc()
        return False


def _default_main_jsx():
    """Default main.jsx"""
    return """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""


def _default_app_jsx(site_data):
    """Generate comprehensive App.jsx that displays ALL content sections"""
    user_name = site_data.get('user_name', 'Professional') if site_data else 'Professional'
    design_dna = site_data.get('design_dna', {}) if site_data else {}
    
    colors = design_dna.get('color_palette', ['#0071e3', '#fff', '#2997ff', '#000', '#f5f5f7'])
    typography = design_dna.get('typography_pair', {'heading': 'Inter', 'body': 'Inter'})
    
    # Build comprehensive component that renders all sections
    component = """import React, {{ useState }} from 'react'
import {{ motion, AnimatePresence }} from 'framer-motion'
import siteData from './data/site_data.json'

function App() {{
  const [currentPage, setCurrentPage] = useState('home')
  
  const colors = {colors_json}
  const typography = {typography_json}
  
  // Extract all content sections
  const content = siteData.content_strategy?.pages || {{}}
  const home = content.home || {{}}
  const patterns = content.behavioral_patterns?.patterns || []
  const antiClaims = content.anti_claims?.anti_claims || []
  const failures = content.failures_and_lessons?.failures || []
  const decisions = content.decision_architecture?.decisions || []
  const method = content.proprietary_method?.method || {{}}
  const about = content.about || {{}}
  
  // Build navigation dynamically based on available content
  const navItems = [
    {{ id: 'home', label: 'Home' }},
    patterns.length > 0 && {{ id: 'patterns', label: 'Patterns', count: patterns.length }},
    antiClaims.length > 0 && {{ id: 'anticlaims', label: 'Anti-Claims', count: antiClaims.length }},
    failures.length > 0 && {{ id: 'failures', label: 'Failures', count: failures.length }},
    decisions.length > 0 && {{ id: 'decisions', label: 'Decisions', count: decisions.length }},
    method.method_name && {{ id: 'method', label: 'Method' }},
    {{ id: 'about', label: 'About' }}
  ].filter(Boolean)
  
  return (
    <div style={{{{ 
      minHeight: '100vh',
      background: colors[3],
      color: colors[4],
      fontFamily: typography.body
    }}}}>
      {{/* Navigation */}}
      <nav style={{{{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        background: 'rgba(0, 0, 0, 0.9)',
        backdropFilter: 'blur(20px)',
        borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        zIndex: 50
      }}}}>
        <div style={{{{
          maxWidth: '1400px',
          margin: '0 auto',
          padding: '1rem 2rem',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem'
        }}}}>
          <h1 style={{{{
            fontFamily: typography.heading,
            fontSize: '1.5rem',
            fontWeight: 'bold',
            background: `linear-gradient(135deg, ${{colors[0]}}, ${{colors[2]}})`,
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}}}>
            {user_name}
          </h1>
          <div style={{{{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}}}>
            {{navItems.map(item => (
              <button
                key={{item.id}}
                onClick={{() => setCurrentPage(item.id)}}
                style={{{{
                  background: 'none',
                  border: 'none',
                  color: currentPage === item.id ? colors[2] : colors[4],
                  cursor: 'pointer',
                  fontSize: '0.9rem',
                  opacity: currentPage === item.id ? 1 : 0.7,
                  transition: 'all 0.3s',
                  fontWeight: currentPage === item.id ? '600' : '400'
                }}}}
              >
                {{item.label}} {{item.count > 0 && `(${{item.count}})`}}
              </button>
            ))}}
          </div>
        </div>
      </nav>
      
      {{/* Content */}}
      <div style={{{{ paddingTop: '80px' }}}}>
        <AnimatePresence mode="wait">
          {{/* HOME PAGE */}}
          {{currentPage === 'home' && (
            <motion.div
              key="home"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                lineHeight: 1.2,
                marginBottom: '2rem'
              }}}}>
                {{home.thesis || 'Welcome'}}
              </h2>
              {{home.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '1.5rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
            </motion.div>
          )}}
          
          {{/* PATTERNS PAGE */}}
          {{currentPage === 'patterns' && (
            <motion.div
              key="patterns"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.behavioral_patterns?.page_title || 'Behavioral Patterns'}}
              </h2>
              {{content.behavioral_patterns?.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.8, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
              <div style={{{{ display: 'grid', gap: '2rem' }}}}>
                {{patterns.map((pattern, i) => (
                  <div key={{i}} style={{{{
                    background: 'rgba(255, 255, 255, 0.03)',
                    padding: '2rem',
                    borderRadius: '1rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}}}>
                    <h3 style={{{{ fontSize: '1.5rem', marginBottom: '0.5rem', color: colors[2] }}}}>
                      {{pattern.name}}
                    </h3>
                    <p style={{{{ fontSize: '1rem', opacity: 0.7, marginBottom: '1rem', fontStyle: 'italic' }}}}>
                      {{pattern.summary}}
                    </p>
                    {{pattern.analysis?.map((point, j) => (
                      <p key={{j}} style={{{{ fontSize: '1rem', marginBottom: '0.75rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                        • {{point}}
                      </p>
                    ))}}
                    {{pattern.evidence_quotes && pattern.evidence_quotes.length > 0 && (
                      <div style={{{{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}}}>
                        {{pattern.evidence_quotes.map((quote, k) => (
                          <blockquote key={{k}} style={{{{ 
                            fontSize: '0.95rem', 
                            opacity: 0.7, 
                            fontStyle: 'italic',
                            borderLeft: `3px solid ${{colors[2]}}`,
                            paddingLeft: '1rem',
                            marginTop: '0.5rem'
                          }}}}>
                            "{{quote}}"
                          </blockquote>
                        ))}}
                      </div>
                    )}}
                  </div>
                ))}}
              </div>
            </motion.div>
          )}}
          
          {{/* ANTI-CLAIMS PAGE */}}
          {{currentPage === 'anticlaims' && (
            <motion.div
              key="anticlaims"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.anti_claims?.page_title || 'Anti-Claims'}}
              </h2>
              {{content.anti_claims?.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.8, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
              <div style={{{{ display: 'grid', gap: '2rem' }}}}>
                {{antiClaims.map((claim, i) => (
                  <div key={{i}} style={{{{
                    background: 'rgba(255, 255, 255, 0.03)',
                    padding: '2rem',
                    borderRadius: '1rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}}}>
                    <h3 style={{{{ fontSize: '1.5rem', marginBottom: '0.5rem', color: colors[2] }}}}>
                      {{claim.what_i_dont_do}}
                    </h3>
                    <p style={{{{ fontSize: '1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                      {{claim.why_i_refuse}}
                    </p>
                    {{claim.what_this_reveals && (
                      <p style={{{{ fontSize: '1rem', opacity: 0.7, fontStyle: 'italic', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}}}>
                        → {{claim.what_this_reveals}}
                      </p>
                    )}}
                  </div>
                ))}}
              </div>
            </motion.div>
          )}}
          
          {{/* FAILURES PAGE */}}
          {{currentPage === 'failures' && (
            <motion.div
              key="failures"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.failures_and_lessons?.page_title || 'Failures & Lessons'}}
              </h2>
              {{content.failures_and_lessons?.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.8, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
              <div style={{{{ display: 'grid', gap: '2rem' }}}}>
                {{failures.map((failure, i) => (
                  <div key={{i}} style={{{{
                    background: 'rgba(255, 255, 255, 0.03)',
                    padding: '2rem',
                    borderRadius: '1rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}}}>
                    <h3 style={{{{ fontSize: '1.5rem', marginBottom: '0.5rem', color: colors[2] }}}}>
                      {{failure.situation}}
                    </h3>
                    <p style={{{{ fontSize: '1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                      <strong>What went wrong:</strong> {{failure.what_went_wrong}}
                    </p>
                    <p style={{{{ fontSize: '1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                      <strong>What I learned:</strong> {{failure.what_i_learned}}
                    </p>
                    {{failure.how_i_apply_it_now && (
                      <p style={{{{ fontSize: '1rem', opacity: 0.7, fontStyle: 'italic', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}}}>
                        → {{failure.how_i_apply_it_now}}
                      </p>
                    )}}
                  </div>
                ))}}
              </div>
            </motion.div>
          )}}
          
          {{/* DECISIONS PAGE */}}
          {{currentPage === 'decisions' && (
            <motion.div
              key="decisions"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.decision_architecture?.page_title || 'Decision Architecture'}}
              </h2>
              {{content.decision_architecture?.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.8, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
              <div style={{{{ display: 'grid', gap: '2rem' }}}}>
                {{decisions.map((decision, i) => (
                  <div key={{i}} style={{{{
                    background: 'rgba(255, 255, 255, 0.03)',
                    padding: '2rem',
                    borderRadius: '1rem',
                    border: '1px solid rgba(255, 255, 255, 0.1)'
                  }}}}>
                    <h3 style={{{{ fontSize: '1.5rem', marginBottom: '0.5rem', color: colors[2] }}}}>
                      {{decision.decision}}
                    </h3>
                    <p style={{{{ fontSize: '1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                      <strong>Why:</strong> {{decision.why}}
                    </p>
                    {{decision.alternative_i_rejected && (
                      <p style={{{{ fontSize: '1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                        <strong>Alternative rejected:</strong> {{decision.alternative_i_rejected}}
                      </p>
                    )}}
                    {{decision.what_this_reveals && (
                      <p style={{{{ fontSize: '1rem', opacity: 0.7, fontStyle: 'italic', paddingTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}}}>
                        → {{decision.what_this_reveals}}
                      </p>
                    )}}
                  </div>
                ))}}
              </div>
            </motion.div>
          )}}
          
          {{/* METHOD PAGE */}}
          {{currentPage === 'method' && (
            <motion.div
              key="method"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.proprietary_method?.page_title || 'My Method'}}
              </h2>
              {{content.proprietary_method?.introduction?.map((para, i) => (
                <p key={{i}} style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.8, lineHeight: 1.6 }}}}>
                  {{para}}
                </p>
              ))}}
              {{method.method_name && (
                <h3 style={{{{ fontSize: '1.8rem', marginBottom: '1rem', color: colors[2] }}}}>
                  {{method.method_name}}
                </h3>
              )}}
              {{method.overview && (
                <p style={{{{ fontSize: '1.1rem', marginBottom: '2rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                  {{method.overview}}
                </p>
              )}}
              {{method.steps && method.steps.length > 0 && (
                <div style={{{{ display: 'grid', gap: '1.5rem', marginTop: '2rem' }}}}>
                  {{method.steps.map((step, i) => (
                    <div key={{i}} style={{{{
                      background: 'rgba(255, 255, 255, 0.03)',
                      padding: '1.5rem',
                      borderRadius: '1rem',
                      border: '1px solid rgba(255, 255, 255, 0.1)'
                    }}}}>
                      <h4 style={{{{ fontSize: '1.2rem', marginBottom: '0.5rem', color: colors[2] }}}}>
                        Step {{i + 1}}: {{step.name}}
                      </h4>
                      <p style={{{{ fontSize: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                        {{step.description}}
                      </p>
                    </div>
                  ))}}
                </div>
              )}}
            </motion.div>
          )}}
          
          {{/* ABOUT PAGE */}}
          {{currentPage === 'about' && (
            <motion.div
              key="about"
              initial={{{{ opacity: 0, y: 20 }}}}
              animate={{{{ opacity: 1, y: 0 }}}}
              exit={{{{ opacity: 0, y: -20 }}}}
              style={{{{
                maxWidth: '1200px',
                margin: '0 auto',
                padding: '4rem 2rem'
              }}}}
            >
              <h2 style={{{{
                fontFamily: typography.heading,
                fontSize: '2.5rem',
                marginBottom: '1rem'
              }}}}>
                {{content.about?.page_title || 'About'}}
              </h2>
              {{content.about?.sections?.map((section, i) => (
                <div key={{i}} style={{{{ marginBottom: '2rem' }}}}>
                  {{section.heading && (
                    <h3 style={{{{ fontSize: '1.5rem', marginBottom: '1rem', color: colors[2] }}}}>
                      {{section.heading}}
                    </h3>
                  )}}
                  {{section.content?.map((para, j) => (
                    <p key={{j}} style={{{{ fontSize: '1.1rem', marginBottom: '1rem', opacity: 0.9, lineHeight: 1.6 }}}}>
                      {{para}}
                    </p>
                  ))}}
                </div>
              ))}}
            </motion.div>
          )}}
        </AnimatePresence>
      </div>
    </div>
  )
}}

export default App
"""
    
    return component.format(
        colors_json=json.dumps(colors[:5]),
        typography_json=json.dumps(typography),
        user_name=user_name
    )
