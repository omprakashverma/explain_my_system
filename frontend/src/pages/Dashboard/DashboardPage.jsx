import React from 'react';
import { LoadingOverlay } from '../../components/common/LoadingOverlay';
import { Header } from '../../components/layout/Header';
import { NotesPanel } from '../../components/notes/NotesPanel';
import { FilePreview } from '../../components/preview/FilePreview';
import { AskPanel } from '../../components/qa/AskPanel';
import { FileExplorer } from '../../components/repository/FileExplorer';
import { RepositoryLoader } from '../../components/repository/RepositoryLoader';
import { StatusBanner } from '../../components/status/StatusBanner';
import { useAppContext } from '../../context/AppContext';

export function DashboardPage() {
  const { ai, notes, preview, repository } = useAppContext();

  return (
    <div className="ems-root">
      <LoadingOverlay message={repository.busyMessage} />
      <Header summary={repository.summary} busyMessage={repository.busyMessage} />

      <section className="control-grid">
        <RepositoryLoader
          busyMessage={repository.busyMessage}
          fileInputRef={repository.fileInputRef}
          gitUrl={repository.gitUrl}
          isBusy={repository.isBusy}
          onClearAll={() =>
            repository.clearAll(preview.resetPreviewState, () => {
              ai.setAnswer(null);
              preview.setTaggedQuestions([]);
              preview.setHighlightedLine(null);
            })
          }
          onGitUrlChange={repository.setGitUrl}
          onLoadGit={() =>
            repository.loadGit(
              repository.gitUrl,
              preview.resetPreviewState,
              preview.selectedFile,
              preview.clearSelectionIfMissing
            )
          }
          onLoadSampleRepo={() =>
            repository.loadSampleRepo(
              preview.resetPreviewState,
              preview.selectedFile,
              preview.clearSelectionIfMissing
            )
          }
          onUploadZip={(file) =>
            repository.uploadZip(
              file,
              preview.resetPreviewState,
              preview.selectedFile,
              preview.clearSelectionIfMissing
            )
          }
        />

        <article className="panel">
          <div className="panel-heading">
            <div>
              <p className="section-kicker">What the system is</p>
              <h2>Auto-generated project summary</h2>
            </div>
          </div>

          <div className="preview-surface">
            <div className="preview-caption">
              {repository.summary?.overview ||
                'Load a repository to see a compact system overview, discovered modules, and other helpful metadata.'}
            </div>

            <div className="chip-row">
              {repository.summary?.top_modules?.length > 0 ? (
                repository.summary.top_modules.map((moduleName) => (
                  <span key={moduleName} className="chip">
                    {moduleName}
                  </span>
                ))
              ) : (
                <span className="muted">No modules detected yet.</span>
              )}
            </div>
          </div>
        </article>
      </section>

      <StatusBanner error={repository.appError} />

      <div className="ems-body">
        <FileExplorer
          files={repository.files}
          onOpenFile={preview.openFile}
          selectedFile={preview.selectedFile}
        />

        <FilePreview
          highlightedLine={preview.highlightedLine}
          highlightedLineRef={preview.highlightedLineRef}
          selectedFile={preview.selectedFile}
          selectedFileLineCount={preview.selectedFileLineCount}
          selectedFileLines={preview.selectedFileLines}
          selectedFileLoaded={preview.selectedFileLoaded}
        />

        <main className="ems-main">
          <AskPanel
            answer={ai.answer}
            answerLoading={ai.answerLoading}
            onAsk={() => ai.askQuestion(preview.selectedFile)}
            onQuestionChange={ai.setQuestion}
            question={ai.question}
          />

          <NotesPanel
            fileQuestion={notes.fileQuestion}
            isBusy={repository.isBusy}
            onFileQuestionChange={notes.setFileQuestion}
            onSaveQuestion={notes.tagQuestionToFile}
            onUsernameChange={notes.setUsername}
            selectedFile={preview.selectedFile}
            taggedQuestions={preview.taggedQuestions}
            username={notes.username}
          />
        </main>
      </div>
    </div>
  );
}
