import axios from 'axios';

const apiClient = axios.create({
  baseURL: __API_BASE_URL__,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient; 