import React, { useState, useEffect } from "react";
import axios from "../api";

const PersonaManager = () => {
    const [personas, setPersonas] = useState([]);
    const [selectedPersona, setSelectedPersona] = useState(null);
    const [formData, setFormData] = useState({ name: "", background: "" });

    useEffect(() => {
        fetchPersonas();
    }, []);

    const fetchPersonas = async () => {
        const response = await axios.get("/personas");
        setPersonas(response.data);
    };

    const handleSave = async () => {
        if (selectedPersona) {
            await axios.put(`/personas/${selectedPersona.id}`, formData);
        } else {
            await axios.post("/personas", formData);
        }
        fetchPersonas();
        setFormData({ name: "", background: "" });
        setSelectedPersona(null);
    };

    const handleDelete = async (id) => {
        await axios.delete(`/personas/${id}`);
        fetchPersonas();
    };

    return (
        <div className="persona-manager">
            <h3>Manage Personas</h3>
            <ul>
                {personas.map((persona) => (
                    <li key={persona.id}>
                        <span>{persona.name}</span>
                        <button onClick={() => setSelectedPersona(persona)}>Edit</button>
                        <button onClick={() => handleDelete(persona.id)}>Delete</button>
                    </li>
                ))}
            </ul>
            <div>
                <h4>{selectedPersona ? "Edit Persona" : "Add New Persona"}</h4>
                <input
                    type="text"
                    placeholder="Name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
                <textarea
                    placeholder="Background"
                    value={formData.background}
                    onChange={(e) =>
                        setFormData({ ...formData, background: e.target.value })
                    }
                />
                <button onClick={handleSave}>Save</button>
            </div>
        </div>
    );
};

export default PersonaManager;
