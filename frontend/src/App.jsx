import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './auth/LoginPage';
import SignupPage from './auth/SignupPage';
import ForgotPasswordPage from './auth/ForgotPasswordPage';
import ResetPasswordPage from './auth/ResetPasswordPage';
import SettingsPage from './settings/SettingsPage';
import Navbar from './layout/Navbar';
import MainLayout from './layout/MainLayout';
import './App.css';

import Dashboard from './dashboard/Dashboard';
import EtdEditor from './documents/EtdEditor';

const PrivateRoute = ({ children }) => {
    // Fix 8.1: Check UI flag instead of token (actual auth is handled via HttpOnly cookie in requests)
    const isAuthenticated = localStorage.getItem('is_authenticated') === 'true';
    return isAuthenticated ? children : <Navigate to="/login" />;
};

import DatabaseViewer from './database/DatabaseViewer';
import ScanReview from './scan/ScanReview';
import { useAppPresenter } from './useAppPresenter';

function App() {
    useAppPresenter();

    return (
        <Router>
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />
                <Route
                    path="/dashboard"
                    element={
                        <PrivateRoute>
                            <MainLayout>
                                <Dashboard />
                            </MainLayout>
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/devices/:id/etd"
                    element={
                        <PrivateRoute>
                            <MainLayout>
                                <EtdEditor />
                            </MainLayout>
                        </PrivateRoute>
                    }
                />

                <Route
                    path="/database-viewer"
                    element={
                        <PrivateRoute>
                            <MainLayout>
                                <DatabaseViewer />
                            </MainLayout>
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/scan-review"
                    element={
                        <PrivateRoute>
                            <MainLayout>
                                <ScanReview />
                            </MainLayout>
                        </PrivateRoute>
                    }
                />
                <Route
                    path="/settings"
                    element={
                        <PrivateRoute>
                            <MainLayout>
                                <SettingsPage />
                            </MainLayout>
                        </PrivateRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/dashboard" />} />
            </Routes>
        </Router>
    );
}

export default App;
