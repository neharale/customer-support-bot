import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const ADMIN_API_BASE_URL = "http://127.0.0.1:8000/api/admin";
const CHAT_API_URL = "http://127.0.0.1:8000/api/chat";
const AUTH_API_URL = "http://127.0.0.1:8000/api/auth/login";

function App() {
  const [token, setToken] = useState(localStorage.getItem("admin_token"));
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState("");

  const [tickets, setTickets] = useState([]);
  const [analytics, setAnalytics] = useState(null);

  const [selectedUserId, setSelectedUserId] = useState(null);
  const [conversations, setConversations] = useState([]);

  const [priorityFilter, setPriorityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");

  const [chatUserId, setChatUserId] = useState("demo_user");
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  const getAuthHeaders = () => ({
    Authorization: `Bearer ${token}`,
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoginError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", username);
      formData.append("password", password);

      const response = await axios.post(AUTH_API_URL, formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const accessToken = response.data.access_token;
      localStorage.setItem("admin_token", accessToken);
      setToken(accessToken);
      setPassword("");
    } catch (error) {
      setLoginError("Invalid username or password.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setToken(null);
    setTickets([]);
    setAnalytics(null);
    setConversations([]);
    setSelectedUserId(null);
  };

  const handleAuthError = (error) => {
    if (error.response && error.response.status === 401) {
      handleLogout();
    }
  };

  const fetchTickets = async () => {
    try {
      const params = {};

      if (priorityFilter) params.priority = priorityFilter;
      if (statusFilter) params.status = statusFilter;
      if (userFilter.trim()) params.user_id = userFilter.trim();

      const response = await axios.get(`${ADMIN_API_BASE_URL}/tickets`, {
        params,
        headers: getAuthHeaders(),
      });

      setTickets(response.data);
    } catch (error) {
      handleAuthError(error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${ADMIN_API_BASE_URL}/analytics`, {
        headers: getAuthHeaders(),
      });

      setAnalytics(response.data);
    } catch (error) {
      handleAuthError(error);
    }
  };

  const clearFilters = async () => {
    setUserFilter("");
    setPriorityFilter("");
    setStatusFilter("");

    try {
      const response = await axios.get(`${ADMIN_API_BASE_URL}/tickets`, {
        headers: getAuthHeaders(),
      });

      setTickets(response.data);
    } catch (error) {
      handleAuthError(error);
    }
  };

  const fetchConversations = async (userId) => {
    try {
      setSelectedUserId(userId);

      const response = await axios.get(
        `${ADMIN_API_BASE_URL}/conversations/${userId}`,
        {
          headers: getAuthHeaders(),
        }
      );

      setConversations(response.data);
    } catch (error) {
      handleAuthError(error);
    }
  };

  const updateStatus = async (ticketId, status) => {
    try {
      await axios.patch(
        `${ADMIN_API_BASE_URL}/tickets/${ticketId}/status`,
        { status },
        {
          headers: getAuthHeaders(),
        }
      );

      await fetchTickets();
      await fetchAnalytics();
    } catch (error) {
      handleAuthError(error);
    }
  };

  const sendChatMessage = async () => {
    if (!chatMessage.trim()) return;

    const userMsg = {
      sender: "user",
      text: chatMessage,
    };

    setChatHistory((prev) => [...prev, userMsg]);
    setChatLoading(true);

    try {
      const response = await axios.post(CHAT_API_URL, {
        user_id: chatUserId,
        message: chatMessage,
      });

      const botMsg = {
        sender: "bot",
        text: response.data.message,
        escalated: response.data.escalated,
        ticket_id: response.data.ticket_id,
        priority: response.data.priority,
        confidence_score: response.data.confidence_score,
      };

      setChatHistory((prev) => [...prev, botMsg]);
      setChatMessage("");

      if (token) {
        await fetchTickets();
        await fetchAnalytics();

        if (response.data.escalated) {
          await fetchConversations(chatUserId);
        }
      }
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Something went wrong while sending the message.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const clearChat = () => {
    setChatHistory([]);
    setChatMessage("");
  };

  useEffect(() => {
    if (token) {
      fetchTickets();
      fetchAnalytics();
    }
  }, [token]);

  if (!token) {
    return (
      <div className="login-page">
        <form className="login-card" onSubmit={handleLogin}>
          <h1>Admin Login</h1>
          <p>Sign in to manage AI support tickets.</p>

          {loginError && <div className="login-error">{loginError}</div>}

          <label>Username</label>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Enter the username"
          />

          <label>Password</label>
          <input
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter the password"
            type="password"
          />

          <button className="primary-button login-button" type="submit">
            Login
          </button>
        </form>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="top-header">
        <div>
          <h1>AI Support Admin Dashboard</h1>
          <p>
            Test customer chats, view escalated tickets, update statuses,
            inspect conversation history, and monitor support analytics.
          </p>
        </div>

        <button className="secondary-button" onClick={handleLogout}>
          Logout
        </button>
      </header>

      {analytics && (
        <section className="analytics-grid">
          <div className="analytics-card">
            <h3>Total Tickets</h3>
            <p>{analytics.total_tickets}</p>
          </div>

          <div className="analytics-card">
            <h3>Open Tickets</h3>
            <p>{analytics.open_tickets}</p>
          </div>

          <div className="analytics-card critical">
            <h3>P0 Tickets</h3>
            <p>{analytics.p0_tickets}</p>
          </div>

          <div className="analytics-card">
            <h3>Escalation Rate</h3>
            <p>{analytics.escalation_rate}%</p>
          </div>

          <div className="analytics-card">
            <h3>Avg Confidence</h3>
            <p>{analytics.average_confidence_score}</p>
          </div>
        </section>
      )}

      <section className="filters">
        <input
          value={userFilter}
          onChange={(e) => setUserFilter(e.target.value)}
          placeholder="Filter by User ID"
          onKeyDown={(e) => {
            if (e.key === "Enter") fetchTickets();
          }}
        />

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
        >
          <option value="">All Priorities</option>
          <option value="P0">P0 Critical</option>
          <option value="P1">P1 High</option>
          <option value="P2">P2 Medium</option>
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="OPEN">OPEN</option>
          <option value="IN_PROGRESS">IN_PROGRESS</option>
          <option value="CLOSED">CLOSED</option>
        </select>

        <button className="primary-button" onClick={fetchTickets}>
          Search
        </button>

        <button className="secondary-button" onClick={clearFilters}>
          Clear Filters
        </button>
      </section>

      <main className="layout">
        <section className="panel chat-panel">
          <div className="panel-header">
            <h2>Customer Chat Simulator</h2>

            <div className="panel-actions">
              <button className="secondary-button" onClick={clearChat}>
                Clear Chat
              </button>
            </div>
          </div>

          <div className="chat-controls">
            <input
              value={chatUserId}
              onChange={(e) => setChatUserId(e.target.value)}
              placeholder="User ID"
            />
          </div>

          <div className="chat-box">
            {chatHistory.length === 0 && (
              <p className="empty">Send a message to test the bot.</p>
            )}

            {chatHistory.map((msg, index) => (
              <div
                key={index}
                className={`chat-message ${
                  msg.sender === "user" ? "user-message" : "bot-message"
                }`}
              >
                <p>{msg.text}</p>

                {msg.escalated && (
                  <div className="chat-meta">
                    Escalated: Yes | Ticket: {msg.ticket_id} | Priority:{" "}
                    {msg.priority}
                  </div>
                )}

                {msg.confidence_score !== undefined && (
                  <div className="chat-meta">
                    Confidence: {msg.confidence_score}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="chat-input-row">
            <input
              value={chatMessage}
              onChange={(e) => setChatMessage(e.target.value)}
              placeholder="Type customer message..."
              onKeyDown={(e) => {
                if (e.key === "Enter") sendChatMessage();
              }}
            />

            <button onClick={sendChatMessage} disabled={chatLoading}>
              {chatLoading ? "Sending..." : "Send"}
            </button>
          </div>
        </section>

        <section className="panel tickets-panel">
          <h2>Tickets</h2>

          {tickets.length === 0 ? (
            <p className="empty">No tickets found.</p>
          ) : (
            <table>
              <thead>
                <tr>
                  <th>Ticket</th>
                  <th>User</th>
                  <th>Priority</th>
                  <th>Status</th>
                  <th>Issue</th>
                  <th>Summary</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {tickets.map((ticket) => (
                  <tr key={ticket.id}>
                    <td>{ticket.id}</td>
                    <td>
                      <button
                        className="link-button"
                        onClick={() => fetchConversations(ticket.user_id)}
                      >
                        {ticket.user_id}
                      </button>
                    </td>
                    <td>
                      <span className={`badge ${ticket.priority}`}>
                        {ticket.priority}
                      </span>
                    </td>
                    <td>{ticket.status}</td>
                    <td>{ticket.issue_summary}</td>
                    <td>{ticket.summary || "No summary"}</td>
                    <td>
                      <select
                        value={ticket.status}
                        onChange={(e) =>
                          updateStatus(ticket.id, e.target.value)
                        }
                      >
                        <option value="OPEN">OPEN</option>
                        <option value="IN_PROGRESS">IN_PROGRESS</option>
                        <option value="CLOSED">CLOSED</option>
                      </select>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="panel conversation-panel">
          <h2>
            Conversation History{" "}
            {selectedUserId ? `for ${selectedUserId}` : ""}
          </h2>

          {!selectedUserId && (
            <p className="empty">Select a user from the tickets table.</p>
          )}

          {conversations.map((conv) => (
            <div className="conversation-card" key={conv.id}>
              <p>
                <strong>User:</strong> {conv.message}
              </p>
              <p>
                <strong>Bot:</strong> {conv.bot_response}
              </p>
              <div className="meta">
                <span>Sentiment: {conv.sentiment}</span>
                <span>Confidence: {conv.confidence_score}</span>
                <span>Escalated: {String(conv.escalated)}</span>
              </div>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}

export default App;