let profileData = {};

// Navigation
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.page-section').forEach(section => {
        section.classList.add('hidden');
        section.classList.remove('active');
    });
    
    // Show target section
    const target = document.getElementById(sectionId);
    target.classList.remove('hidden');
    target.classList.add('active');
    
    // Scroll to top
    window.scrollTo(0, 0);
}

// Form Steps
function nextStep(step) {
    document.getElementById('step-1').classList.add('hidden');
    document.getElementById('step-2').classList.remove('hidden');
    window.scrollTo(0, document.getElementById('generator').offsetTop);
}

function prevStep(step) {
    document.getElementById('step-2').classList.add('hidden');
    document.getElementById('step-1').classList.remove('hidden');
}

// Analysis Submission
async function submitAnalysis() {
    document.getElementById('step-2').classList.add('hidden');
    document.getElementById('loading').classList.remove('hidden');

    const filesInput = document.getElementById('files');
    const notesInput = document.getElementById('notes').value;
    
    // Collect URLs from separate fields
    const urlsList = [
        document.getElementById('url-github').value,
        document.getElementById('url-linkedin').value,
        document.getElementById('url-site').value
    ].map(u => u.trim()).filter(u => u); // Remove empty strings

    const answers = {
        love_work: document.getElementById('q1').value,
        biggest_mistake: document.getElementById('q2').value,
        who_are_you: document.getElementById('q3').value,
        soul_project: document.getElementById('q4').value
    };

    const vibe = {
        favorite_color: document.getElementById('fav-color').value,
        animal: document.getElementById('fav-animal').value,
        abstract_word: document.getElementById('abstract-word').value
    };

    const formData = new FormData();
    
    for (let i = 0; i < filesInput.files.length; i++) {
        formData.append('files', filesInput.files[i]);
    }

    // Append other data
    formData.append('urls', JSON.stringify(urlsList));
    formData.append('text_input', notesInput);
    formData.append('answers', JSON.stringify(answers));
    formData.append('vibe', JSON.stringify(vibe));

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            profileData = data.profile;
            renderCV(profileData);
            
            // Handle Website Button (Re-enabled for Thesis)
            const btnWebsite = document.getElementById('btn-website');
            if (data.website_ready && data.website_url) {
                btnWebsite.href = data.website_url;
                btnWebsite.classList.remove('hidden');
            } else {
                btnWebsite.classList.add('hidden');
            }

            // await generateLatex(profileData); // Disabled
        } else {
            alert('Error analyzing profile: ' + (data.detail || 'Unknown error'));
            document.getElementById('step-2').classList.remove('hidden');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred. Please check the console and ensure the backend is running.');
        document.getElementById('step-2').classList.remove('hidden');
    } finally {
        document.getElementById('loading').classList.add('hidden');
        document.getElementById('results').classList.remove('hidden');
    }
}

// Render Professional Fingerprint
function renderCV(profile) {
    const container = document.getElementById('cv-preview');
    const fp = profile.fingerprint || {};
    const meta = profile.meta || {};

    // Helpers
    const renderList = (items, titleKey, descKey, evidenceKey) => {
        if (!items || items.length === 0) return '<p>No data found.</p>';
        return items.map(item => `
            <div class="cv-project">
                <div class="cv-project-title">${item[titleKey] || item.name || item.trait || item.pair || item.conflict}</div>
                <div>${item[descKey] || item.description || item.insight}</div>
                <div style="margin-top:0.5rem; font-style:italic; color:#666;">
                    <i class="fas fa-search"></i> Evidence: "${item[evidenceKey] || item.evidence}"
                </div>
            </div>
        `).join('');
    };

    container.innerHTML = `
        <div class="cv-header">
            <h1 class="cv-name">${meta.name || 'Unknown Subject'}</h1>
            <div class="cv-tagline">${meta.inferred_role || 'Professional Fingerprint Analysis'}</div>
        </div>

        <div class="cv-section">
            <div class="cv-section-title">Recurring Patterns</div>
            <div class="cv-content">
                ${renderList(fp.patterns, 'name', 'description', 'evidence')}
            </div>
        </div>

        <div class="cv-section">
            <div class="cv-section-title">Behavioral Traits</div>
            <div class="cv-content">
                ${renderList(fp.behaviors, 'trait', 'description', 'evidence')}
            </div>
        </div>

        <div class="cv-section">
            <div class="cv-section-title">Trade-offs & Choices</div>
            <div class="cv-content">
                ${renderList(fp.trade_offs, 'pair', 'description', 'evidence')}
            </div>
        </div>

        <div class="cv-section">
            <div class="cv-section-title">Contradictions & Tensions</div>
            <div class="cv-content">
                ${renderList(fp.contradictions, 'conflict', 'insight', 'evidence')}
            </div>
        </div>

        <div class="cv-footer">
            Generated by the Professional Fingerprint Engine • Interpretation over Narration.
        </div>
    `;
}


