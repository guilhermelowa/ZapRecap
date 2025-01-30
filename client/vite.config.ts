import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx']
  },
  define: {
    __WS_TOKEN__: JSON.stringify(process.env.WS_TOKEN || 'development')
  },
  optimizeDeps: {
    include: ['react-plotly.js'],
  },
  build: {
    commonjsOptions: {
      include: [/react-plotly\.js/, /node_modules/],
    },
  },
  server: {
    hmr: {
      protocol: 'ws',
      host: 'localhost'
    }
  }
});
