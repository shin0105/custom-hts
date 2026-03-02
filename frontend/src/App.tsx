/**
 * Main App component with routing.
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Navigation } from './components/Navigation';
import { HomePage } from './pages/HomePage';
import { KoreanMarketPage } from './pages/KoreanMarketPage';
import { USMarketPage } from './pages/USMarketPage';
import { AccountCheckPage } from './pages/AccountCheckPage';
import { BondMarketPage } from './pages/BondMarketPage';
import { DomesticFuturesOptionsPage } from './pages/DomesticFuturesOptionsPage';

export const App: React.FC = () => {
  return (
    <Router>
      <div style={{ minHeight: '100vh', backgroundColor: '#f3f4f6' }}>
        <Navigation />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/korean" element={<KoreanMarketPage />} />
          <Route path="/bonds" element={<BondMarketPage />} />
          <Route path="/futures-options" element={<DomesticFuturesOptionsPage />} />
          <Route path="/us" element={<USMarketPage />} />
          <Route path="/account-check" element={<AccountCheckPage />} />
        </Routes>
      </div>
    </Router>
  );
};
