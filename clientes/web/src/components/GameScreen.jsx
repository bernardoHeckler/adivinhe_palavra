import React, { useState, useEffect } from 'react';
import { Stage } from './Stage';
import { Scoreboard } from './Scoreboard';
import { QRCodeInvite } from './QRCodeInvite';

export function GameScreen({ gameState, sendGuess, sendReady }) {
    const [isReady, setIsReady] = useState(false);

    useEffect(() => {
        if (!gameState.matchResult) {
            setIsReady(false);
        }
    }, [gameState.matchResult]);

    const handleReady = () => {
        setIsReady(true);
        if (sendReady) sendReady();
    };

    return (
        <main className="game-layout">
            <aside className="sidebar left-sidebar">
                <Scoreboard
                    players={gameState.players}
                    scoreboard={gameState.scoreboard}
                />
            </aside>

            <Stage
                room={gameState.room}
                roundNumber={gameState.roundNumber}
                timer={gameState.timer}
                category={gameState.category}
                emojis={gameState.emojis}
                subtitle={gameState.subtitle}
                feedback={gameState.feedback}
                shakeGuess={gameState.shakeGuess}
                onSendGuess={sendGuess}
                messages={gameState.messages}
                revealedAnswer={gameState.revealedAnswer}
            />

            <aside className="sidebar right-sidebar">
                <div className="hero-copy" style={{ padding: 0 }}>
                    <p className="eyebrow">Multiplayer em tempo real</p>
                    <h1 data-text="Adivinhe.io" style={{ fontSize: 'clamp(1.8rem, 4vw, 2.5rem)' }}>Adivinhe.io</h1>
                    <p className="hero-text" style={{ fontSize: '0.9rem' }}>
                        Entre em uma sala, receba um desafio em emojis e tente acertar antes da galera
                    </p>
                </div>

                {gameState.ipServidor && gameState.room && (
                    <QRCodeInvite
                        ipServidor={gameState.ipServidor}
                        room={gameState.room}
                    />
                )}
            </aside>

            {gameState.matchResult && (
                <div className="modal-overlay">
                    <div className="modal-content">
                        <h2>🎉 Partida Encerrada!</h2>
                        <p className="winner-text"><strong>{gameState.matchResult.winner}</strong> atingiu a meta de {gameState.matchResult.target} pontos.</p>

                        <div className="top3-list">
                            <h3>Top 3 Jogadores:</h3>
                            {gameState.matchResult.top3.map((p, i) => (
                                <div key={i} className="top3-item">
                                    <span>{i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉'} {p.usuario}</span>
                                    <strong>{p.pontos} pts</strong>
                                </div>
                            ))}
                        </div>

                        <div style={{ marginTop: '20px' }}>
                            <button
                                onClick={handleReady}
                                disabled={isReady}
                                className="ready-btn"
                            >
                                {isReady ? "Aguardando outros jogadores..." : `Próxima Partida (${gameState.matchResult.prontos}/${gameState.matchResult.total_jogadores})`}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}
