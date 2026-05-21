import axios from 'axios';
import { API_BASE } from '../utils/constants';
import { authStorage } from './authStorage';

export const apiClient = axios.create({
  baseURL: API_BASE
});

apiClient.interceptors.request.use((config) => {
  const token = authStorage.getToken();
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
