import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';

export default defineConfig(({ command, mode }) => {
  console.log('Vite command:', command);
  console.log('Vite mode:', mode);

  const apiBaseUrl = mode === 'production'
    ? 'https://zap-recap-ffe516b006a4.herokuapp.com/'
    : 'http://localhost:8000';
  
  console.log('Selected API URL:', apiBaseUrl);

  return {
    base: '/static/',
    plugins: [
      react(),
      nodePolyfills({
        include: ['buffer', 'stream']
      })
    ],
    define: {
      __API_BASE_URL__: JSON.stringify(apiBaseUrl),
      global: {}
    },
    resolve: {
      extensions: ['.js', '.jsx', '.ts', '.tsx'],
      alias: {
        stream: 'stream-browserify',
        buffer: 'buffer'
      }
    },
    optimizeDeps: {
      exclude: ['react-plotly.js'],
      include: ['react-plotly.js/factory']
    },
    build: {
      commonjsOptions: {
        include: [/node_modules/],
        transformMixedEsModules: true
      },
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('node_modules')) {
              return 'vendor';
            }
          }
        }
      },
      chunkSizeWarningLimit: 1000,
      sourcemap: false
    },
    server: {
      hmr: {
        protocol: 'ws',
        host: 'localhost'
      },
      headers: {
        'Content-Security-Policy': 
          "connect-src 'self' " + 
          "http://localhost:8000 " + 
          "https://zap-recap-ffe516b006a4.herokuapp.com " + 
          "ws://localhost:5173"
      }
    },
    preview: {
      headers: {
        'Content-Security-Policy': 
          "connect-src 'self' " + 
          "http://localhost:8000 " + 
          "https://zap-recap-ffe516b006a4.herokuapp.com " + 
          "ws://localhost:5173"
      }
    },
    ssr: {
      noExternal: ['react-plotly.js']
    }
  };
});
