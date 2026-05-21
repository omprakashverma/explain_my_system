import { useEffect, useState } from 'react';
import { noteService } from '../services/noteService';
import { getErrorMessage } from '../utils/errorUtils';

export function useNotes(
  runWithBusy,
  openFile,
  selectedFile,
  getHighlightedLine,
  getUsername,
  setAppError,
  setTaggedQuestions,
  repositoryKey
) {
  const [fileQuestion, setFileQuestion] = useState('');
  const [questionScope, setQuestionScope] = useState('FILE');
  const [discussionFilter, setDiscussionFilter] = useState('ALL');
  const [replyDrafts, setReplyDrafts] = useState({});

  const refreshQuestions = async (scope = discussionFilter) => {
    if (!repositoryKey) {
      setTaggedQuestions([]);
      return;
    }
    try {
      const response = await noteService.listQuestions(
        scope === 'FILE' ? selectedFile : selectedFile || null,
        scope
      );
      setTaggedQuestions(response.questions || []);
    } catch (error) {
      setAppError(getErrorMessage(error));
    }
  };

  useEffect(() => {
    refreshQuestions();
  }, [discussionFilter, repositoryKey, selectedFile]);

  useEffect(() => {
    if (!selectedFile && questionScope === 'FILE') {
      setQuestionScope('REPOSITORY');
    }
    if (!selectedFile && discussionFilter === 'FILE') {
      setDiscussionFilter('REPOSITORY');
    }
  }, [discussionFilter, questionScope, selectedFile]);

  const tagQuestionToFile = async () => {
    const username = getUsername();
    if (!username.trim() || !fileQuestion.trim()) return;
    if (questionScope === 'FILE' && !selectedFile) return;
    await runWithBusy('Saving tagged question...', async () => {
      await noteService.saveQuestion({
        path: questionScope === 'FILE' ? selectedFile : null,
        question: fileQuestion.trim(),
        scope: questionScope
      });
      setFileQuestion('');
      if (selectedFile) {
        await openFile(selectedFile, getHighlightedLine());
      }
      await refreshQuestions();
    });
  };

  const updateReplyDraft = (questionId, value) => {
    setReplyDrafts((current) => ({
      ...current,
      [questionId]: value
    }));
  };

  const submitReply = async (questionId) => {
    const draft = replyDrafts[questionId] || '';
    if (!draft.trim()) return;
    await runWithBusy('Posting reply...', async () => {
      await noteService.saveReply(questionId, { content: draft.trim() });
      setReplyDrafts((current) => ({
        ...current,
        [questionId]: ''
      }));
      if (selectedFile) {
        await openFile(selectedFile, getHighlightedLine());
      }
      await refreshQuestions();
    });
  };

  const toggleResolved = async (questionId, resolved) => {
    await runWithBusy(resolved ? 'Re-opening question...' : 'Marking question resolved...', async () => {
      await noteService.setResolved(questionId, !resolved);
      if (selectedFile) {
        await openFile(selectedFile, getHighlightedLine());
      }
      await refreshQuestions();
    });
  };

  return {
    discussionFilter,
    fileQuestion,
    questionScope,
    refreshQuestions,
    replyDrafts,
    setDiscussionFilter,
    setFileQuestion,
    setQuestionScope,
    submitReply,
    tagQuestionToFile,
    toggleResolved,
    updateReplyDraft
  };
}
