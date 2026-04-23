import React from 'react';
import { Stage } from './Stage';
import { Scoreboard } from './Scoreboard';
import { Chat } from './Chat';
import { QRCodeInvite } from './QRCodeInvite';

export function GameScreen({ gameState, sendGuess }) {
    return (
        <main className="game-layout">
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
            />

            <aside className="sidebar">
                <Scoreboard 
                    players={gameState.players} 
                    scoreboard={gameState.scoreboard} 
                />
                
                {gameState.ipServidor && gameState.room && (
                    <QRCodeInvite 
                        ipServidor={gameState.ipServidor} 
                        room={gameState.room} 
                    />
                )}

                <Chat 
                    messages={gameState.messages} 
                    status={gameState.status} 
                    connected={gameState.connected} 
                />
            </aside>
        </main>
    );
}
