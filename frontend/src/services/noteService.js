import { apiClient } from './apiClient';

export const noteService = {
  async listQuestions(path, scope, teamName) {
    const response = await apiClient.get('/questions', {
      params: {
        path: path || undefined,
        scope,
        team_name: teamName || undefined
      }
    });
    return response.data;
  },
  async saveQuestion(payload) {
    const response = await apiClient.post('/tag-question', payload);
    return response.data;
  },
  async getReplies(questionId) {
    const response = await apiClient.get(`/questions/${questionId}/replies`);
    return response.data;
  },
  async saveReply(questionId, payload) {
    const response = await apiClient.post(`/questions/${questionId}/reply`, payload);
    return response.data;
  },
  async setResolved(questionId, resolved) {
    const response = await apiClient.patch(`/questions/${questionId}/resolve`, { resolved });
    return response.data;
  }
};
