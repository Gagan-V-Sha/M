import axios from 'axios';

const api = axios.create({
    baseURL: '/api', // Proxy handles this
    withCredentials: true, // Fix 8.1: Ensure cookies are sent with cross-origin/same-origin requests
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use(
    (config) => config,
    (error) => Promise.reject(error)
);

// Add response interceptor to handle 401s globally
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response && error.response.status === 401) {
            // Do not redirect on 401 if the request was to the login endpoint
            const isLoginRequest = error.config && error.config.url && error.config.url.includes('/auth/login');
            if (!isLoginRequest) {
                // Token invalid or expired - force logout
                console.warn("Session expired or invalid. Redirecting to login.");
                // Fix 8.1: Use localStorage flag instead of sessionStorage token
                localStorage.removeItem('is_authenticated');
                // Use window.location to force full reload/redirect outside React Router context if needed
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default api;
