import React, { useEffect, useRef } from 'react';

export function Chat({ messages, status, connected }) {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const statusClass = connected ? "online" : "offline";

    return (
        <section className="panel">
            <div className="panel-header">
                <h3>Chat da sala</h3>
                <span className={`status-pill ${statusClass}`}>{status}</span>
            </div>
            <div className="messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message ${msg.type}`}>
                        <div className="meta">
                            <strong>{msg.author}</strong>
                            <span>{msg.time}</span>
                        </div>
                        <p>{msg.text}</p>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
        </section>
    );
}
