import { apiClient } from './apiClient';

export const repositoryService = {
  async getFiles() {
    const response = await apiClient.get('/files');
    return response.data;
  },
  async getSummary() {
    const response = await apiClient.get('/summary');
    return response.data;
  },
  async uploadZip(file) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/upload-zip', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return response.data;
  },
  async loadGit(url) {
    const response = await apiClient.post('/load-git', null, {
      params: { url }
    });
    return response.data;
  },
  async loadSample() {
    const response = await apiClient.post('/load-sample');
    return response.data;
  },
  async clear() {
    const response = await apiClient.post('/clear');
    return response.data;
  }
};
