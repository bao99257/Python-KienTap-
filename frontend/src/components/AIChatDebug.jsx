import React, { useState } from 'react';
import { Button, Card, Alert, Badge } from 'react-bootstrap';

const AIChatDebug = () => {
  const [testResults, setTestResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const addResult = (test, status, message, details = null) => {
    setTestResults(prev => [...prev, {
      id: Date.now(),
      test,
      status,
      message,
      details,
      timestamp: new Date().toLocaleTimeString()
    }]);
  };

  const runTests = async () => {
    setIsLoading(true);
    setTestResults([]);

    // Test 1: Check backend connection
    try {
      const response = await fetch('http://localhost:8000/api/');
      if (response.status === 200 || response.status === 404) {
        addResult('Backend Connection', 'success', 'Backend server is running');
      } else {
        addResult('Backend Connection', 'warning', `Backend returned status: ${response.status}`);
      }
    } catch (error) {
      addResult('Backend Connection', 'error', 'Cannot connect to backend', error.message);
    }

    // Test 2: Check AI test endpoint
    try {
      const response = await fetch('http://localhost:8000/ai/test/');
      if (response.ok) {
        const data = await response.json();
        addResult('AI Test Endpoint', 'success', 'AI endpoint is working', data);
      } else {
        addResult('AI Test Endpoint', 'error', `AI endpoint failed: ${response.status}`);
      }
    } catch (error) {
      addResult('AI Test Endpoint', 'error', 'AI endpoint not accessible', error.message);
    }

    // Test 3: Check authentication
    const token = localStorage.getItem('authTokens') ? 
      JSON.parse(localStorage.getItem('authTokens')).access : null;
    
    if (token) {
      addResult('Authentication', 'success', 'Auth token found in localStorage');
      
      // Test 4: Try AI chat endpoint
      try {
        const response = await fetch('http://localhost:8000/ai/chat/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `JWT ${token}`
          },
          body: JSON.stringify({
            message: 'Test message',
            context: {}
          })
        });

        if (response.ok) {
          const data = await response.json();
          addResult('AI Chat Endpoint', 'success', 'AI chat is working!', data);
        } else {
          const errorText = await response.text();
          addResult('AI Chat Endpoint', 'error', `AI chat failed: ${response.status}`, errorText);
        }
      } catch (error) {
        addResult('AI Chat Endpoint', 'error', 'AI chat request failed', error.message);
      }
    } else {
      addResult('Authentication', 'warning', 'No auth token found. Please login first.');
    }

    setIsLoading(false);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'success': return 'success';
      case 'warning': return 'warning';
      case 'error': return 'danger';
      default: return 'secondary';
    }
  };

  return (
    <Card className="m-3">
      <Card.Header>
        <h5>🔧 AI Chat Debug Tool</h5>
      </Card.Header>
      <Card.Body>
        <Button 
          variant="primary" 
          onClick={runTests} 
          disabled={isLoading}
          className="mb-3"
        >
          {isLoading ? 'Running Tests...' : 'Run Diagnostic Tests'}
        </Button>

        {testResults.length > 0 && (
          <div>
            <h6>Test Results:</h6>
            {testResults.map((result) => (
              <Alert 
                key={result.id} 
                variant={getStatusColor(result.status)}
                className="mb-2"
              >
                <div className="d-flex justify-content-between align-items-start">
                  <div>
                    <strong>{result.test}</strong>
                    <Badge bg={getStatusColor(result.status)} className="ms-2">
                      {result.status.toUpperCase()}
                    </Badge>
                    <div className="mt-1">{result.message}</div>
                    {result.details && (
                      <details className="mt-2">
                        <summary>Details</summary>
                        <pre className="mt-1" style={{fontSize: '0.8rem'}}>
                          {typeof result.details === 'string' 
                            ? result.details 
                            : JSON.stringify(result.details, null, 2)
                          }
                        </pre>
                      </details>
                    )}
                  </div>
                  <small className="text-muted">{result.timestamp}</small>
                </div>
              </Alert>
            ))}
          </div>
        )}

        <div className="mt-3">
          <h6>Troubleshooting Tips:</h6>
          <ul className="small">
            <li>Make sure Django server is running on port 8000</li>
            <li>Check if ai_chat app is in INSTALLED_APPS</li>
            <li>Run: <code>python manage.py migrate</code></li>
            <li>Run: <code>python manage.py setup_ai_knowledge</code></li>
            <li>Make sure you're logged in to use AI chat</li>
          </ul>
        </div>
      </Card.Body>
    </Card>
  );
};

export default AIChatDebug;
