import React, { createContext, useContext, useEffect, useMemo } from 'react';
import { useAskAI } from '../hooks/useAskAI';
import { useFilePreview } from '../hooks/useFilePreview';
import { useNotes } from '../hooks/useNotes';
import { useRepository } from '../hooks/useRepository';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const repository = useRepository();
  const preview = useFilePreview(repository.setAppError);
  const ai = useAskAI(repository.setAppError);
  const notes = useNotes(
    async (message, task) => repository.runWithBusy(message, task),
    preview.openFile,
    () => preview.selectedFile,
    () => preview.highlightedLine
  );

  useEffect(() => {
    repository.refresh(preview.selectedFile, preview.clearSelectionIfMissing);
  }, []);

  const value = useMemo(
    () => ({
      repository,
      preview,
      ai,
      notes
    }),
    [ai, notes, preview, repository]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within AppProvider');
  }
  return context;
}
