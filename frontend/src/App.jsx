// frontend/src/App.jsx
import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [topic, setTopic] = useState('');
  
  // New loading states
  const [isLoadingScript, setIsLoadingScript] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  
  // Script related states
  const [generatedScriptText, setGeneratedScriptText] = useState('');
  const [scriptSegments, setScriptSegments] = useState([]); // To store [{speaker, text}, ...]

  const [audioUrl, setAudioUrl] = useState('');
  const [error, setError] = useState('');


  // --- IMPLEMENT handleGenerateScript ---
  const handleGenerateScript = async (e) => {
    // If called from a form submit, prevent default. If from button click, e might be undefined.
    if (e && e.preventDefault) e.preventDefault(); 

    if (!topic.trim()) {
      setError("Please enter a topic.");
      return;
    }

    setIsLoadingScript(true);
    setGeneratedScriptText(''); // Clear previous script text
    setScriptSegments([]);      // Clear previous segments
    setAudioUrl('');            // Clear previous audio if generating new script
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/generate-script', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: topic }),
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
        } catch (jsonError) {
            console.warn("Could not parse error response as JSON:", jsonError);
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      
      setGeneratedScriptText(data.raw_script_text || "Script generated, but no text content received.");
      setScriptSegments(data.segments || []);

      if (!data.segments || data.segments.length === 0) {
          console.warn("Script generated, but no segments were parsed. Audio generation might fail or be incorrect.");
          // Optionally set an error or warning for the user here if segments are critical
          // setError("Warning: Script was generated, but could not be structured for audio. Please check script format.");
      }

    } catch (err) {
      console.error("Failed to generate script:", err);
      setError(`Script generation failed: ${err.message}`);
      setGeneratedScriptText('');
      setScriptSegments([]);
    } finally {
      setIsLoadingScript(false);
    }
  };

  const handleGenerateAudio = async (e) => {
    if (e && e.preventDefault) e.preventDefault();

    if (scriptSegments.length === 0) {
        setError("No script segments available to generate audio. Please generate a script first.");
        return;
    }

    setIsLoadingAudio(true);
    setAudioUrl(''); // Clear previous audio
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/generate-podcast-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ segments: scriptSegments }), // Send the segments array
      });

      if (!response.ok) {
        let errorDetail = `HTTP error! status: ${response.status} ${response.statusText}`;
        try {
            const errorData = await response.json();
            errorDetail = errorData.detail || errorDetail;
        } catch (jsonError) {
            console.warn("Could not parse error response as JSON:", jsonError);
        }
        throw new Error(errorDetail);
      }

      // Get the audio data as a Blob
      const audioBlob = await response.blob();
      
      // Create an Object URL from the Blob
      const newAudioUrl = URL.createObjectURL(audioBlob);
      setAudioUrl(newAudioUrl);

    } catch (err) {
      console.error("Failed to generate audio:", err);
      setError(`Audio generation failed: ${err.message}`);
      setAudioUrl('');
    } finally {
      setIsLoadingAudio(false);
    }
  };

  // Clean up Object URL when component unmounts or audioUrl changes
  useEffect(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎙️ AI Podcast Generator (Host & Guest) 🎙️</h1>
      </header>
      <main>
        <div className="input-form">
          <div className="form-group">
            <label htmlFor="topic">Podcast Topic or Sentence:</label>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., The impact of AI on daily life"
              rows={3}
              required
              disabled={isLoadingScript || isLoadingAudio}
            />
          </div>

          <div className="action-buttons">
            <button 
              onClick={handleGenerateScript}
              disabled={isLoadingScript || isLoadingAudio || !topic.trim()}
              className="button-script"
            >
              {isLoadingScript ? 'Generating Script...' : 'Generate Script'}
            </button>
            
            <button 
              onClick={handleGenerateAudio}
              disabled={isLoadingScript || isLoadingAudio || scriptSegments.length === 0}
              className="button-audio"
            >
              {isLoadingAudio ? 'Generating Audio...' : 'Generate Podcast Audio'}
            </button>
          </div>
        </div>

        {error && <p className="error-message">Error: {error}</p>}

        {(isLoadingScript || isLoadingAudio) && 
          <p className="loading-message">
            {isLoadingScript ? 'Generating your script, please wait...' : 'Generating your podcast audio, please wait...'}
          </p>
        }

        {generatedScriptText && !isLoadingScript && !isLoadingAudio && (
          <section className="results-section">
            <h2>Generated Script:</h2>
            <pre className="script-display">{generatedScriptText}</pre>
          </section>
        )}

        {audioUrl && !isLoadingAudio && ( // Only show if audio is ready and not currently generating audio
          <section className="results-section">
            <h2>Generated Audio:</h2>
            <audio controls src={audioUrl} className="audio-player" key={audioUrl}>
              Your browser does not support the audio element.
            </audio>
          </section>
        )}
      </main>
      <footer>
        <p>Powered by Shubham Shinde</p>
      </footer>
    </div>
  );
}

export default App;






