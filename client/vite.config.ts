import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ['react-plotly.js'],
  },
  build: {
    commonjsOptions: {
      include: [/react-plotly\.js/, /node_modules/],
    },
  },
});
