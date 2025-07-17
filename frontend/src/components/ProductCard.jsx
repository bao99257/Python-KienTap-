import React from 'react';
import { Card, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function ProductCard({ product, showSimilarity = false }) {
  return (
    <Card className="h-100 shadow-sm">
      <div className="position-relative">
        <Card.Img 
          variant="top" 
          src={product.image} 
          style={{ height: '200px', objectFit: 'cover' }}
        />
        {showSimilarity && product.similarity_score && (
          <Badge 
            bg="success" 
            className="position-absolute top-0 end-0 m-2"
          >
            {Math.round(product.similarity_score * 100)}% match
          </Badge>
        )}
      </div>
      <Card.Body className="d-flex flex-column">
        <Card.Title className="h6">{product.name}</Card.Title>
        <Card.Text className="text-muted small flex-grow-1">
          {product.description?.substring(0, 100)}...
        </Card.Text>
        <div className="d-flex justify-content-between align-items-center mt-auto">
          <span className="h5 text-primary mb-0">${product.price}</span>
          <Link 
            to={`/products/${product.id}`} 
            className="btn btn-outline-primary btn-sm"
          >
            View Details
          </Link>
        </div>
      </Card.Body>
    </Card>
  );
}

export default ProductCard;