import axios from 'axios';

console.log('Build mode:', import.meta.env.MODE);
console.log('Build prod:', import.meta.env.PROD);
console.log('Build dev:', import.meta.env.DEV);

const baseURL = __API_BASE_URL__;
console.log('Selected baseURL:', baseURL);

const apiClient = axios.create({
  baseURL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add error logging
apiClient.interceptors.request.use(
  config => {
    console.log('Request URL:', config.url);
    return config;
  },
  error => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

export default apiClient; 