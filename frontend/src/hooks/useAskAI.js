import { useState } from 'react';
import { aiService } from '../services/aiService';
import { getErrorMessage } from '../utils/errorUtils';

export function useAskAI(setAppError) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [answerLoading, setAnswerLoading] = useState(false);

  const askQuestion = async (selectedFile) => {
    if (!question.trim()) return;
    setAnswerLoading(true);
    setAppError('');
    setAnswer('Thinking...');
    try {
      const response = await aiService.ask(question.trim(), selectedFile);
      setAnswer(response.answer);
    } catch (error) {
      setAnswer(`Error: ${getErrorMessage(error)}`);
    } finally {
      setAnswerLoading(false);
    }
  };

  return {
    answer,
    answerLoading,
    askQuestion,
    question,
    setAnswer,
    setQuestion
  };
}
