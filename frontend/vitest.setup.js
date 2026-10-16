import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';
import { TextEncoder, TextDecoder } from 'util';

Object.assign(globalThis, { TextEncoder, TextDecoder });

afterEach(() => {
    cleanup();
});
