import React, { useState, useEffect } from "react";
import axios from "../api";

const HistoryPanel = () => {
    const [history, setHistory] = useState([]);
    const [selected, setSelected] = useState(null);

    useEffect(() => {
        fetchHistory();
    }, []);

    const fetchHistory = async () => {
        const response = await axios.get("/conversations");
        setHistory(response.data);
    };

    const deleteConversation = async (id) => {
        await axios.delete(`/conversations/${id}`);
        fetchHistory();
    };

    const renameConversation = async (id, newName) => {
        await axios.put(`/conversations/${id}`, { name: newName });
        fetchHistory();
    };

    return (
        <div className="history-panel">
            <h3>Conversation History</h3>
            <ul>
                {history.map((conv) => (
                    <li key={conv.id}>
                        <span>{conv.name}</span>
                        <button onClick={() => setSelected(conv)}>Rename</button>
                        <button onClick={() => deleteConversation(conv.id)}>Delete</button>
                    </li>
                ))}
            </ul>
            {selected && (
                <div className="rename-modal">
                    <input
                        type="text"
                        placeholder="New name"
                        onChange={(e) => renameConversation(selected.id, e.target.value)}
                    />
                    <button onClick={() => setSelected(null)}>Close</button>
                </div>
            )}
        </div>
    );
};

export default HistoryPanel;
