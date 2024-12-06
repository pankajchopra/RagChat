import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import ChatWindow from './components/ChatWindow';
import PersonaManager from './components/PersonaManager';
import Preferences from './components/Preferences';
import './App.css';

const App = () => {
  return (
      <Router>
        <div className="App">
          <header className="App-header">
            <h1>RAGgpt</h1>
          </header>
          <Routes>
            <Route path="/" element={<ChatWindow />} />
            <Route path="/personas" element={<PersonaManager />} />
            <Route path="/preferences" element={<Preferences />} />
          </Routes>
        </div>
      </Router>
  );
};

export default App;
