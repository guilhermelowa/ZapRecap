import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: '/static/',
  plugins: [react()],
  define: {
    __WS_TOKEN__: JSON.stringify(process.env.WS_TOKEN || 'development'),
    global: {},
    process: { env: {} }
  },
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx'],
    alias: {
      stream: 'stream-browserify'
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
