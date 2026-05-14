import { apiClient } from './apiClient';

export const aiService = {
  async ask(prompt, selectedFile) {
    const response = await apiClient.post('/ask', {
      prompt,
      selected_file: selectedFile || null
    });
    return response.data;
  }
};
