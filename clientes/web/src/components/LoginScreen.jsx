import React, { useState } from 'react';

export function LoginScreen({ onConnect }) {
    const [username, setUsername] = useState("");
    const [room, setRoom] = useState("");

    React.useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const salaDaUrl = urlParams.get("sala");
        if (salaDaUrl) {
            setRoom(salaDaUrl);
        }
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (username.trim()) {
            onConnect(room || "default", username.trim());
        }
    };

    return (
        <section className="hero-card">
            <div className="hero-copy">
                <p className="eyebrow">Multiplayer em tempo real</p>
                <h1>Advinhe.io</h1>
                <p className="hero-text">
                    Entre em uma sala, receba um desafio em emojis e tente acertar antes da galera
                </p>
            </div>

            <form onSubmit={handleSubmit} className="login-card">
                <label>
                    <span>Seu nome</span>
                    <input 
                        name="usuario" 
                        maxLength="24" 
                        placeholder="Ex: Bernardo" 
                        required 
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                    />
                </label>
                <label>
                    <span>Sala</span>
                    <input 
                        name="sala" 
                        maxLength="24" 
                        placeholder="Ex: amigos" 
                        value={room}
                        onChange={e => setRoom(e.target.value)}
                    />
                </label>
                <button type="submit">Entrar na rodada</button>
                <p className="login-hint">Crie uma sala e convide seus amigos</p>
            </form>
        </section>
    );
}
