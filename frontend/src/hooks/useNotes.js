import { useState } from 'react';
import { noteService } from '../services/noteService';

export function useNotes(runWithBusy, openFile, getSelectedFile, getHighlightedLine) {
  const [username, setUsername] = useState('');
  const [fileQuestion, setFileQuestion] = useState('');

  const tagQuestionToFile = async () => {
    const selectedFile = getSelectedFile();
    if (!selectedFile || !username.trim() || !fileQuestion.trim()) return;
    await runWithBusy('Saving tagged question...', async () => {
      await noteService.saveQuestion({
        path: selectedFile,
        username: username.trim(),
        question: fileQuestion.trim()
      });
      setFileQuestion('');
      await openFile(selectedFile, getHighlightedLine());
    });
  };

  return {
    fileQuestion,
    setFileQuestion,
    setUsername,
    tagQuestionToFile,
    username
  };
}
