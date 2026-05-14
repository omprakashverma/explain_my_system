import { apiClient } from './apiClient';

export const noteService = {
  async saveQuestion(payload) {
    const response = await apiClient.post('/tag-question', payload);
    return response.data;
  }
};
