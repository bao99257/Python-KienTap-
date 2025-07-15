import React, { useState, useEffect, useRef, useContext } from "react";
import UserContext from "../context/userContext";
import ChatBotProductCard from "./ChatBotProductCard";
import ChatBotOrderCard from "./ChatBotOrderCard";

// CSS styles for word wrapping
const chatStyles = `
  .chat-message-content {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
    word-break: break-word !important;
    white-space: pre-wrap !important;
    max-width: 100% !important;
  }

  .chat-container {
    word-wrap: break-word !important;
    overflow-wrap: break-word !important;
  }
`;

const ChatBot = () => {
  const { authTokens } = useContext(UserContext);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [config, setConfig] = useState({});
  const [wsConnected, setWsConnected] = useState(false);
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);

  const API_BASE = "/api/chatbot";

  // Scroll to bottom when messages change
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // WebSocket connection management
  const connectWebSocket = (sessionId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `ws://localhost:8000/ws/chatbot/${sessionId}/?token=${authTokens?.access}`;
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      console.log("WebSocket connected");
      setWsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);

      if (data.type === "message") {
        setMessages((prev) => [...prev, data.message]);
        setLoading(false);
      }
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket disconnected");
      setWsConnected(false);
    };

    wsRef.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      setWsConnected(false);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  };

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, []);

  // Fetch available models
  const fetchModels = async () => {
    try {
      const response = await fetch(`${API_BASE}/models/`, {
        headers: {
          Authorization: `JWT ${authTokens?.access}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setModels(data);
        if (data.length > 0 && !selectedModel) {
          setSelectedModel(data[0].name);
        }
      }
    } catch (error) {
      console.error("Error fetching models:", error);
    }
  };

  // Fetch user config
  const fetchConfig = async () => {
    try {
      const response = await fetch(`${API_BASE}/config/`, {
        headers: {
          Authorization: `JWT ${authTokens?.access}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setConfig(data);
        if (data.default_model && !selectedModel) {
          setSelectedModel(data.default_model);
        }
      }
    } catch (error) {
      console.error("Error fetching config:", error);
    }
  };

  // Fetch chat sessions
  const fetchSessions = async () => {
    try {
      const response = await fetch(`${API_BASE}/sessions/`, {
        headers: {
          Authorization: `JWT ${authTokens?.access}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSessions(data);
      }
    } catch (error) {
      console.error("Error fetching sessions:", error);
    }
  };

  // Fetch messages for a session
  const fetchSessionMessages = async (sessionId) => {
    try {
      const response = await fetch(`${API_BASE}/sessions/${sessionId}/`, {
        headers: {
          Authorization: `JWT ${authTokens?.access}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data.messages || []);
      }
    } catch (error) {
      console.error("Error fetching session messages:", error);
    }
  };

  // Send message to AI
  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput("");
    setLoading(true);

    // Add user message to UI immediately
    const tempUserMessage = {
      id: Date.now(),
      role: "user",
      content: userMessage,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);

    // Use WebSocket if connected, otherwise fallback to HTTP
    if (wsConnected && wsRef.current) {
      wsRef.current.send(
        JSON.stringify({
          type: "chat_message",
          message: userMessage,
          model: selectedModel,
        })
      );
    } else {
      // Fallback to HTTP API
      try {
        const response = await fetch(`${API_BASE}/chat/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `JWT ${authTokens?.access}`,
          },
          body: JSON.stringify({
            message: userMessage,
            session_id: currentSession?.id,
            model: selectedModel,
          }),
        });

        if (response.ok) {
          const data = await response.json();

          // Add AI response to messages with smart content
          const aiMessage = {
            id: Date.now() + 1,
            role: "assistant",
            content: data.message,
            timestamp: data.timestamp,
            model_used: data.model_used,
            response_type: data.type,
            // Add products, orders if available
            products: data.products || null,
            orders: data.orders || null,
            count: data.count || null,
          };

          setMessages((prev) => [...prev, aiMessage]);

          // Update current session or create new one
          if (!currentSession) {
            const newSession = {
              id: data.session_id,
              title:
                userMessage.length > 50
                  ? userMessage.substring(0, 50) + "..."
                  : userMessage,
              created_at: new Date().toISOString(),
              updated_at: new Date().toISOString(),
            };
            setCurrentSession(newSession);
            setSessions((prev) => [newSession, ...prev]);
          }
        } else {
          const errorData = await response.json();
          console.error("Error sending message:", errorData);
          // Remove the temporary user message on error
          setMessages((prev) => prev.slice(0, -1));
        }
      } catch (error) {
        console.error("Error sending message:", error);
        // Remove the temporary user message on error
        setMessages((prev) => prev.slice(0, -1));
      } finally {
        setLoading(false);
      }
    }
  };

  // Create new session
  const createNewSession = () => {
    setCurrentSession(null);
    setMessages([]);
    disconnectWebSocket();
  };

  // Select session
  const selectSession = (session) => {
    setCurrentSession(session);
    fetchSessionMessages(session.id);
    connectWebSocket(session.id);
  };

  // Initialize
  useEffect(() => {
    if (authTokens?.access) {
      fetchModels();
      fetchConfig();
      fetchSessions();
    }
  }, [authTokens]);

  if (!authTokens?.access) {
    return (
      <div
        className="d-flex justify-content-center align-items-center"
        style={{ height: "400px" }}
      >
        <div className="text-center">
          <h5>Vui lòng đăng nhập để sử dụng AI Chatbot</h5>
        </div>
      </div>
    );
  }

  return (
    <>
      <style>{chatStyles}</style>
      <div
        className="container-fluid chat-container"
        style={{ height: "90vh", maxHeight: "90vh" }}
      >
        <div className="row h-100">
          {/* Sidebar - Chat Sessions */}
          <div className="col-md-3 border-end">
            <div className="d-flex justify-content-between align-items-center p-3 border-bottom">
              <h6 className="mb-0">Chat Sessions</h6>
              <button
                className="btn btn-primary btn-sm"
                onClick={createNewSession}
              >
                New Chat
              </button>
            </div>

            <div
              className="list-group list-group-flush"
              style={{ maxHeight: "calc(100vh - 200px)", overflowY: "auto" }}
            >
              {sessions.map((session) => (
                <button
                  key={session.id}
                  className={`list-group-item list-group-item-action ${
                    currentSession?.id === session.id ? "active" : ""
                  }`}
                  onClick={() => selectSession(session)}
                >
                  <div className="d-flex w-100 justify-content-between">
                    <h6 className="mb-1">{session.title}</h6>
                    <small>
                      {new Date(session.updated_at).toLocaleDateString()}
                    </small>
                  </div>
                  {session.last_message && (
                    <p className="mb-1 text-muted small">
                      {session.last_message.content}
                    </p>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Main Chat Area */}
          <div className="col-md-9 d-flex flex-column">
            {/* Header */}
            <div className="p-3 border-bottom">
              <div className="d-flex justify-content-between align-items-center">
                <div className="d-flex align-items-center">
                  <h5 className="mb-0 me-3">AI Chatbot</h5>
                  {currentSession && (
                    <span
                      className={`badge ${
                        wsConnected ? "bg-success" : "bg-secondary"
                      }`}
                    >
                      {wsConnected ? "🟢 Real-time" : "🔴 HTTP"}
                    </span>
                  )}
                </div>
                <div className="d-flex align-items-center">
                  <label className="me-2">Model:</label>
                  <select
                    className="form-select form-select-sm"
                    value={selectedModel}
                    onChange={(e) => setSelectedModel(e.target.value)}
                    style={{ width: "auto" }}
                  >
                    {models.map((model) => (
                      <option key={model.name} value={model.name}>
                        {model.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div
              className="flex-grow-1 p-3"
              style={{
                overflowY: "auto",
                maxHeight: "calc(90vh - 250px)",
                minHeight: "400px",
                wordWrap: "break-word",
                overflowWrap: "break-word",
              }}
            >
              {messages.length === 0 ? (
                <div className="text-center text-muted mt-5">
                  <h4>👋 Chào bạn!</h4>
                  <p>Hãy bắt đầu cuộc trò chuyện với AI</p>
                </div>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={message.id || index}
                    className={`mb-3 d-flex ${
                      message.role === "user"
                        ? "justify-content-end"
                        : "justify-content-start"
                    }`}
                  >
                    {message.role === "user" ? (
                      // User message
                      <div
                        className="p-3 rounded bg-primary text-white"
                        style={{
                          maxWidth: "70%",
                          wordWrap: "break-word",
                          overflowWrap: "break-word",
                        }}
                      >
                        <div className="mb-1">
                          <strong>Bạn</strong>
                        </div>
                        <div className="chat-message-content">
                          {message.content}
                        </div>
                        <small className="text-muted">
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </small>
                      </div>
                    ) : (
                      // AI message with smart content
                      <div
                        style={{
                          maxWidth: "90%",
                          wordWrap: "break-word",
                          overflowWrap: "break-word",
                        }}
                      >
                        <div className="p-3 rounded bg-light mb-2">
                          <div className="mb-1">
                            <strong>AI</strong>
                            {message.model_used && (
                              <small className="text-muted ms-2">
                                ({message.model_used})
                              </small>
                            )}
                          </div>
                          <div className="chat-message-content">
                            {message.content}
                          </div>
                          <small className="text-muted">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </small>
                        </div>

                        {/* Render products if available */}
                        {message.products && message.products.length > 0 && (
                          <div className="mb-2">
                            <div className="d-flex flex-wrap justify-content-start">
                              {message.products.map((product) => (
                                <ChatBotProductCard
                                  key={product.id}
                                  product={product}
                                />
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Render orders if available */}
                        {message.orders && message.orders.length > 0 && (
                          <div className="mb-2">
                            <div className="d-flex flex-wrap justify-content-start">
                              {message.orders.map((order) => (
                                <ChatBotOrderCard
                                  key={order.id}
                                  order={order}
                                />
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ))
              )}
              {loading && (
                <div className="d-flex justify-content-start mb-3">
                  <div className="bg-light p-3 rounded">
                    <div
                      className="spinner-border spinner-border-sm me-2"
                      role="status"
                    ></div>
                    AI đang suy nghĩ...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-top">
              <div className="input-group">
                <input
                  type="text"
                  className="form-control"
                  placeholder="Nhập tin nhắn của bạn..."
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) =>
                    e.key === "Enter" && !e.shiftKey && sendMessage()
                  }
                  disabled={loading}
                />
                <button
                  className="btn btn-primary"
                  onClick={sendMessage}
                  disabled={loading || !input.trim()}
                >
                  {loading ? (
                    <span
                      className="spinner-border spinner-border-sm"
                      role="status"
                    ></span>
                  ) : (
                    "Gửi"
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default ChatBot;
