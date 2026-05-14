import { useRef, useState } from 'react';
import { repositoryService } from '../services/repositoryService';
import { getErrorMessage } from '../utils/errorUtils';

export function useRepository() {
  const fileInputRef = useRef(null);
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [busyMessage, setBusyMessage] = useState('');
  const [appError, setAppError] = useState('');
  const [gitUrl, setGitUrl] = useState('');

  const runWithBusy = async (message, task) => {
    setBusyMessage(message);
    setAppError('');
    try {
      return await task();
    } catch (error) {
      setAppError(getErrorMessage(error));
      return null;
    } finally {
      setBusyMessage('');
    }
  };

  const refresh = async (selectedFile, onInvalidSelection) => {
    try {
      const [filesResponse, summaryResponse] = await Promise.all([
        repositoryService.getFiles(),
        repositoryService.getSummary()
      ]);
      const filesList = filesResponse.files || [];
      setFiles(filesList);
      setSummary(summaryResponse || null);
      if (selectedFile && !filesList.includes(selectedFile)) {
        onInvalidSelection?.();
      }
      return filesList;
    } catch (error) {
      setAppError(getErrorMessage(error));
      return [];
    }
  };

  const uploadZip = async (file, onReset, selectedFile, onInvalidSelection) => {
    if (!file) return;
    await runWithBusy('Uploading repository ZIP...', async () => {
      await repositoryService.uploadZip(file);
      onReset?.();
      await refresh(selectedFile, onInvalidSelection);
    });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const loadGit = async (url, onReset, selectedFile, onInvalidSelection) => {
    if (!url.trim()) return;
    await runWithBusy('Cloning repository from Git...', async () => {
      await repositoryService.loadGit(url.trim());
      onReset?.();
      await refresh(selectedFile, onInvalidSelection);
    });
  };

  const loadSampleRepo = async (onReset, selectedFile, onInvalidSelection) => {
    await runWithBusy('Loading bundled sample repository...', async () => {
      await repositoryService.loadSample();
      onReset?.();
      await refresh(selectedFile, onInvalidSelection);
    });
  };

  const clearAll = async (onReset, onClearExtras) => {
    await runWithBusy('Clearing repository state...', async () => {
      await repositoryService.clear();
      setFiles([]);
      setSummary(null);
      onClearExtras?.();
      onReset?.();
      await refresh(null, null);
    });
  };

  return {
    appError,
    busyMessage,
    runWithBusy,
    fileInputRef,
    files,
    gitUrl,
    isBusy: Boolean(busyMessage),
    refresh,
    setAppError,
    setGitUrl,
    setSummary,
    summary,
    uploadZip,
    loadGit,
    loadSampleRepo,
    clearAll
  };
}
