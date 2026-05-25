import React, { useState } from 'react';
import './style.css';

// The backend API endpoint. For production, you might get this from an environment variable.
const API_ENDPOINT = 'http://127.0.0.1:5001/api/ticket';

const App = () => {
    const [ticketText, setTicketText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState('');

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!ticketText.trim()) {
            setError('Ticket content cannot be empty.');
            return;
        }

        // Reset state for a new submission
        setIsLoading(true);
        setResults(null);
        setError('');

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ticket_text: ticketText }),
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle errors from the backend, including API failures
                throw new Error(data.error || `Server responded with status: ${response.status}`);
            }

            setResults(data);
        } catch (err) {
            // Handle network errors or exceptions thrown
            setError(err.message || 'An unknown error occurred. Please check the console.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="container">
            <h1>AI Support Ticket Router</h1>
            <p>Enter a customer support ticket to see it analyzed and routed in real-time.</p>

            <form onSubmit={handleSubmit}>
                <textarea
                    value={ticketText}
                    onChange={(e) => setTicketText(e.target.value)}
                    placeholder="e.g., I can't log in to my account, my password reset is not working..."
                    rows="6"
                    required
                    disabled={isLoading}
                />
                <button type="submit" disabled={isLoading} className="process-btn">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="m21.64 3.64-1.28-1.28a1.21 1.21 0 0 0-1.71 0L11.4 9.61a1.21 1.21 0 0 0 0 1.71l1.28 1.28a1.21 1.21 0 0 0 1.71 0l7.25-7.25a1.21 1.21 0 0 0 0-1.71Z"/><path d="m14 13-8.5 8.5a2.09 2.09 0 0 1-3-3L11 10"/><path d="m16 16 6-6"/><path d="m8 8 2-2"/><path d="m13 7 6-6"/><path d="m3.64 21.64 1.28-1.28a1.21 1.21 0 0 0 0-1.71L-2.33 11.4a1.21 1.21 0 0 0-1.71 0l-1.28 1.28a1.21 1.21 0 0 0 0 1.71l7.25 7.25a1.21 1.21 0 0 0 1.71 0Z"/>
                    </svg>
                    {isLoading ? 'Processing...' : 'Process Ticket'}
                </button>
            </form>

            {isLoading && <div className="loader">Analyzing ticket... This may take a moment.</div>}
            {error && <div className="error">{error}</div>}
            {results && <ResultsDisplay data={results} />}
        </div>
    );
};

// Enhanced component to parse and render guidance into styled cards
const GuidanceSteps = ({ guidance }) => {
    // More robust parsing to handle titles and descriptions
    const rawSteps = guidance.split(/\n(?=\d+\.|\*\*)/).filter(Boolean);

    const steps = rawSteps.map(rawStep => {
        const lines = rawStep.trim().split('\n');
        const title = lines[0].replace(/^\d+\.\s*/, '').replace(/\*\*/g, '').trim();
        const description = lines.slice(1).join(' ').trim();
        return { title, description };
    });

    return (
        <div className="guidance-container">
            {steps.map((step, index) => (
                <div key={index} className="guidance-card">
                    <div className="guidance-step-indicator">{index + 1}</div>
                    <div className="guidance-content">
                        <h4>{step.title}</h4>
                        {step.description && <p>{step.description}</p>}
                    </div>
                </div>
            ))}
        </div>
    );
};

const AnalysisCard = ({ icon, title, value }) => (
    <div className="analysis-card">
        <div className="analysis-icon">{icon}</div>
        <div className="analysis-content">
            <span className="analysis-title">{title}</span>
            <span className="analysis-value">{value}</span>
        </div>
    </div>
);

// A sub-component to cleanly display the results
const ResultsDisplay = ({ data }) => (
    <div className="results-container">
        <div className="result-section">
            <h3>📊 Ticket Analysis</h3>
            <div className="analysis-grid">
                <AnalysisCard icon="📁" title="Category" value={data.analysis.category} />
                <AnalysisCard icon="⚡️" title="Urgency" value={data.analysis.urgency} />
                <AnalysisCard icon="😊" title="Sentiment" value={data.analysis.sentiment} />
            </div>
        </div>

        <div className="result-section">
            <h3>🔀 Routing Decision</h3>
            <div className="routing-decision-wrapper">
                <span>Assigned To:</span>
                <span className="routing-badge">{data.routing.decision}</span>
            </div>
        </div>

        <div className="result-section">
            <h3>🛠️ Agent Guidance ({data.agent_guidance.type})</h3>
            <GuidanceSteps guidance={data.agent_guidance.guidance} />
        </div>

        <div className="result-section">
            <h3>📧 Customer Email Preview</h3>
            <pre>{data.customer_response.email_preview}</pre>
        </div>
    </div>
);

export default App;
