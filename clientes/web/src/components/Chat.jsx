import React, { useEffect, useRef } from 'react';

export function Chat({ messages }) {
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="chat-minimal">
            <div className="messages minimal-messages">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`message-minimal ${msg.type}`}>
                        <span className="time-meta">[{msg.time}]</span>{' '}
                        <strong>{msg.author}: </strong>
                        <span>{msg.text}</span>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </div>
        </div>
    );
}
