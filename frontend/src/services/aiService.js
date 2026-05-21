import { apiClient } from './apiClient';

export const aiService = {
  async ask(prompt, selectedFile, scope) {
    const response = await apiClient.post('/ask', {
      prompt,
      selected_file: selectedFile || null,
      scope
    });
    return response.data;
  },
  async listPromptTemplates() {
    const response = await apiClient.get('/prompt-templates');
    return response.data;
  },
  async runPromptTemplate(templateId) {
    const response = await apiClient.post('/prompt-templates/run', {
      template_id: templateId
    });
    return response.data;
  }
};
