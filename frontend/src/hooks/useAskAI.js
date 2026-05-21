import { useEffect, useState } from 'react';
import { aiService } from '../services/aiService';
import { getErrorMessage } from '../utils/errorUtils';

export function useAskAI(setAppError, selectedFile) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [answerLoading, setAnswerLoading] = useState(false);
  const [askScope, setAskScope] = useState(selectedFile ? 'FILE' : 'REPOSITORY');
  const [templates, setTemplates] = useState([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState('');

  useEffect(() => {
    if (!selectedFile && askScope === 'FILE') {
      setAskScope('REPOSITORY');
    }
  }, [askScope, selectedFile]);

  useEffect(() => {
    let active = true;

    const loadTemplates = async () => {
      try {
        const response = await aiService.listPromptTemplates();
        if (active) {
          setTemplates(response.templates || []);
        }
      } catch (error) {
        if (active) {
          setAppError(getErrorMessage(error));
        }
      }
    };

    loadTemplates();
    return () => {
      active = false;
    };
  }, [setAppError]);

  const applyTemplate = (templateId) => {
    setSelectedTemplateId(templateId);
    const template = templates.find((item) => item.id === templateId);
    if (!template) {
      return;
    }
    setAskScope(template.scope || 'REPOSITORY');
    setQuestion(template.prompt_template);
  };

  const askQuestion = async () => {
    if (!question.trim()) return;
    setAnswerLoading(true);
    setAppError('');
    setAnswer('Thinking...');
    try {
      const response = await aiService.ask(question.trim(), selectedFile, askScope);
      setAnswer(response);
    } catch (error) {
      setAnswer(`Error: ${getErrorMessage(error)}`);
    } finally {
      setAnswerLoading(false);
    }
  };

  const runTemplate = async (templateId) => {
    setSelectedTemplateId(templateId);
    setAnswerLoading(true);
    setAppError('');
    setAnswer('Running template...');
    try {
      const response = await aiService.runPromptTemplate(templateId);
      setAskScope(response.scope || 'REPOSITORY');
      setQuestion(response.template.prompt_template);
      setAnswer(response);
    } catch (error) {
      setAnswer(`Error: ${getErrorMessage(error)}`);
    } finally {
      setAnswerLoading(false);
    }
  };

  return {
    answer,
    answerLoading,
    applyTemplate,
    askQuestion,
    askScope,
    question,
    runTemplate,
    selectedTemplateId,
    setAnswer,
    setAskScope,
    setQuestion,
    templates
  };
}
