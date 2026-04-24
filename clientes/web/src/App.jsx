import React, { useState } from 'react';
import { LoginScreen } from './components/LoginScreen';
import { GameScreen } from './components/GameScreen';
import { useGameSocket } from './hooks/useGameSocket';

export default function App() {
    const { gameState, connect, sendGuess, sendReady } = useGameSocket();
    const [inGame, setInGame] = useState(false);

    const handleConnect = async (room, username) => {
        try {
            await connect(room, username);
            setInGame(true);
        } catch (error) {
            alert("Não foi possível conectar ao servidor.");
        }
    };

    return (
        <div className={`page-shell ${inGame ? "in-game-shell" : "login-shell"}`}>
            {!inGame ? (
                <LoginScreen onConnect={handleConnect} />
            ) : (
                <GameScreen gameState={gameState} sendGuess={sendGuess} sendReady={sendReady} />
            )}
        </div>
    );
}
