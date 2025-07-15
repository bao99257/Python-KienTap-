import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Table, Badge, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import httpService from '../../services/httpService';
import './AdminFlashSale.css';

const AdminFlashSale = () => {
  const [programs, setPrograms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingProgram, setEditingProgram] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    start_time: '',
    end_time: '',
    is_active: true
  });
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchPrograms();
  }, []);

  const fetchPrograms = async () => {
    try {
      setLoading(true);
      const response = await httpService.get('/api/flash-sale-programs/');
      setPrograms(response.data);
      setError(null);
    } catch (err) {
      console.error('Error fetching programs:', err);
      setError('Không thể tải danh sách chương trình Flash Sale');
    } finally {
      setLoading(false);
    }
  };

  const handleShowModal = (program = null) => {
    if (program) {
      setEditingProgram(program);
      setFormData({
        name: program.name,
        description: program.description,
        start_time: new Date(program.start_time).toISOString().slice(0, 16),
        end_time: new Date(program.end_time).toISOString().slice(0, 16),
        is_active: program.is_active
      });
    } else {
      setEditingProgram(null);
      setFormData({
        name: '',
        description: '',
        start_time: '',
        end_time: '',
        is_active: true
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingProgram(null);
    setFormData({
      name: '',
      description: '',
      start_time: '',
      end_time: '',
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
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString()
      };

      if (editingProgram) {
        await httpService.put(`/api/flash-sale-programs/${editingProgram.id}/`, payload);
      } else {
        await httpService.post('/api/flash-sale-programs/', payload);
      }

      await fetchPrograms();
      handleCloseModal();
      setError(null);
    } catch (err) {
      console.error('Error saving program:', err);
      setError(err.response?.data?.detail || 'Có lỗi xảy ra khi lưu chương trình');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (programId) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa chương trình này?')) {
      return;
    }

    try {
      await httpService.delete(`/api/flash-sale-programs/${programId}/`);
      await fetchPrograms();
      setError(null);
    } catch (err) {
      console.error('Error deleting program:', err);
      setError('Không thể xóa chương trình');
    }
  };

  const getStatusBadge = (program) => {
    const now = new Date();
    const startTime = new Date(program.start_time);
    const endTime = new Date(program.end_time);

    if (!program.is_active) {
      return <Badge bg="secondary">Tạm dừng</Badge>;
    } else if (now < startTime) {
      return <Badge bg="info">Sắp diễn ra</Badge>;
    } else if (now >= startTime && now <= endTime) {
      return <Badge bg="success">Đang diễn ra</Badge>;
    } else {
      return <Badge bg="danger">Đã kết thúc</Badge>;
    }
  };

  const formatDateTime = (dateString) => {
    return new Date(dateString).toLocaleString('vi-VN');
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
            <h2>
              <i className="fas fa-bolt me-2"></i>
              Quản lý Flash Sale
            </h2>
            <Button variant="primary" onClick={() => handleShowModal()}>
              <i className="fas fa-plus me-2"></i>
              Tạo chương trình mới
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
              <h5 className="mb-0">Danh sách chương trình Flash Sale</h5>
            </Card.Header>
            <Card.Body>
              {programs.length === 0 ? (
                <div className="text-center py-4">
                  <i className="fas fa-calendar-times fa-3x text-muted mb-3"></i>
                  <h5>Chưa có chương trình Flash Sale nào</h5>
                  <p className="text-muted">Tạo chương trình đầu tiên để bắt đầu</p>
                  <Button variant="primary" onClick={() => handleShowModal()}>
                    Tạo chương trình mới
                  </Button>
                </div>
              ) : (
                <Table responsive hover>
                  <thead>
                    <tr>
                      <th>Tên chương trình</th>
                      <th>Thời gian bắt đầu</th>
                      <th>Thời gian kết thúc</th>
                      <th>Trạng thái</th>
                      <th>Số sản phẩm</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {programs.map(program => (
                      <tr key={program.id}>
                        <td>
                          <strong>{program.name}</strong>
                          {program.description && (
                            <div className="text-muted small">{program.description}</div>
                          )}
                        </td>
                        <td>{formatDateTime(program.start_time)}</td>
                        <td>{formatDateTime(program.end_time)}</td>
                        <td>{getStatusBadge(program)}</td>
                        <td>
                          <Badge bg="info">{program.items_count || 0} sản phẩm</Badge>
                        </td>
                        <td>
                          <div className="d-flex gap-2">
                            <Button
                              size="sm"
                              variant="outline-primary"
                              as={Link}
                              to={`/admin/flash-sale/${program.id}/items`}
                            >
                              <i className="fas fa-box"></i>
                            </Button>
                            <Button
                              size="sm"
                              variant="outline-secondary"
                              onClick={() => handleShowModal(program)}
                            >
                              <i className="fas fa-edit"></i>
                            </Button>
                            <Button
                              size="sm"
                              variant="outline-danger"
                              onClick={() => handleDelete(program.id)}
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

      {/* Modal for Create/Edit Program */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingProgram ? 'Chỉnh sửa chương trình' : 'Tạo chương trình mới'}
          </Modal.Title>
        </Modal.Header>
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Tên chương trình *</Form.Label>
                  <Form.Control
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    placeholder="VD: Flash Sale 12:00"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Trạng thái</Form.Label>
                  <Form.Check
                    type="checkbox"
                    name="is_active"
                    label="Kích hoạt chương trình"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                  />
                </Form.Group>
              </Col>
            </Row>

            <Form.Group className="mb-3">
              <Form.Label>Mô tả</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Mô tả về chương trình Flash Sale..."
              />
            </Form.Group>

            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Thời gian bắt đầu *</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    name="start_time"
                    value={formData.start_time}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Thời gian kết thúc *</Form.Label>
                  <Form.Control
                    type="datetime-local"
                    name="end_time"
                    value={formData.end_time}
                    onChange={handleInputChange}
                    required
                  />
                </Form.Group>
              </Col>
            </Row>
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
                editingProgram ? 'Cập nhật' : 'Tạo mới'
              )}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  );
};

export default AdminFlashSale;
