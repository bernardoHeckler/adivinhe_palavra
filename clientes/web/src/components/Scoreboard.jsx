import React from 'react';

export function Scoreboard({ players, scoreboard }) {
    const renderScores = () => {
        if (!scoreboard || scoreboard.length === 0) {
            return <div className="score-row" style={{justifyContent: 'center', color: 'var(--muted)'}}>Nenhum ponto ainda</div>;
        }
        return scoreboard.map((item, index) => (
            <div key={index} className="score-row">
                <strong>{item.usuario}</strong>
                <span>{item.pontos} pts</span>
            </div>
        ));
    };

    return (
        <section className="panel">
            <div className="panel-header">
                <h3>Placar</h3>
                <span>{players.length} jogadores</span>
            </div>
            <div className="scoreboard-list">
                {renderScores()}
            </div>
        </section>
    );
}
