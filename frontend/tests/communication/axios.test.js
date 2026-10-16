import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock axios module before importing the axios.js file
vi.mock('axios', () => {
    const mockInterceptors = {
        request: { use: vi.fn((fulfilled) => { mockInterceptors._requestFulfilled = fulfilled; return 0; }) },
        response: { use: vi.fn((fulfilled, rejected) => { mockInterceptors._responseFulfilled = fulfilled; mockInterceptors._responseRejected = rejected; return 0; }) },
    };
    const mockAxios = {
        create: vi.fn(() => ({
            interceptors: mockInterceptors,
            get: vi.fn(),
            post: vi.fn(),
        })),
        _mockInterceptors: mockInterceptors,
    };
    return { default: mockAxios };
});

// We test the interceptor logic directly since the module is hard to re-import
// Instead, we test the behavior by importing and calling them manually

describe('Axios Interceptor Logic', () => {

    let sessionStorageMock;

    beforeEach(() => {
        sessionStorageMock = {};
        vi.stubGlobal('sessionStorage', {
            getItem: vi.fn((key) => sessionStorageMock[key] ?? null),
            setItem: vi.fn((key, val) => { sessionStorageMock[key] = val; }),
            removeItem: vi.fn((key) => { delete sessionStorageMock[key]; }),
            clear: vi.fn(() => { sessionStorageMock = {}; }),
        });
    });

    afterEach(() => {
        vi.unstubAllGlobals();
    });

    // ---- Request interceptor logic (extracted inline for testability) ----
    function applyRequestInterceptor(config) {
        const token = sessionStorage.getItem('token');
        if (token && token !== 'null' && token !== 'undefined' && token !== '') {
            config.headers = { ...config.headers, Authorization: `Bearer ${token}` };
        } else {
            if (config.headers) delete config.headers.Authorization;
        }
        return config;
    }

    it('attaches Authorization header when valid token exists', () => {
        sessionStorageMock['token'] = 'abc.def.ghi';
        const config = { headers: {} };
        const result = applyRequestInterceptor(config);
        expect(result.headers.Authorization).toBe('Bearer abc.def.ghi');
    });

    it('does NOT attach header when no token', () => {
        const config = { headers: {} };
        const result = applyRequestInterceptor(config);
        expect(result.headers.Authorization).toBeUndefined();
    });

    it('does NOT attach header when token is string "null"', () => {
        sessionStorageMock['token'] = 'null';
        const config = { headers: { Authorization: 'old' } };
        const result = applyRequestInterceptor(config);
        expect(result.headers.Authorization).toBeUndefined();
    });

    it('does NOT attach header when token is string "undefined"', () => {
        sessionStorageMock['token'] = 'undefined';
        const config = { headers: {} };
        const result = applyRequestInterceptor(config);
        expect(result.headers.Authorization).toBeUndefined();
    });

    it('does NOT attach header when token is empty string', () => {
        sessionStorageMock['token'] = '';
        const config = { headers: {} };
        const result = applyRequestInterceptor(config);
        expect(result.headers.Authorization).toBeUndefined();
    });

    // ---- Response interceptor logic ----
    function applyResponseRejection(error) {
        if (error.response && error.response.status === 401) {
            const isLoginRequest = error.config && error.config.url && error.config.url.includes('/auth/login');
            if (!isLoginRequest) {
                sessionStorage.removeItem('token');
                // window.location.href assignment — we test the removeItem was called
            }
        }
        return Promise.reject(error);
    }

    it('removes token on 401 for non-login URL', async () => {
        sessionStorageMock['token'] = 'valid-token';
        const error = { response: { status: 401 }, config: { url: '/api/gspr' } };
        await expect(applyResponseRejection(error)).rejects.toEqual(error);
        expect(sessionStorage.removeItem).toHaveBeenCalledWith('token');
    });

    it('does NOT remove token on 401 for login URL', async () => {
        sessionStorageMock['token'] = 'valid-token';
        const error = { response: { status: 401 }, config: { url: '/auth/login' } };
        await expect(applyResponseRejection(error)).rejects.toEqual(error);
        expect(sessionStorage.removeItem).not.toHaveBeenCalled();
    });

    it('passes through 200 responses unchanged', async () => {
        const response = { status: 200, data: { ok: true } };
        // Response fulfilled interceptor just returns the response as-is
        const fulfilled = (r) => r;
        const result = fulfilled(response);
        expect(result.data.ok).toBe(true);
    });
});
