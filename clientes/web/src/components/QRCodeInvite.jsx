import React from 'react';
import { QRCodeSVG } from 'qrcode.react';

export function QRCodeInvite({ ipServidor, room }) {
    if (!ipServidor || !room) return null;

    const porta = window.location.port ? `:${window.location.port}` : "";
    const url = `http://${ipServidor}${porta}/?sala=${encodeURIComponent(room)}`;

    return (
        <div className="hero-qrcode-container">
            <p className="eyebrow" style={{margin: 0}}>Convide seus amigos</p>
            <div className="hero-qrcode-box" style={{ display: 'flex' }}>
                <QRCodeSVG 
                    value={url} 
                    size={120} 
                    bgColor={"#ffffff"} 
                    fgColor={"#0f172a"} 
                    level={"L"} 
                />
            </div>
        </div>
    );
}
