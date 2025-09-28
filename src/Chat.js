import React, { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function Chat() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "👋 Hello, do you have any questions? I'm here to help!" }
  ]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setTyping(true);

    const messageToSend = input; // Store before clearing
    setInput(""); // Clear input immediately

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat", {
        message: messageToSend,
      });
      typeBotMessage(res.data.reply);
    } catch (err) {
      console.error(err);
      setTyping(false);
    }
  };

  const typeBotMessage = (text) => {
    let index = 0;
    let typedText = "";
    const botMsg = { sender: "bot", text: "" };
    setMessages((prev) => [...prev, botMsg]);

    const interval = setInterval(() => {
      typedText += text[index];
      index++;
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = { sender: "bot", text: typedText };
        return newMessages;
      });

      if (index >= text.length) {
        clearInterval(interval);
        setTyping(false);
      }
    }, 30);
  };

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  return (
    <div className="chat-container">
      <h1>Ask Steve</h1>
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.sender}`}>
            {msg.sender === "bot" && <span className="bot-icon">🤖</span>}
            <span className="message-text">{msg.text}</span>
          </div>
        ))}
        {typing && <div className="message bot">🤖 Thinking...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="input-box">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              sendMessage();
            }
          }}
          placeholder="Ask me anything..."
        />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
