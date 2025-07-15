import React from 'react';
import { Card, Badge, ListGroup } from 'react-bootstrap';

const ChatBotOrderCard = ({ order }) => {
  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('vi-VN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusBadge = (order) => {
    if (order.isRefunded) {
      return <Badge bg="warning">Đã hoàn tiền</Badge>;
    }
    if (order.isDelivered) {
      return <Badge bg="success">Đã giao hàng</Badge>;
    }
    if (order.isPaid) {
      return <Badge bg="info">Đã thanh toán</Badge>;
    }
    return <Badge bg="secondary">Chờ thanh toán</Badge>;
  };

  const getImageUrl = (imageUrl) => {
    if (!imageUrl || imageUrl === '/placeholder.png') {
      return '/placeholder.png';
    }
    if (imageUrl.startsWith('http')) {
      return imageUrl;
    }
    return `http://localhost:8000${imageUrl}`;
  };

  return (
    <Card className="mb-3" style={{ maxWidth: '400px', display: 'inline-block', margin: '5px' }}>
      <Card.Header className="d-flex justify-content-between align-items-center">
        <small className="text-muted">Đơn hàng #{order.id}</small>
        {getStatusBadge(order)}
      </Card.Header>
      
      <Card.Body>
        <div className="mb-2">
          <strong>Ngày đặt:</strong> {formatDate(order.createdAt)}
        </div>
        
        <div className="mb-2">
          <strong>Tổng tiền:</strong> 
          <span className="text-primary ms-1">
            {formatPrice(order.totalPrice)}
          </span>
        </div>
        
        {order.paymentMethod && (
          <div className="mb-2">
            <strong>Thanh toán:</strong> {order.paymentMethod}
          </div>
        )}
        
        {order.orderItems && order.orderItems.length > 0 && (
          <div>
            <strong>Sản phẩm:</strong>
            <ListGroup variant="flush" className="mt-2">
              {order.orderItems.slice(0, 3).map((item, index) => (
                <ListGroup.Item key={index} className="px-0 py-1">
                  <div className="d-flex align-items-center">
                    <img 
                      src={getImageUrl(item.image)} 
                      alt={item.productName}
                      style={{ width: '40px', height: '40px', objectFit: 'cover' }}
                      className="me-2"
                      onError={(e) => {
                        e.target.src = '/placeholder.png';
                      }}
                    />
                    <div className="flex-grow-1">
                      <div style={{ fontSize: '0.9rem' }}>
                        {item.productName}
                      </div>
                      {item.variant_info && (
                        <small className="text-muted">{item.variant_info}</small>
                      )}
                      <div className="d-flex justify-content-between">
                        <small>SL: {item.qty}</small>
                        <small>{formatPrice(item.price)}</small>
                      </div>
                    </div>
                  </div>
                </ListGroup.Item>
              ))}
              {order.orderItems.length > 3 && (
                <ListGroup.Item className="px-0 py-1 text-center">
                  <small className="text-muted">
                    ... và {order.orderItems.length - 3} sản phẩm khác
                  </small>
                </ListGroup.Item>
              )}
            </ListGroup>
          </div>
        )}
      </Card.Body>
    </Card>
  );
};

export default ChatBotOrderCard;
