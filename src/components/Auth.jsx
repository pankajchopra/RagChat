import React from "react";

const Auth = () => {
    const handleLogin = () => {
        window.location.href = "https://accounts.google.com/o/oauth2/auth"; // Replace with your OAuth URL
    };

    return (
        <div className="auth">
            <h3>Login to RAGgpt</h3>
            <button onClick={handleLogin}>Login with Google</button>
        </div>
    );
};

export default Auth;
