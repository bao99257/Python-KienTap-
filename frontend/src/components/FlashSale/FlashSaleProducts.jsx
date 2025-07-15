import React, { useState } from "react";
import { Link } from "react-router-dom";
import "./FlashSaleProducts.css";

const FlashSaleProducts = ({
  products = [],
  loading = false,
  onPurchase,
  onAddToCart,
  className = "",
}) => {
  const [purchasingItems, setPurchasingItems] = useState(new Set());

  const formatPrice = (price) => {
    return new Intl.NumberFormat("vi-VN", {
      style: "currency",
      currency: "VND",
    }).format(price);
  };

  const formatDiscount = (discount) => {
    return `-${discount}%`;
  };

  const getProgressBarColor = (percentage) => {
    if (percentage >= 80) return "#f44336"; // Red - almost sold out
    if (percentage >= 50) return "#ff9800"; // Orange - half sold
    return "#4caf50"; // Green - plenty left
  };

  const getStockStatus = (item) => {
    const percentage = item.sold_percentage || 0;
    if (percentage >= 95) return { text: "Sắp hết hàng", class: "critical" };
    if (percentage >= 80) return { text: "Còn ít", class: "low" };
    if (percentage >= 50) return { text: "Bán chạy", class: "medium" };
    return { text: "Còn hàng", class: "good" };
  };

  const handlePurchase = async (item) => {
    if (!onPurchase || purchasingItems.has(item.id)) return;

    setPurchasingItems((prev) => new Set(prev).add(item.id));

    try {
      await onPurchase(item);
    } finally {
      setPurchasingItems((prev) => {
        const newSet = new Set(prev);
        newSet.delete(item.id);
        return newSet;
      });
    }
  };

  const handleAddToCart = (item) => {
    if (onAddToCart) {
      onAddToCart(item);
    }
  };

  if (loading) {
    return (
      <div className={`flash-sale-products loading ${className}`}>
        <div className="products-grid">
          {[...Array(8)].map((_, index) => (
            <div key={index} className="product-card skeleton">
              <div className="skeleton-image"></div>
              <div className="skeleton-content">
                <div className="skeleton-line"></div>
                <div className="skeleton-line short"></div>
                <div className="skeleton-line"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className={`flash-sale-products empty ${className}`}>
        <div className="empty-state">
          <i className="fas fa-box-open"></i>
          <h3>Không có sản phẩm Flash Sale</h3>
          <p>
            Hiện tại không có sản phẩm nào trong chương trình Flash Sale này.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={`flash-sale-products ${className}`}>
      <div className="products-grid">
        {products.map((item) => {
          const stockStatus = getStockStatus(item);
          const isPurchasing = purchasingItems.has(item.id);
          const isAvailable = item.is_available && item.remaining_quantity > 0;

          return (
            <div
              key={item.id}
              className={`product-card ${!isAvailable ? "sold-out" : ""}`}
            >
              {/* Product Image */}
              <div className="product-image-container">
                <Link to={`/products/${item.product_info.id}`}>
                  <img
                    src={item.product_info.image || "/image/placeholder.png"}
                    alt={item.product_info.name}
                    className="product-image"
                  />
                </Link>

                {/* Discount Badge */}
                <div className="discount-badge">
                  {formatDiscount(item.discount_percentage)}
                </div>

                {/* Stock Status Badge */}
                <div className={`stock-badge ${stockStatus.class}`}>
                  {stockStatus.text}
                </div>

                {/* Sold Out Overlay */}
                {!isAvailable && (
                  <div className="sold-out-overlay">
                    <span>Đã hết hàng</span>
                  </div>
                )}
              </div>

              {/* Product Info */}
              <div className="product-info">
                <Link
                  to={`/products/${item.product_info.id}`}
                  className="product-name"
                >
                  {item.product_info.name}
                </Link>

                <div className="product-brand">{item.product_info.brand}</div>

                {/* Rating */}
                {item.product_info.rating > 0 && (
                  <div className="product-rating">
                    <div className="stars">
                      {[...Array(5)].map((_, i) => (
                        <i
                          key={i}
                          className={`fas fa-star ${
                            i < Math.floor(item.product_info.rating)
                              ? "filled"
                              : ""
                          }`}
                        ></i>
                      ))}
                    </div>
                    <span className="rating-text">
                      ({item.product_info.numReviews})
                    </span>
                  </div>
                )}

                {/* Prices */}
                <div className="product-prices">
                  <div className="flash-price">
                    {formatPrice(item.flash_price)}
                  </div>
                  <div className="original-price">
                    {formatPrice(item.original_price)}
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="sold-progress">
                  <div className="progress-info">
                    <span>Đã bán {Math.round(item.sold_percentage)}%</span>
                    <span>{item.remaining_quantity} còn lại</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{
                        width: `${item.sold_percentage}%`,
                        backgroundColor: getProgressBarColor(
                          item.sold_percentage
                        ),
                      }}
                    ></div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="product-actions">
                  {isAvailable ? (
                    <>
                      <button
                        className={`btn-purchase ${
                          isPurchasing ? "loading" : ""
                        }`}
                        onClick={() => handlePurchase(item)}
                        disabled={isPurchasing}
                      >
                        {isPurchasing ? (
                          <>
                            <i className="fas fa-spinner fa-spin"></i>
                            Đang xử lý...
                          </>
                        ) : (
                          <>
                            <i className="fas fa-bolt"></i>
                            Mua ngay
                          </>
                        )}
                      </button>

                      <button
                        className="btn-add-cart"
                        onClick={() => handleAddToCart(item)}
                      >
                        <i className="fas fa-cart-plus"></i>
                      </button>
                    </>
                  ) : (
                    <button className="btn-sold-out" disabled>
                      <i className="fas fa-times"></i>
                      Hết hàng
                    </button>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FlashSaleProducts;
