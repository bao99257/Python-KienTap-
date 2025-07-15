import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { useParams, Link } from 'react-router-dom';
import httpService from '../../services/httpService';
import './AdminFlashSale.css';

const AdminFlashSaleItems = () => {
  const { programId } = useParams();
  const [program, setProgram] = useState(null);
  const [items, setItems] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [formData, setFormData] = useState({
    product: '',
    original_price: '',
    flash_price: '',
    total_quantity: '',
    max_per_user: 1,
    is_active: true
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchProgram();
    fetchItems();
    fetchProducts();
  }, [programId]);

  const fetchProgram = async () => {
    try {
      const response = await httpService.get(`/api/flash-sale-programs/${programId}/`);
      setProgram(response.data);
    } catch (err) {
      console.error('Error fetching program:', err);
      setError('Không thể tải thông tin chương trình');
    }
  };

  const fetchItems = async () => {
    try {
      setLoading(true);
      const response = await httpService.get(`/api/flash-sale-items/?program=${programId}`);
      setItems(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching items:', err);
      setError('Không thể tải danh sách sản phẩm');
    } finally {
      setLoading(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const response = await httpService.get('/api/products/');
      setProducts(response.data);
    } catch (err) {
      console.error('Error fetching products:', err);
    }
  };

  const handleShowModal = (item = null) => {
    if (item) {
      setEditingItem(item);
      setFormData({
        product: item.product,
        original_price: item.original_price,
        flash_price: item.flash_price,
        total_quantity: item.total_quantity,
        max_per_user: item.max_per_user,
        is_active: item.is_active
      });
    } else {
      setEditingItem(null);
      setFormData({
        product: '',
        original_price: '',
        flash_price: '',
        total_quantity: '',
        max_per_user: 1,
        is_active: true
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingItem(null);
    setFormData({
      product: '',
      original_price: '',
      flash_price: '',
      total_quantity: '',
      max_per_user: 1,
      is_active: true
    });
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const payload = {
        ...formData,
        program: programId
      };

      if (editingItem) {
        await httpService.put(`/api/flash-sale-items/${editingItem.id}/`, payload);
      } else {
        await httpService.post('/api/flash-sale-items/', payload);
      }

      await fetchItems();
      handleCloseModal();
      setError(null);
    } catch (err) {
      console.error('Error saving item:', err);
      setError(err.response?.data?.detail || 'Có lỗi xảy ra khi lưu sản phẩm');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (itemId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa sản phẩm này khỏi Flash Sale?')) {
      return;
    }

    try {
      await httpService.delete(`/api/flash-sale-items/${itemId}/`);
      await fetchItems();
      setError(null);
    } catch (err) {
      console.error('Error deleting item:', err);
      setError('Không thể xóa sản phẩm');
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('vi-VN', {
      style: 'currency',
      currency: 'VND'
    }).format(price);
  };

  const getProductName = (productId) => {
    const product = products.find(p => p.id === productId);
    return product ? product.name : 'Không tìm thấy sản phẩm';
  };

  if (loading) {
    return (
      <Container className="admin-flash-sale">
        <div className="text-center py-5">
          <Spinner animation="border" variant="primary" />
          <p className="mt-3">Đang tải...</p>
        </div>
      </Container>
    );
  }

  return (
    <Container className="admin-flash-sale">
      <Row className="mb-4">
        <Col>
          <div className="d-flex justify-content-between align-items-center">
            <div>
              <Link to="/admin/flash-sale" className="text-decoration-none">
                <i className="fas fa-arrow-left me-2"></i>
                Quay lại
              </Link>
              <h2 className="mt-2">
                <i className="fas fa-box me-2"></i>
                Sản phẩm Flash Sale
              </h2>
              {program && (
                <p className="text-muted mb-0">
                  Chương trình: <strong>{program.name}</strong>
                </p>
              )}
            </div>
            <Button variant="primary" onClick={() => handleShowModal()}>
              <i className="fas fa-plus me-2"></i>
              Thêm sản phẩm
            </Button>
          </div>
        </Col>
      </Row>

      {error && (
        <Row className="mb-3">
          <Col>
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          </Col>
        </Row>
      )}

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <h5 className="mb-0">Danh sách sản phẩm trong Flash Sale</h5>
            </Card.Header>
            <Card.Body>
              {items.length === 0 ? (
                <div className="text-center py-4">
                  <i className="fas fa-box-open fa-3x text-muted mb-3"></i>
                  <h5>Chưa có sản phẩm nào</h5>
                  <p className="text-muted">Thêm sản phẩm vào chương trình Flash Sale</p>
                  <Button variant="primary" onClick={() => handleShowModal()}>
                    Thêm sản phẩm đầu tiên
                  </Button>
                </div>
              ) : (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Sản phẩm</th>
                      <th>Giá gốc</th>
                      <th>Giá Flash Sale</th>
                      <th>Giảm giá</th>
                      <th>Số lượng</th>
                      <th>Đã bán</th>
                      <th>Giới hạn/người</th>
                      <th>Trạng thái</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map(item => (
                      <tr key={item.id}>
                        <td>
                          <div className="d-flex align-items-center">
                            {item.product_info?.image && (
                              <img 
                                src={item.product_info.image} 
                                alt={item.product_info.name}
                                style={{ width: '40px', height: '40px', objectFit: 'cover' }}
                                className="rounded me-2"
                              />
                            )}
                            <div>
                              <strong>{item.product_info?.name || getProductName(item.product)}</strong>
                              <div className="text-muted small">ID: {item.product}</div>
                            </div>
                          </div>
                        </td>
                        <td>{formatPrice(item.original_price)}</td>
                        <td className="text-danger fw-bold">{formatPrice(item.flash_price)}</td>
                        <td>
                          <Badge bg="success">-{item.discount_percentage}%</Badge>
                        </td>
                        <td>{item.total_quantity}</td>
                        <td>
                          <div>
                            <strong>{item.sold_quantity}</strong>
                            <div className="text-muted small">
                              {Math.round(item.sold_percentage)}% đã bán
                            </div>
                          </div>
                        </td>
                        <td>{item.max_per_user}</td>
                        <td>
                          {item.is_active ? (
                            <Badge bg="success">Hoạt động</Badge>
                          ) : (
                            <Badge bg="secondary">Tạm dừng</Badge>
                          )}
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              size="sm"
                              variant="outline-secondary"
                              onClick={() => handleShowModal(item)}
                            >
                              <i className="fas fa-edit"></i>
                            </Button>
                            <Button
                              size="sm"
                              variant="outline-danger"
                              onClick={() => handleDelete(item.id)}
                            >
                              <i className="fas fa-trash"></i>
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Modal for Create/Edit Item */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingItem ? 'Chỉnh sửa sản phẩm' : 'Thêm sản phẩm mới'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Sản phẩm *</Form.Label>
                  <Form.Select
                    name="product"
                    value={formData.product}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Chọn sản phẩm</option>
                    {products.map(product => (
                      <option key={product.id} value={product.id}>
                        {product.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Trạng thái</Form.Label>
                  <Form.Check
                    type="checkbox"
                    name="is_active"
                    label="Kích hoạt sản phẩm"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Giá gốc *</Form.Label>
                  <Form.Control
                    type="number"
                    name="original_price"
                    value={formData.original_price}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="1000"
                    placeholder="VD: 100000"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Giá Flash Sale *</Form.Label>
                  <Form.Control
                    type="number"
                    name="flash_price"
                    value={formData.flash_price}
                    onChange={handleInputChange}
                    required
                    min="0"
                    step="1000"
                    placeholder="VD: 50000"
                  />
                </Form.Group>
              </Col>
            </Row>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tổng số lượng *</Form.Label>
                  <Form.Control
                    type="number"
                    name="total_quantity"
                    value={formData.total_quantity}
                    onChange={handleInputChange}
                    required
                    min="1"
                    placeholder="VD: 100"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Giới hạn mỗi người *</Form.Label>
                  <Form.Control
                    type="number"
                    name="max_per_user"
                    value={formData.max_per_user}
                    onChange={handleInputChange}
                    required
                    min="1"
                    placeholder="VD: 2"
                  />
                </Form.Group>
              </Col>
            </Row>

            {formData.original_price && formData.flash_price && (
              <Alert variant="info">
                <strong>Giảm giá: </strong>
                {Math.round(((formData.original_price - formData.flash_price) / formData.original_price) * 100)}%
              </Alert>
            )}
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Hủy
            </Button>
            <Button type="submit" variant="primary" disabled={submitting}>
              {submitting ? (
                <>
                  <Spinner animation="border" size="sm" className="me-2" />
                  Đang lưu...
                </>
              ) : (
                editingItem ? 'Cập nhật' : 'Thêm mới'
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default AdminFlashSaleItems;
