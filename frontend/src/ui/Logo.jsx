import React from 'react';
import logo from '../assets/LogoWhite.png'; // Assuming white logo for dark theme

const Logo = () => {
    return (
        <div className="logo-container" style={{ display: 'flex', alignItems: 'center' }}>
            <img
                src={logo}
                className="logo"
                alt="MinerU Logo"
                style={{ height: '32px', objectFit: 'contain' }}
                onError={(e) => { e.target.style.display = 'none'; }} // Hide if fails
            />

        </div>
    );
};

export default Logo;
