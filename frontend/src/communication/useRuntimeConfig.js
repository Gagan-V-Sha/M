import { useEffect, useState } from 'react';
import api from './axios';

const defaultConfig = {
    role: 'scanner',
    mineru_enabled: true,
    mineru_available: true,
    mineru_ready: true,
    mineru_version: null,
    database_backend: 'sqlite',
    database_shared: false,
    message: null,
};

/** Shared deploy config (Pi hides scan UI when mineru_ready is false). */
export const useRuntimeConfig = () => {
    const [config, setConfig] = useState(defaultConfig);
    const [loaded, setLoaded] = useState(false);

    useEffect(() => {
        let cancelled = false;
        Promise.resolve(api.get('/config'))
            .then((response) => {
                if (!cancelled && response?.data) {
                    setConfig({ ...defaultConfig, ...response.data });
                }
            })
            .catch(() => {
                /* keep defaults (scanner) if config is unreachable */
            })
            .finally(() => {
                if (!cancelled) setLoaded(true);
            });
        return () => {
            cancelled = true;
        };
    }, []);

    return { config, loaded, mineruReady: !!config.mineru_ready };
};
