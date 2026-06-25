import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import App from './App';
import Health from './components/Health/Health';
import './style.css';

ReactDOM.createRoot(document.getElementById('app')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<App />} />
        <Route path="/health" element={<Health />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
