import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Table, Button, Form, Modal, Alert, Badge } from 'react-bootstrap';
import { FaRobot, FaComments, FaUsers, FaChartLine, FaPlus, FaEdit, FaTrash } from 'react-icons/fa';
import AdminLayout from '../../components/admin/AdminLayout';

const AdminAIChat = () => {
  const [stats, setStats] = useState({});
  const [conversations, setConversations] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [showKnowledgeModal, setShowKnowledgeModal] = useState(false);
  const [editingKnowledge, setEditingKnowledge] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [knowledgeForm, setKnowledgeForm] = useState({
    knowledge_type: 'faq',
    question: '',
    answer: '',
    keywords: [],
    is_active: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('authTokens') ? 
        JSON.parse(localStorage.getItem('authTokens')).access : null;

      // Fetch stats
      const statsResponse = await fetch('/ai/admin/stats/', {
        headers: { 'Authorization': `JWT ${token}` }
      });
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStats(statsData);
      }

      // Fetch conversations
      const conversationsResponse = await fetch('/ai/admin/conversations/', {
        headers: { 'Authorization': `JWT ${token}` }
      });
      if (conversationsResponse.ok) {
        const conversationsData = await conversationsResponse.json();
        setConversations(conversationsData.conversations || []);
      }

      // Fetch knowledge base
      const knowledgeResponse = await fetch('/ai/admin/knowledge/', {
        headers: { 'Authorization': `JWT ${token}` }
      });
      if (knowledgeResponse.ok) {
        const knowledgeData = await knowledgeResponse.json();
        setKnowledgeBase(knowledgeData);
      }

    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Có lỗi xảy ra khi tải dữ liệu');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveKnowledge = async () => {
    try {
      const token = localStorage.getItem('authTokens') ? 
        JSON.parse(localStorage.getItem('authTokens')).access : null;

      const url = editingKnowledge ? 
        `/ai/admin/knowledge/${editingKnowledge.id}/` : 
        '/ai/admin/knowledge/';
      
      const method = editingKnowledge ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `JWT ${token}`
        },
        body: JSON.stringify(knowledgeForm)
      });

      if (response.ok) {
        setShowKnowledgeModal(false);
        setEditingKnowledge(null);
        setKnowledgeForm({
          knowledge_type: 'faq',
          question: '',
          answer: '',
          keywords: [],
          is_active: true
        });
        fetchData();
      } else {
        setError('Có lỗi xảy ra khi lưu knowledge base');
      }
    } catch (error) {
      console.error('Error saving knowledge:', error);
      setError('Có lỗi xảy ra khi lưu knowledge base');
    }
  };

  const handleEditKnowledge = (knowledge) => {
    setEditingKnowledge(knowledge);
    setKnowledgeForm({
      knowledge_type: knowledge.knowledge_type,
      question: knowledge.question,
      answer: knowledge.answer,
      keywords: knowledge.keywords,
      is_active: knowledge.is_active
    });
    setShowKnowledgeModal(true);
  };

  const handleDeleteKnowledge = async (id) => {
    if (!window.confirm('Bạn có chắc chắn muốn xóa knowledge base này?')) return;

    try {
      const token = localStorage.getItem('authTokens') ? 
        JSON.parse(localStorage.getItem('authTokens')).access : null;

      const response = await fetch(`/ai/admin/knowledge/${id}/`, {
        method: 'DELETE',
        headers: { 'Authorization': `JWT ${token}` }
      });

      if (response.ok) {
        fetchData();
      } else {
        setError('Có lỗi xảy ra khi xóa knowledge base');
      }
    } catch (error) {
      console.error('Error deleting knowledge:', error);
      setError('Có lỗi xảy ra khi xóa knowledge base');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('vi-VN');
  };

  const getKnowledgeTypeLabel = (type) => {
    const types = {
      'faq': 'FAQ',
      'product_info': 'Thông tin sản phẩm',
      'size_guide': 'Hướng dẫn size',
      'policy': 'Chính sách',
      'general': 'Chung'
    };
    return types[type] || type;
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <Container fluid>
        <Row className="mb-4">
          <Col>
            <h2><FaRobot className="me-2" />Quản lý AI Chat</h2>
          </Col>
        </Row>

        {error && (
          <Alert variant="danger" dismissible onClose={() => setError('')}>
            {error}
          </Alert>
        )}

        {/* Stats Cards */}
        <Row className="mb-4">
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <FaComments size={30} className="text-primary mb-2" />
                <h4>{stats.total_conversations || 0}</h4>
                <p className="text-muted">Tổng cuộc hội thoại</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <FaUsers size={30} className="text-success mb-2" />
                <h4>{stats.active_conversations || 0}</h4>
                <p className="text-muted">Cuộc hội thoại đang hoạt động</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <FaChartLine size={30} className="text-info mb-2" />
                <h4>{stats.total_messages || 0}</h4>
                <p className="text-muted">Tổng tin nhắn</p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="text-center">
              <Card.Body>
                <FaRobot size={30} className="text-warning mb-2" />
                <h4>{knowledgeBase.length}</h4>
                <p className="text-muted">Knowledge Base</p>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Recent Conversations */}
        <Row className="mb-4">
          <Col>
            <Card>
              <Card.Header>
                <h5>Cuộc hội thoại gần đây</h5>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Session ID</th>
                      <th>Người dùng</th>
                      <th>Tin nhắn</th>
                      <th>Cập nhật</th>
                      <th>Trạng thái</th>
                    </tr>
                  </thead>
                  <tbody>
                    {conversations.slice(0, 10).map((conversation) => (
                      <tr key={conversation.id}>
                        <td>{conversation.session_id.substring(0, 8)}...</td>
                        <td>{conversation.user?.username || 'N/A'}</td>
                        <td>{conversation.messages?.length || 0}</td>
                        <td>{formatDate(conversation.updated_at)}</td>
                        <td>
                          <Badge bg={conversation.is_active ? 'success' : 'secondary'}>
                            {conversation.is_active ? 'Hoạt động' : 'Không hoạt động'}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Knowledge Base Management */}
        <Row>
          <Col>
            <Card>
              <Card.Header className="d-flex justify-content-between align-items-center">
                <h5>Quản lý Knowledge Base</h5>
                <Button 
                  variant="primary" 
                  onClick={() => setShowKnowledgeModal(true)}
                >
                  <FaPlus className="me-1" />
                  Thêm mới
                </Button>
              </Card.Header>
              <Card.Body>
                <Table responsive>
                  <thead>
                    <tr>
                      <th>Loại</th>
                      <th>Câu hỏi</th>
                      <th>Trạng thái</th>
                      <th>Cập nhật</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {knowledgeBase.map((knowledge) => (
                      <tr key={knowledge.id}>
                        <td>
                          <Badge bg="info">
                            {getKnowledgeTypeLabel(knowledge.knowledge_type)}
                          </Badge>
                        </td>
                        <td>{knowledge.question.substring(0, 50)}...</td>
                        <td>
                          <Badge bg={knowledge.is_active ? 'success' : 'secondary'}>
                            {knowledge.is_active ? 'Hoạt động' : 'Không hoạt động'}
                          </Badge>
                        </td>
                        <td>{formatDate(knowledge.updated_at)}</td>
                        <td>
                          <Button
                            variant="outline-primary"
                            size="sm"
                            className="me-1"
                            onClick={() => handleEditKnowledge(knowledge)}
                          >
                            <FaEdit />
                          </Button>
                          <Button
                            variant="outline-danger"
                            size="sm"
                            onClick={() => handleDeleteKnowledge(knowledge.id)}
                          >
                            <FaTrash />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          </Col>
        </Row>

        {/* Knowledge Base Modal */}
        <Modal show={showKnowledgeModal} onHide={() => setShowKnowledgeModal(false)} size="lg">
          <Modal.Header closeButton>
            <Modal.Title>
              {editingKnowledge ? 'Chỉnh sửa' : 'Thêm mới'} Knowledge Base
            </Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Loại</Form.Label>
                <Form.Select
                  value={knowledgeForm.knowledge_type}
                  onChange={(e) => setKnowledgeForm({...knowledgeForm, knowledge_type: e.target.value})}
                >
                  <option value="faq">FAQ</option>
                  <option value="product_info">Thông tin sản phẩm</option>
                  <option value="size_guide">Hướng dẫn size</option>
                  <option value="policy">Chính sách</option>
                  <option value="general">Chung</option>
                </Form.Select>
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Câu hỏi</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={3}
                  value={knowledgeForm.question}
                  onChange={(e) => setKnowledgeForm({...knowledgeForm, question: e.target.value})}
                  placeholder="Nhập câu hỏi..."
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Label>Câu trả lời</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={5}
                  value={knowledgeForm.answer}
                  onChange={(e) => setKnowledgeForm({...knowledgeForm, answer: e.target.value})}
                  placeholder="Nhập câu trả lời..."
                />
              </Form.Group>

              <Form.Group className="mb-3">
                <Form.Check
                  type="checkbox"
                  label="Hoạt động"
                  checked={knowledgeForm.is_active}
                  onChange={(e) => setKnowledgeForm({...knowledgeForm, is_active: e.target.checked})}
                />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={() => setShowKnowledgeModal(false)}>
              Hủy
            </Button>
            <Button variant="primary" onClick={handleSaveKnowledge}>
              Lưu
            </Button>
          </Modal.Footer>
        </Modal>
      </Container>
    </AdminLayout>
  );
};

export default AdminAIChat;
