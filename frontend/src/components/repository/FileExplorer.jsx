import React from 'react';
import { EmptyState } from '../common/EmptyState';

export function FileExplorer({ files, onOpenFile, selectedFile }) {
  return (
    <aside className="panel ems-sidebar">
      <div className="panel-heading compact">
        <div>
          <p className="section-kicker">Repository Files</p>
          <h2>Source explorer</h2>
        </div>
      </div>

      <div className="ems-files">
        {files.length === 0 ? (
          <EmptyState>No repository files loaded yet.</EmptyState>
        ) : (
          files.map((filePath) => (
            <button
              key={filePath}
              type="button"
              className={`ems-file ${filePath === selectedFile ? 'active' : ''}`}
              onClick={() => onOpenFile(filePath)}
            >
              {filePath}
            </button>
          ))
        )}
      </div>
    </aside>
  );
}
