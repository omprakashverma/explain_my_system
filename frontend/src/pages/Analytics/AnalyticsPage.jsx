import React from 'react';
import { EmptyState } from '../../components/common/EmptyState';
import { useAppContext } from '../../context/AppContext';
import { noteService } from '../../services/noteService';

function minutesBetween(start, end) {
  if (!start || !end) {
    return null;
  }

  const startTime = new Date(start).getTime();
  const endTime = new Date(end).getTime();
  if (Number.isNaN(startTime) || Number.isNaN(endTime) || endTime < startTime) {
    return null;
  }

  return Math.round((endTime - startTime) / 60000);
}

export function AnalyticsPage() {
  const { repository } = useAppContext();
  const [questions, setQuestions] = React.useState([]);
  const [loading, setLoading] = React.useState(false);

  const loadQuestions = React.useCallback(async () => {
    setLoading(true);
    repository.setAppError('');
    try {
      const response = await noteService.listQuestions(null, 'ALL');
      setQuestions(response.questions || []);
    } catch (error) {
      repository.setAppError(error?.response?.data?.detail || error.message || 'Unable to load dashboard metrics.');
    } finally {
      setLoading(false);
    }
  }, [repository]);

  React.useEffect(() => {
    loadQuestions();
  }, [loadQuestions, repository.summary?.loaded_at, repository.summary?.source_label]);

  const metrics = React.useMemo(() => {
    const totalQuestions = questions.length;
    const openQuestions = questions.filter((item) => !item.resolved).length;
    const resolvedQuestions = totalQuestions - openQuestions;
    const totalReplies = questions.reduce((count, item) => count + (item.reply_count || 0), 0);

    const contributorCounts = new Map();
    const pathCounts = new Map();
    const responseMinutes = [];

    questions.forEach((item) => {
      contributorCounts.set(item.username, (contributorCounts.get(item.username) || 0) + 1);
      const repositoryLabel = item.path || 'Repository-wide';
      pathCounts.set(repositoryLabel, (pathCounts.get(repositoryLabel) || 0) + 1);
      if (item.replies?.length) {
        const responseTime = minutesBetween(item.created_at, item.replies[0].created_at);
        if (responseTime !== null) {
          responseMinutes.push(responseTime);
        }
      }
    });

    const topContributors = [...contributorCounts.entries()]
      .sort((left, right) => right[1] - left[1])
      .slice(0, 4);

    const topPaths = [...pathCounts.entries()]
      .sort((left, right) => right[1] - left[1])
      .slice(0, 5);

    const averageResponseTime = responseMinutes.length
      ? Math.round(responseMinutes.reduce((sum, value) => sum + value, 0) / responseMinutes.length)
      : null;

    return {
      averageResponseTime,
      openQuestions,
      resolvedQuestions,
      topContributors,
      topPaths,
      totalQuestions,
      totalReplies
    };
  }, [questions]);

  const maxPathCount = metrics.topPaths[0]?.[1] || 1;

  return (
    <div className="app-page">
      <section className="hero-card app-page-hero">
        <div>
          <p className="hero-kicker">Dashboard</p>
          <h1>Collaboration health for the current codebase</h1>
          <p className="hero-copy">
            Track discussion volume, open questions, response speed, and the parts of the repository drawing the most engineering attention.
          </p>
        </div>

        <div className="dashboard-card-grid">
          <article className="analytics-card">
            <span>Total Questions</span>
            <strong>{metrics.totalQuestions}</strong>
            <small>Knowledge threads captured</small>
          </article>
          <article className="analytics-card">
            <span>Open vs Resolved</span>
            <strong>{metrics.openQuestions} / {metrics.resolvedQuestions}</strong>
            <small>Open and resolved discussion count</small>
          </article>
          <article className="analytics-card">
            <span>Average First Reply</span>
            <strong>{metrics.averageResponseTime !== null ? `${metrics.averageResponseTime} min` : 'No data'}</strong>
            <small>Measured from question creation to first reply</small>
          </article>
          <article className="analytics-card">
            <span>Total Replies</span>
            <strong>{metrics.totalReplies}</strong>
            <small>Follow-up collaboration activity</small>
          </article>
        </div>
      </section>

      {questions.length === 0 && !loading ? (
        <EmptyState>
          No collaborative metrics yet. Start tagging questions or replying to discussions to populate the dashboard.
        </EmptyState>
      ) : (
        <div className="analytics-layout">
          <section className="panel">
            <div className="panel-heading compact">
              <div>
                <p className="section-kicker">Top Contributors</p>
                <h3>Who is driving repository knowledge</h3>
              </div>
            </div>

            <div className="analytics-list">
              {metrics.topContributors.length ? metrics.topContributors.map(([username, count]) => (
                <div key={username} className="analytics-list-row">
                  <div>
                    <strong>{username}</strong>
                    <p className="muted">Questions created</p>
                  </div>
                  <span className="analytics-value-pill">{count}</span>
                </div>
              )) : <p className="muted">No contributor data yet.</p>}
            </div>
          </section>

          <section className="panel">
            <div className="panel-heading compact">
              <div>
                <p className="section-kicker">Hotspots</p>
                <h3>Most discussed files and scopes</h3>
              </div>
            </div>

            <div className="analytics-bars">
              {metrics.topPaths.length ? metrics.topPaths.map(([label, count]) => (
                <div key={label} className="analytics-bar-row">
                  <div className="analytics-bar-copy">
                    <strong>{label}</strong>
                    <small>{count} discussions</small>
                  </div>
                  <div className="analytics-bar-track">
                    <span
                      className="analytics-bar-fill"
                      style={{ width: `${Math.max(16, (count / maxPathCount) * 100)}%` }}
                    />
                  </div>
                </div>
              )) : <p className="muted">No file-level activity yet.</p>}
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
