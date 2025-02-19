import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_NODE_ENV === 'production' 
    ? 'https://zap-recap-ffe516b006a4.herokuapp.com/' 
    : 'http://localhost:8000',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient; 