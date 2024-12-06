import React, { useState } from "react";
import axios from "../api";

const Preferences = () => {
    const [preferences, setPreferences] = useState({
        theme: "dark",
        avatar: "default",
        language: "en",
        notificationSound: true,
    });

    const handleSave = async () => {
        await axios.put("/preferences", preferences);
        alert("Preferences saved!");
    };

    return (
        <div className="preferences">
            <h3>User Preferences</h3>
            <label>
                Theme:
                <select
                    value={preferences.theme}
                    onChange={(e) => setPreferences({ ...preferences, theme: e.target.value })}
                >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                </select>
            </label>
            <label>
                Avatar:
                <input
                    type="text"
                    value={preferences.avatar}
                    onChange={(e) => setPreferences({ ...preferences, avatar: e.target.value })}
                />
            </label>
            <label>
                Language:
                <input
                    type="text"
                    value={preferences.language}
                    onChange={(e) => setPreferences({ ...preferences, language: e.target.value })}
                />
            </label>
            <label>
                Notification Sound:
                <input
                    type="checkbox"
                    checked={preferences.notificationSound}
                    onChange={(e) =>
                        setPreferences({
                            ...preferences,
                            notificationSound: e.target.checked,
                        })
                    }
                />
            </label>
            <button onClick={handleSave}>Save Preferences</button>
        </div>
    );
};

export default Preferences;
