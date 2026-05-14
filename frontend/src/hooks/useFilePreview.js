import { useEffect, useRef, useState } from 'react';
import { fileService } from '../services/fileService';
import { getErrorMessage } from '../utils/errorUtils';

export function useFilePreview(setAppError) {
  const highlightedLineRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContents, setFileContents] = useState({});
  const [taggedQuestions, setTaggedQuestions] = useState([]);
  const [highlightedLine, setHighlightedLine] = useState(null);

  const selectedFileLoaded = selectedFile
    ? Object.prototype.hasOwnProperty.call(fileContents, selectedFile)
    : false;

  const selectedFileText =
    selectedFile && selectedFileLoaded ? fileContents[selectedFile] || '' : '';
  const selectedFileLines = selectedFileLoaded ? selectedFileText.split('\n') : [];
  const selectedFileLineCount = selectedFileLoaded ? selectedFileLines.length : 0;

  useEffect(() => {
    if (!selectedFile || !highlightedLine || !highlightedLineRef.current) {
      return;
    }
    highlightedLineRef.current.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    });
  }, [highlightedLine, selectedFile, selectedFileText]);

  const resetPreviewState = () => {
    setSelectedFile(null);
    setHighlightedLine(null);
    setFileContents({});
    setTaggedQuestions([]);
  };

  const openFile = async (path, targetLine = null) => {
    setSelectedFile(path);
    setHighlightedLine(targetLine);
    setAppError('');
    try {
      const response = await fileService.getFile(path);
      setFileContents((current) => ({
        ...current,
        [path]: response.text
      }));
      setTaggedQuestions(response.questions || []);
    } catch (error) {
      setAppError(getErrorMessage(error));
    }
  };

  const jumpToSource = async (path, line) => {
    if (!path) return;
    await openFile(path, line || null);
  };

  const clearSelectionIfMissing = () => {
    setSelectedFile(null);
    setHighlightedLine(null);
    setTaggedQuestions([]);
  };

  return {
    clearSelectionIfMissing,
    fileContents,
    highlightedLine,
    highlightedLineRef,
    jumpToSource,
    openFile,
    resetPreviewState,
    selectedFile,
    selectedFileLineCount,
    selectedFileLines,
    selectedFileLoaded,
    selectedFileText,
    setHighlightedLine,
    taggedQuestions,
    setTaggedQuestions
  };
}
