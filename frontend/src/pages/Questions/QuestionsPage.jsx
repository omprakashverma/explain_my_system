import React from 'react';
import { EmptyState } from '../../components/common/EmptyState';
import { useAppContext } from '../../context/AppContext';
import { noteService } from '../../services/noteService';
import { formatTimestamp } from '../../utils/formatters';

function questionMatchesSearch(question, searchTerm) {
  const haystack = [
    question.question,
    question.username,
    question.team_name,
    question.path,
    ...(question.replies || []).map((reply) => reply.content)
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  return haystack.includes(searchTerm.toLowerCase());
}

export function QuestionsPage() {
  const { auth, preview, repository } = useAppContext();
  const [questions, setQuestions] = React.useState([]);
  const [search, setSearch] = React.useState('');
  const [statusFilter, setStatusFilter] = React.useState('ALL');
  const [teamFilter, setTeamFilter] = React.useState('ALL');
  const [expandedIds, setExpandedIds] = React.useState({});
  const [replyDrafts, setReplyDrafts] = React.useState({});
  const [loading, setLoading] = React.useState(false);

  const loadQuestions = React.useCallback(async () => {
    setLoading(true);
    repository.setAppError('');
    try {
      const response = await noteService.listQuestions(null, 'ALL');
      setQuestions(response.questions || []);
    } catch (error) {
      repository.setAppError(error?.response?.data?.detail || error.message || 'Unable to load questions.');
    } finally {
      setLoading(false);
    }
  }, [repository]);

  React.useEffect(() => {
    loadQuestions();
  }, [loadQuestions, repository.summary?.loaded_at, repository.summary?.source_label]);

  const availableTeams = React.useMemo(() => (
    Array.from(new Set(
      questions
        .map((item) => item.team_name?.trim())
        .filter(Boolean)
    )).sort((left, right) => left.localeCompare(right))
  ), [questions]);

  React.useEffect(() => {
    if (teamFilter !== 'ALL' && !availableTeams.includes(teamFilter)) {
      setTeamFilter('ALL');
    }
  }, [availableTeams, teamFilter]);

  const filteredQuestions = React.useMemo(() => (
    questions.filter((item) => {
      if (statusFilter === 'OPEN' && item.resolved) {
        return false;
      }
      if (statusFilter === 'RESOLVED' && !item.resolved) {
        return false;
      }
      if (search.trim() && !questionMatchesSearch(item, search.trim())) {
        return false;
      }
      if (teamFilter !== 'ALL' && item.team_name !== teamFilter) {
        return false;
      }
      return true;
    })
  ), [questions, search, statusFilter, teamFilter]);

  const updateReplyDraft = (questionId, value) => {
    setReplyDrafts((current) => ({
      ...current,
      [questionId]: value
    }));
  };

  const submitReply = async (questionId) => {
    const draft = (replyDrafts[questionId] || '').trim();
    if (!draft) {
      return;
    }

    await repository.runWithBusy('Posting reply...', async () => {
      await noteService.saveReply(questionId, { content: draft });
      setReplyDrafts((current) => ({
        ...current,
        [questionId]: ''
      }));
      await loadQuestions();
    });
  };

  const toggleResolved = async (questionId, resolved) => {
    await repository.runWithBusy(resolved ? 'Re-opening question...' : 'Marking question resolved...', async () => {
      await noteService.setResolved(questionId, !resolved);
      await loadQuestions();
    });
  };

  const toggleExpanded = (questionId) => {
    setExpandedIds((current) => ({
      ...current,
      [questionId]: !current[questionId]
    }));
  };

  return (
    <div className="app-page">
      <section className="hero-card app-page-hero">
        <div>
          <p className="hero-kicker">Questions</p>
          <h1>Open engineering discussions across the repository</h1>
          <p className="hero-copy">
            Browse active collaborative questions, reply inline, and follow the conversations that shape how the team understands the codebase.
          </p>
        </div>

        <div className="stat-grid">
          <div className="stat-card">
            <span>Total Questions</span>
            <strong>{questions.length}</strong>
            <small>Across file and repository scope</small>
          </div>
          <div className="stat-card">
            <span>Open Threads</span>
            <strong>{questions.filter((item) => !item.resolved).length}</strong>
            <small>Needs team attention</small>
          </div>
          <div className="stat-card">
            <span>Resolved</span>
            <strong>{questions.filter((item) => item.resolved).length}</strong>
            <small>Knowledge captured</small>
          </div>
          <div className="stat-card">
            <span>Repository</span>
            <strong className="value-wrap">{repository.summary?.source_label || 'No repo loaded'}</strong>
            <small>{loading ? 'Refreshing discussions...' : 'Current workspace context'}</small>
          </div>
        </div>
      </section>

      <section className="panel questions-toolbar-panel">
        <div className="questions-toolbar">
          <input
            className="text-input"
            placeholder="Search questions, authors, files, or replies"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />

          <select
            className="template-select"
            value={teamFilter}
            onChange={(event) => setTeamFilter(event.target.value)}
          >
            <option value="ALL">All teams</option>
            {availableTeams.map((teamName) => (
              <option key={teamName} value={teamName}>
                {teamName}
              </option>
            ))}
          </select>

          <div className="scope-toggle">
            <button
              className={`scope-chip ${statusFilter === 'ALL' ? 'active' : ''}`}
              type="button"
              onClick={() => setStatusFilter('ALL')}
            >
              All
            </button>
            <button
              className={`scope-chip ${statusFilter === 'OPEN' ? 'active' : ''}`}
              type="button"
              onClick={() => setStatusFilter('OPEN')}
            >
              Open
            </button>
            <button
              className={`scope-chip ${statusFilter === 'RESOLVED' ? 'active' : ''}`}
              type="button"
              onClick={() => setStatusFilter('RESOLVED')}
            >
              Resolved
            </button>
          </div>
        </div>
      </section>

      <section className="questions-grid">
        {filteredQuestions.length === 0 ? (
          <EmptyState>
            {loading ? 'Loading collaborative questions...' : 'No questions match the current filters yet.'}
          </EmptyState>
        ) : (
          filteredQuestions.map((item) => {
            const isExpanded = Boolean(expandedIds[item.id]);
            const canResolve = auth.user?.role === 'admin' || auth.user?.id === item.user_id;

            return (
              <article key={item.id} className={`question-row-card ${item.resolved ? 'resolved' : 'open'}`}>
                <div className="question-row-main">
                  <div className="question-row-copy">
                    <div className="chip-row">
                      <span className={`status-pill ${item.resolved ? 'valid' : 'inactive'}`}>
                        {item.resolved ? 'Resolved' : 'Open'}
                      </span>
                      <span className="chip subtle">{item.scope}</span>
                      {item.team_name ? <span className="chip subtle">Team: {item.team_name}</span> : null}
                      <span className="chip subtle">{item.reply_count} replies</span>
                    </div>

                    <h3>{item.question}</h3>
                    <p className="question-row-meta">
                      Asked by <strong>{item.username}</strong> on {formatTimestamp(item.created_at)}
                    </p>

                    {item.path ? (
                      <button
                        className="question-path-link"
                        type="button"
                        onClick={() => preview.openFile(item.path)}
                      >
                        {item.path}
                      </button>
                    ) : (
                      <p className="muted">Repository-wide discussion</p>
                    )}
                  </div>

                  <div className="question-row-actions">
                    <button className="btn secondary" type="button" onClick={() => toggleExpanded(item.id)}>
                      {isExpanded ? 'Hide Replies' : 'View Replies'}
                    </button>
                    {canResolve ? (
                      <button
                        className="btn ghost"
                        type="button"
                        onClick={() => toggleResolved(item.id, item.resolved)}
                      >
                        {item.resolved ? 'Re-open' : 'Resolve'}
                      </button>
                    ) : null}
                  </div>
                </div>

                {isExpanded ? (
                  <div className="question-row-details">
                    <div className="reply-list">
                      {item.replies?.length ? item.replies.map((reply) => (
                        <div key={reply.id} className="reply-card">
                          <div className="reply-meta">
                            <strong>{reply.username}</strong>
                            <small>{formatTimestamp(reply.created_at)}</small>
                          </div>
                          <p>{reply.content}</p>
                        </div>
                      )) : <p className="muted">No replies yet.</p>}
                    </div>

                    <div className="reply-composer">
                      <textarea
                        className="text-area compact"
                        placeholder="Reply to this discussion"
                        value={replyDrafts[item.id] || ''}
                        onChange={(event) => updateReplyDraft(item.id, event.target.value)}
                      />
                      <div className="button-row">
                        <button
                          className="btn"
                          type="button"
                          disabled={repository.isBusy || !(replyDrafts[item.id] || '').trim()}
                          onClick={() => submitReply(item.id)}
                        >
                          Post Reply
                        </button>
                        <span className="muted">
                          {item.latest_reply_at ? `Latest reply ${formatTimestamp(item.latest_reply_at)}` : 'Be the first to reply'}
                        </span>
                      </div>
                    </div>
                  </div>
                ) : null}
              </article>
            );
          })
        )}
      </section>
    </div>
  );
}
