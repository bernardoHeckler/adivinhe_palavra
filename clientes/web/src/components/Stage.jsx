import React, { useState } from 'react';
import { Chat } from './Chat';

export function Stage({ 
    room, 
    roundNumber, 
    timer, 
    category, 
    emojis, 
    subtitle, 
    feedback, 
    shakeGuess, 
    onSendGuess,
    messages,
    revealedAnswer
}) {
    const [guess, setGuess] = useState("");

    const handleGuess = (e) => {
        e.preventDefault();
        if (guess.trim()) {
            onSendGuess(guess.trim());
            setGuess("");
        }
    };

    return (
        <section className="stage-card">
            <div className="stage-topbar">
                <div>
                    <p className="eyebrow">Sala <span>{room}</span></p>
                    <h2>Rodada {roundNumber}</h2>
                </div>
                <div className="timer-badge">
                    <span>Tempo</span>
                    <strong>{timer > 0 ? timer : "--"}</strong>
                </div>
            </div>

            <div className="emoji-stage">
                <p className="category-pill">{category}</p>
                {revealedAnswer ? (
                    <div className="emoji-display answer-reveal">{revealedAnswer}</div>
                ) : (
                    <div className="emoji-display">{emojis}</div>
                )}
                <p className="stage-subtitle">{revealedAnswer ? "A resposta era essa!" : subtitle}</p>
            </div>

            <div className={`feedback-banner ${feedback ? feedback.type : "hidden"}`}>
                {feedback ? feedback.text : ""}
            </div>

            <div className={`guess-box ${shakeGuess ? "shake" : ""}`}>
                <form onSubmit={handleGuess} className="guess-form">
                    <input 
                        value={guess}
                        onChange={e => setGuess(e.target.value)}
                        autoComplete="off"
                        placeholder="Digite seu palpite ou converse com a sala"
                    />
                    <button type="submit">Enviar</button>
                </form>
            </div>

            <Chat messages={messages} />
        </section>
    );
}
