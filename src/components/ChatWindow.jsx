import React, { useState, useEffect } from "react";
import SpeechRecognition, { useSpeechRecognition } from "react-speech-recognition";
import io from "socket.io-client";

const socket = io('http://localhost:8000'); // Backend server URL
const ChatWindow = () => {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState("");
    const { transcript, listening, resetTranscript } = useSpeechRecognition();
    const recognition = new SpeechRecognition();
    useEffect(() => {
        // if (!SpeechRecognition.browserSupportsSpeechRecognition()) {
        //     alert("Your browser does not support Speech-to-Text");
        // }

        socket.on("response", (data) => {
            setMessages((prev) => [...prev, { text: data, isUser: false }]);
        });

        return () => socket.disconnect();
    }, []);

    const handleSend = () => {
        socket.emit("query", input);
        setMessages((prev) => [...prev, { text: input, isUser: true }]);
        setInput("");
    };

    const handleSpeech = () => {
        resetTranscript();
        recognition.startListening();
    };

    const handleStop = () => {
        recognition.stopListening();
        setInput(transcript);
    };

    return (
        <div className="chat-window">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} style={{ color: msg.isUser ? "black" : "blue" }}>
                        {msg.text}
                    </div>
                ))}
            </div>
            <div>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your query..."
                />
                <button onClick={handleSend}>Send</button>
                <button onClick={handleSpeech} disabled={listening}>Start Speaking</button>
                <button onClick={handleStop} disabled={!listening}>Stop</button>
            </div>
        </div>
    );
};

export default ChatWindow;
