import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const ADMIN_API_BASE_URL = "http://127.0.0.1:8000/api/admin";
const CHAT_API_URL = "http://127.0.0.1:8000/api/chat";

function App() {
  const [tickets, setTickets] = useState([]);
  const [selectedUserId, setSelectedUserId] = useState(null);
  const [conversations, setConversations] = useState([]);

  const [priorityFilter, setPriorityFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [userFilter, setUserFilter] = useState("");

  const [chatUserId, setChatUserId] = useState("demo_user");
  const [chatMessage, setChatMessage] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  const fetchTickets = async () => {
    const params = {};

    if (priorityFilter) params.priority = priorityFilter;
    if (statusFilter) params.status = statusFilter;
    if (userFilter.trim()) params.user_id = userFilter.trim();

    const response = await axios.get(`${ADMIN_API_BASE_URL}/tickets`, {
      params,
    });

    setTickets(response.data);
  };

  const clearFilters = async () => {
    setUserFilter("");
    setPriorityFilter("");
    setStatusFilter("");

    const response = await axios.get(`${ADMIN_API_BASE_URL}/tickets`);
    setTickets(response.data);
  };

  const fetchConversations = async (userId) => {
    setSelectedUserId(userId);

    const response = await axios.get(
      `${ADMIN_API_BASE_URL}/conversations/${userId}`
    );

    setConversations(response.data);
  };

  const updateStatus = async (ticketId, status) => {
    await axios.patch(`${ADMIN_API_BASE_URL}/tickets/${ticketId}/status`, {
      status,
    });

    await fetchTickets();
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

      await fetchTickets();

      if (response.data.escalated) {
        await fetchConversations(chatUserId);
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
    fetchTickets();
  }, []);

  return (
    <div className="app">
      <header>
        <h1>AI Support Admin Dashboard</h1>
        <p>
          Test customer chats, view escalated tickets, update statuses, and
          inspect conversation history.
        </p>
      </header>

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