import React, { useState, useEffect, useContext } from "react";
import { Container, Row, Col, Nav, Tab, Alert, Spinner } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import {
  CountdownTimer,
  FlashSaleTimeline,
  FlashSaleProducts,
} from "../components/FlashSale";
import CartContext from "../context/cartContext";
import httpService from "../services/httpService";
import "./FlashSalePage.css";

const FlashSalePage = () => {
  const navigate = useNavigate();
  const { productsInCart, addItemToCart } = useContext(CartContext);

  const [dashboardData, setDashboardData] = useState(null);
  const [currentItems, setCurrentItems] = useState([]);
  const [selectedProgram, setSelectedProgram] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [loading, setLoading] = useState(true);
  const [itemsLoading, setItemsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [categories, setCategories] = useState([]);

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();

    // Refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Fetch categories
  useEffect(() => {
    fetchCategories();
  }, []);

  // Fetch items when program or category changes
  useEffect(() => {
    if (selectedProgram) {
      fetchFlashSaleItems(selectedProgram.id, selectedCategory);
    }
  }, [selectedProgram, selectedCategory]);

  const fetchDashboardData = async () => {
    try {
      const response = await httpService.get("/api/flash-sale/dashboard/");
      setDashboardData(response.data);

      // Auto-select current program if available
      if (response.data.current_program && !selectedProgram) {
        setSelectedProgram(response.data.current_program);
      } else if (
        !response.data.current_program &&
        response.data.today_timeline.length > 0
      ) {
        // Select first upcoming program
        const upcomingProgram = response.data.today_timeline.find(
          (p) => p.is_upcoming
        );
        if (upcomingProgram) {
          setSelectedProgram(upcomingProgram);
        }
      }

      setError(null);
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setError("Không thể tải dữ liệu Flash Sale");
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await httpService.get("/api/category/");
      setCategories(response.data);
    } catch (err) {
      console.error("Error fetching categories:", err);
    }
  };

  const fetchFlashSaleItems = async (programId, category = "all") => {
    setItemsLoading(true);
    try {
      let url = `/api/flash-sale-items/?program=${programId}&available_only=true`;
      if (category !== "all") {
        url += `&category=${category}`;
      }

      const response = await httpService.get(url);
      setCurrentItems(response.data);
    } catch (err) {
      console.error("Error fetching flash sale items:", err);
      setCurrentItems([]);
    } finally {
      setItemsLoading(false);
    }
  };

  const handleTimeSlotSelect = (program) => {
    setSelectedProgram(program);
    setSelectedCategory("all"); // Reset category filter
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  // Helper function to add Flash Sale item to cart
  const addFlashSaleToCart = (item, quantity = 1) => {
    const flashSaleCartItem = {
      id: item.product_info.id,
      name: item.product_info.name,
      image: item.product_info.image,
      price: item.flash_price, // Use Flash Sale price
      originalPrice: item.original_price,
      countInStock: item.remaining_quantity,
      qty: quantity,
      isFlashSale: true,
      flashSaleItemId: item.id,
      maxPerUser: item.max_per_user,
      discount: item.discount_percentage,
    };

    // Use addItemToCart from CartContext
    addItemToCart(flashSaleCartItem);
  };

  const handlePurchase = async (item) => {
    try {
      // Add Flash Sale item to cart
      addFlashSaleToCart(item, 1);

      // Navigate to cart page
      navigate("/cart");

      return { success: true };
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || "Có lỗi xảy ra khi thêm vào giỏ hàng";
      alert(errorMessage);
      throw err;
    }
  };

  const handleAddToCart = (item) => {
    try {
      // Add Flash Sale item to cart
      addFlashSaleToCart(item, 1);

      // Show success message
      alert("Đã thêm sản phẩm Flash Sale vào giỏ hàng!");
    } catch (err) {
      alert("Có lỗi xảy ra khi thêm vào giỏ hàng");
    }
  };

  const handleTimeUp = () => {
    // Refresh dashboard when time is up
    fetchDashboardData();
  };

  if (loading) {
    return (
      <Container className="flash-sale-page">
        <div className="loading-container">
          <Spinner animation="border" variant="primary" />
          <p>Đang tải Flash Sale...</p>
        </div>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="flash-sale-page">
        <Alert variant="danger">
          <Alert.Heading>Có lỗi xảy ra</Alert.Heading>
          <p>{error}</p>
          <button
            className="btn btn-outline-danger"
            onClick={fetchDashboardData}
          >
            Thử lại
          </button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid className="flash-sale-page">
      {/* Header Section */}
      <div className="flash-sale-header">
        <Container>
          <Row>
            <Col>
              <div className="header-content">
                <h1 className="page-title">
                  <i className="fas fa-bolt"></i>
                  Flash Sale
                </h1>
                <p className="page-subtitle">
                  Ưu đãi có giới hạn - Nhanh tay kẻo lỡ!
                </p>
              </div>
            </Col>
          </Row>
        </Container>
      </div>

      <Container>
        {/* Current Program & Countdown */}
        {dashboardData?.current_program && (
          <Row className="mb-4">
            <Col>
              <div className="current-program-banner">
                <div className="program-info">
                  <h2>{dashboardData.current_program.name}</h2>
                  <p>{dashboardData.current_program.description}</p>
                </div>
                <div className="program-countdown">
                  <CountdownTimer
                    endTime={dashboardData.current_program.end_time}
                    onTimeUp={handleTimeUp}
                    size="large"
                  />
                </div>
              </div>
            </Col>
          </Row>
        )}

        {/* Next Program Preview */}
        {!dashboardData?.current_program && dashboardData?.next_program && (
          <Row className="mb-4">
            <Col>
              <div className="next-program-banner">
                <div className="program-info">
                  <h3>Flash Sale tiếp theo</h3>
                  <h2>{dashboardData.next_program.name}</h2>
                  <p>
                    Bắt đầu lúc:{" "}
                    {new Date(
                      dashboardData.next_program.start_time
                    ).toLocaleString("vi-VN")}
                  </p>
                </div>
                <div className="program-countdown">
                  <CountdownTimer
                    endTime={dashboardData.next_program.start_time}
                    size="large"
                    showLabels={true}
                  />
                </div>
              </div>
            </Col>
          </Row>
        )}

        {/* Timeline */}
        <Row className="mb-4">
          <Col>
            <FlashSaleTimeline
              programs={dashboardData?.today_timeline || []}
              currentProgram={dashboardData?.current_program}
              onTimeSlotSelect={handleTimeSlotSelect}
            />
          </Col>
        </Row>

        {/* Category Tabs & Products */}
        {selectedProgram && (
          <Row>
            <Col>
              <div className="products-section">
                <div className="section-header">
                  <h3>Sản phẩm Flash Sale</h3>
                  <div className="program-badge">{selectedProgram.name}</div>
                </div>

                {/* Category Filter */}
                <Tab.Container
                  activeKey={selectedCategory}
                  onSelect={handleCategoryChange}
                >
                  <Nav variant="pills" className="category-nav mb-4">
                    <Nav.Item>
                      <Nav.Link eventKey="all">
                        <i className="fas fa-th-large"></i>
                        Tất cả
                      </Nav.Link>
                    </Nav.Item>
                    {categories.map((category) => (
                      <Nav.Item key={category.id}>
                        <Nav.Link eventKey={category.title}>
                          {category.title}
                        </Nav.Link>
                      </Nav.Item>
                    ))}
                  </Nav>

                  {/* Products Grid */}
                  <FlashSaleProducts
                    products={currentItems}
                    loading={itemsLoading}
                    onPurchase={handlePurchase}
                    onAddToCart={handleAddToCart}
                  />
                </Tab.Container>
              </div>
            </Col>
          </Row>
        )}

        {/* No Program Selected */}
        {!selectedProgram && (
          <Row>
            <Col>
              <div className="no-program-selected">
                <i className="fas fa-calendar-times"></i>
                <h3>Chọn khung giờ Flash Sale</h3>
                <p>Vui lòng chọn một khung giờ Flash Sale để xem sản phẩm</p>
              </div>
            </Col>
          </Row>
        )}
      </Container>
    </Container>
  );
};

export default FlashSalePage;
