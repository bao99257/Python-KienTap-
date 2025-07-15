import React from "react";
import { Card, Button, Badge } from "react-bootstrap";

const ChatBotProductCard = ({ product }) => {
  const handleViewProduct = () => {
    // Chuyển đến trang chi tiết sản phẩm với đúng format
    window.open(`/#/products/${product.id}`, "_blank");
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(price);
  };

  const getImageUrl = (imageUrl) => {
    if (!imageUrl || imageUrl === "/placeholder.png") {
      return "/placeholder.png";
    }
    if (imageUrl.startsWith("http")) {
      return imageUrl;
    }
    return `http://localhost:8000${imageUrl}`;
  };

  return (
    <Card
      className="mb-2"
      style={{ maxWidth: "300px", display: "inline-block", margin: "5px" }}
    >
      <Card.Img
        variant="top"
        src={getImageUrl(product.image)}
        style={{ height: "200px", objectFit: "cover" }}
        onError={(e) => {
          e.target.src = "/placeholder.png";
        }}
      />
      <Card.Body>
        <Card.Title
          style={{ fontSize: "1rem", height: "2.5rem", overflow: "hidden" }}
        >
          {product.name}
        </Card.Title>

        <div className="d-flex justify-content-between align-items-center mb-2">
          <Badge bg="secondary">{product.brand?.name || "No Brand"}</Badge>
          <Badge bg="info">{product.category?.name || "No Category"}</Badge>
        </div>

        <div className="d-flex justify-content-between align-items-center mb-2">
          <strong className="text-primary">
            {formatPrice(product.min_price || product.price)}
          </strong>
          <small className="text-muted">
            Còn: {product.total_stock || product.countInStock}
          </small>
        </div>

        {product.rating && (
          <div className="mb-2">
            <span className="text-warning">
              {"★".repeat(Math.floor(product.rating))}
              {"☆".repeat(5 - Math.floor(product.rating))}
            </span>
            <small className="text-muted ms-1">
              ({product.numReviews} đánh giá)
            </small>
          </div>
        )}

        <Button
          variant="primary"
          size="sm"
          onClick={handleViewProduct}
          className="w-100"
        >
          Xem chi tiết
        </Button>
      </Card.Body>
    </Card>
  );
};

export default ChatBotProductCard;
