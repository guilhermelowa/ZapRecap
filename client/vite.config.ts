import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import tsconfigPaths from 'vite-tsconfig-paths';
import { resolve } from 'path';

export default defineConfig({
  plugins: [react(), tsconfigPaths()],
  define: {
    __WS_TOKEN__: JSON.stringify(process.env.WS_TOKEN || 'development'),
    global: {}
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
