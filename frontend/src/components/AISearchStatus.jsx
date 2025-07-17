import React, { useState, useEffect } from 'react';
import { Alert, Spinner } from 'react-bootstrap';
import httpService from '../services/httpService';

function AISearchStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAIStatus();
  }, []);

  const checkAIStatus = async () => {
    try {
      const response = await httpService.get('/api/ai-search/status/');
      setStatus(response.data);
    } catch (error) {
      setStatus({
        status: 'error',
        message: 'Failed to check AI status'
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Alert variant="info">
        <Spinner size="sm" className="me-2" />
        Checking AI Search status...
      </Alert>
    );
  }

  if (status?.status === 'ready') {
    return (
      <Alert variant="success">
        <i className="fas fa-robot me-2"></i>
        AI Search is ready! You can now search by image and description.
      </Alert>
    );
  }

  return (
    <Alert variant="warning">
      <i className="fas fa-exclamation-triangle me-2"></i>
      AI Search is not available. {status?.message}
    </Alert>
  );
}

export default AISearchStatus;