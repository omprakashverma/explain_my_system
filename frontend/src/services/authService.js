import { apiClient } from './apiClient';

export const authService = {
  async register(payload) {
    const response = await apiClient.post('/auth/register', payload);
    return response.data;
  },
  async login(payload) {
    const response = await apiClient.post('/auth/login', payload);
    return response.data;
  },
  async logout() {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
  async getCurrentUser() {
    const response = await apiClient.get('/auth/me');
    return response.data;
  }
};
