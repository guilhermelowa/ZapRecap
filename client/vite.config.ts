import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { nodePolyfills } from 'vite-plugin-node-polyfills';

export default defineConfig({
  // base: '/static/',
  plugins: [
    react(),
    nodePolyfills({
      include: ['buffer', 'stream']
    })
  ],
  define: {
    __WS_TOKEN__: JSON.stringify(process.env.WS_TOKEN || 'development'),
    __API_BASE_URL__: JSON.stringify(
      process.env.VITE_NODE_ENV === 'production' 
        ? 'https://zap-recap-ffe516b006a4.herokuapp.com/' 
        : 'http://localhost:8000'
    ),
    global: {},
    process: { env: {} }
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
        manualChunks: {
          vendor: [
            'react',
            'react-dom',
            'react-router-dom',
            'i18next',
            'react-i18next'
          ]
        }
      }
    },
    chunkSizeWarningLimit: 1000
  },
  server: {
    hmr: {
      protocol: 'ws',
      host: 'localhost'
    }
  },
  ssr: {
    noExternal: ['react-plotly.js']
  }
});
