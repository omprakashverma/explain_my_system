import { apiClient } from './apiClient';

export const fileService = {
  async getFile(path) {
    const response = await apiClient.get('/file', {
      params: { path }
    });
    return response.data;
  }
};
