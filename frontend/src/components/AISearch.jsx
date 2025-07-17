import React, { useState } from 'react';
import { 
  Button, 
  Form, 
  Modal, 
  Spinner, 
  Alert, 
  Card, 
  Row, 
  Col,
  Badge 
} from 'react-bootstrap';
import httpService from '../services/httpService';

function AISearch({ onResults, onClose }) {
  const [showModal, setShowModal] = useState(false);
  const [searchType, setSearchType] = useState('text');
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [results, setResults] = useState([]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Kiểm tra kích thước file
      if (file.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      // Kiểm tra định dạng
      const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
      if (!allowedTypes.includes(file.type)) {
        setError('Only JPG, PNG, and WebP images are allowed');
        return;
      }

      setSelectedImage(file);
      setError('');

      // Tạo preview
      const reader = new FileReader();
      reader.onload = (e) => setImagePreview(e.target.result);
      reader.readAsDataURL(file);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    setError('');

    try {
      let response;
      const formData = new FormData();

      if (searchType === 'image') {
        if (!selectedImage) {
          setError('Please select an image');
          setLoading(false);
          return;
        }
        formData.append('image', selectedImage);
        response = await httpService.post('/api/ai-search/image/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      } else if (searchType === 'text') {
        if (!searchText.trim()) {
          setError('Please enter search text');
          setLoading(false);
          return;
        }
        response = await httpService.post('/api/ai-search/text/', {
          text: searchText
        });
      } else if (searchType === 'hybrid') {
        if (!searchText.trim() && !selectedImage) {
          setError('Please provide text or image or both');
          setLoading(false);
          return;
        }
        if (searchText.trim()) {
          formData.append('text', searchText);
        }
        if (selectedImage) {
          formData.append('image', selectedImage);
        }
        response = await httpService.post('/api/ai-search/hybrid/', formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }

      if (response.data.success) {
        setResults(response.data.products);
        if (onResults) {
          onResults(response.data.products);
        }
        if (response.data.products.length === 0) {
          setError('No matching products found. Try different search terms.');
        }
      } else {
        setError(response.data.message || 'Search failed');
      }

    } catch (error) {
      console.error('AI Search error:', error);
      if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError('An error occurred during search. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetForm = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setSearchText('');
    setError('');
    setResults([]);
  };

  const handleClose = () => {
    setShowModal(false);
    resetForm();
    if (onClose) onClose();
  };

  return (
    <>
      <Button 
        variant="outline-primary" 
        onClick={() => setShowModal(true)}
        className="ai-search-btn d-flex align-items-center"
      >
        <i className="fas fa-robot me-2"></i>
        AI Search
      </Button>

      <Modal show={showModal} onHide={handleClose} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <i className="fas fa-robot me-2"></i>
            AI-Powered Product Search
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError('')}>
              {error}
            </Alert>
          )}

          <Form.Group className="mb-3">
            <Form.Label>Search Method</Form.Label>
            <Form.Select 
              value={searchType} 
              onChange={(e) => {
                setSearchType(e.target.value);
                setError('');
              }}
            >
              <option value="text">Search by Description</option>
              <option value="image">Search by Image</option>
              <option value="hybrid">Combined Search (Text + Image)</option>
            </Form.Select>
          </Form.Group>

          {(searchType === 'text' || searchType === 'hybrid') && (
            <Form.Group className="mb-3">
              <Form.Label>Product Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={searchText}
                onChange={(e) => setSearchText(e.target.value)}
                placeholder="Describe what you're looking for... (e.g., red summer dress, wireless headphones, running shoes)"
              />
              <Form.Text className="text-muted">
                Be specific about color, style, material, or use case for better results.
              </Form.Text>
            </Form.Group>
          )}

          {(searchType === 'image' || searchType === 'hybrid') && (
            <Form.Group className="mb-3">
              <Form.Label>Upload Image</Form.Label>
              <Form.Control
                type="file"
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleImageChange}
              />
              <Form.Text className="text-muted">
                Supported formats: JPG, PNG, WebP. Max size: 10MB
              </Form.Text>
              
              {imagePreview && (
                <div className="mt-3">
                  <img 
                    src={imagePreview} 
                    alt="Preview" 
                    style={{ 
                      maxWidth: '200px', 
                      maxHeight: '200px', 
                      objectFit: 'contain',
                      border: '1px solid #ddd',
                      borderRadius: '4px'
                    }} 
                  />
                </div>
              )}
            </Form.Group>
          )}

          {results.length > 0 && (
            <div className="mt-4">
              <h6>Search Results ({results.length} products found)</h6>
              <Row>
                {results.slice(0, 6).map((product) => (
                  <Col md={4} key={product.id} className="mb-3">
                    <Card className="h-100">
                      <Card.Img 
                        variant="top" 
                        src={product.image} 
                        style={{ height: '150px', objectFit: 'cover' }}
                      />
                      <Card.Body className="d-flex flex-column">
                        <Card.Title className="small">{product.name}</Card.Title>
                        <Card.Text className="small text-muted flex-grow-1">
                          ${product.price}
                        </Card.Text>
                        <Badge 
                          bg="info" 
                          className="align-self-start"
                        >
                          {Math.round(product.similarity_score * 100)}% match
                        </Badge>
                      </Card.Body>
                    </Card>
                  </Col>
                ))}
              </Row>
              {results.length > 6 && (
                <p className="text-muted">
                  And {results.length - 6} more results...
                </p>
              )}
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
          <Button 
            variant="primary" 
            onClick={handleSearch}
            disabled={loading}
            className="d-flex align-items-center"
          >
            {loading ? (
              <>
                <Spinner size="sm" className="me-2" />
                Searching...
              </>
            ) : (
              <>
                <i className="fas fa-search me-2"></i>
                Search
              </>
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
}

export default AISearch;