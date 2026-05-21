import React, { useEffect, useId, useMemo, useRef, useState } from 'react';
import mermaid from 'mermaid';

const MERMAID_START_RE =
  /^(graph|flowchart|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie|mindmap|timeline|gitGraph|architecture)\b/i;

function isFlowchartDiagram(chart) {
  const firstLine = chart
    .split('\n')
    .map((line) => line.trim())
    .find(Boolean);

  return Boolean(firstLine && /^(graph|flowchart)\b/i.test(firstLine));
}

function isMermaidStartLine(line) {
  return MERMAID_START_RE.test(line.trim());
}

function isLikelyMermaidContentLine(line) {
  const trimmed = line.trim();
  if (!trimmed) {
    return true;
  }

  if (
    isMermaidStartLine(trimmed) ||
    /^(subgraph|end|direction|classDef|class|style|click|linkStyle|accTitle|accDescr|section)\b/i.test(trimmed) ||
    trimmed.startsWith('%%')
  ) {
    return true;
  }

  if (
    /(-->|<--|<-->|==>|-.->|---|:::|[()[\]{}]|\|.*\||:)/.test(trimmed) ||
    /^[A-Za-z0-9_."'-]+\s*(-->|<--|<-->|==>|-.->|---)/.test(trimmed)
  ) {
    return true;
  }

  return false;
}

function parseBareMermaid(answer) {
  const lines = answer.split('\n');
  const startIndex = lines.findIndex((line) => isMermaidStartLine(line));

  if (startIndex === -1) {
    return null;
  }

  const diagramLines = [];
  let endIndex = startIndex;

  for (let index = startIndex; index < lines.length; index += 1) {
    const line = lines[index];
    const trimmed = line.trim();

    if (!trimmed) {
      if (diagramLines.length > 0) {
        endIndex = index;
        break;
      }
      continue;
    }

    if (diagramLines.length > 0 && !isLikelyMermaidContentLine(line)) {
      endIndex = index;
      break;
    }

    diagramLines.push(line);
    endIndex = index + 1;
  }

  if (diagramLines.length === 0) {
    return null;
  }

  const before = lines.slice(0, startIndex).join('\n').trim();
  const after = lines.slice(endIndex).join('\n').trim();
  const explanation = [before, after].filter(Boolean).join('\n\n');

  return {
    type: 'mermaid',
    diagram: diagramLines.join('\n').trim(),
    explanation
  };
}

function createMermaidNodeId(label) {
  const normalized = label
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_+|_+$/g, '');

  return normalized || 'node';
}

function normalizeNodeRef(ref, nodeRegistry) {
  const trimmed = ref.trim();
  if (!trimmed) {
    return trimmed;
  }

  if (
    /^(subgraph|end|direction|classDef|class|style|click|linkStyle)\b/.test(trimmed) ||
    trimmed.includes('["') ||
    trimmed.includes("['") ||
    /[\[\]{}()]/.test(trimmed) ||
    trimmed.includes(':::') ||
    trimmed.includes('@{')
  ) {
    return trimmed;
  }

  if (/^[A-Za-z_][A-Za-z0-9_]*$/.test(trimmed)) {
    return trimmed;
  }

  if (!nodeRegistry.has(trimmed)) {
    const baseId = createMermaidNodeId(trimmed);
    let candidateId = baseId;
    let suffix = 2;

    while ([...nodeRegistry.values()].includes(candidateId)) {
      candidateId = `${baseId}_${suffix}`;
      suffix += 1;
    }

    nodeRegistry.set(trimmed, candidateId);
  }

  const nodeId = nodeRegistry.get(trimmed);
  const label = trimmed.replace(/"/g, '&quot;');
  return `${nodeId}["${label}"]`;
}

function normalizeEdgeTarget(segment, nodeRegistry) {
  const trimmed = segment.trim();
  if (!trimmed) {
    return trimmed;
  }

  const edgeLabelMatch = trimmed.match(/^(\|[^|]+\|\s*)(.+)$/);
  if (edgeLabelMatch) {
    return `${edgeLabelMatch[1]}${normalizeNodeRef(edgeLabelMatch[2], nodeRegistry)}`;
  }

  return normalizeNodeRef(trimmed, nodeRegistry);
}

function normalizeFlowchartMermaid(chart) {
  if (!isFlowchartDiagram(chart)) {
    return chart;
  }

  const nodeRegistry = new Map();
  const arrowPattern = /\s(<-->|<--|-->|-.->|==>|---)\s/;

  return chart
    .split('\n')
    .map((line) => {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('%%')) {
        return line;
      }

      const repairedLine = line
        .replace(/-\.\->>/g, ' -.-> ')
        .replace(/-->>/g, ' --> ')
        .replace(/->>/g, ' --> ');

      if (
        /^(graph|flowchart|subgraph|end|direction|classDef|class|style|click|linkStyle)\b/.test(trimmed) ||
        !arrowPattern.test(repairedLine)
      ) {
        return repairedLine;
      }

      const match = repairedLine.match(/^(.*?)(\s(?:<-->|<--|-->|-.->|==>|---)\s)(.*)$/);
      if (!match) {
        return repairedLine;
      }

      const [, left, arrow, right] = match;
      const normalizedLeft = normalizeNodeRef(left, nodeRegistry);
      const normalizedRight = normalizeEdgeTarget(right, nodeRegistry);
      return `${normalizedLeft}${arrow}${normalizedRight}`;
    })
    .join('\n');
}

function hasSequenceDiagramSyntax(lines) {
  return lines.some((line) =>
    /^(participant|actor|activate|deactivate|autonumber|loop|alt|else|opt|par|and|critical|break|rect|note\s+(over|left of|right of)|title)\b/i.test(
      line.trim()
    )
  );
}

function normalizeSequenceMermaid(chart) {
  const lines = chart.split('\n');
  const firstContentIndex = lines.findIndex((line) => line.trim());

  if (firstContentIndex === -1 || !hasSequenceDiagramSyntax(lines)) {
    return chart;
  }

  const firstLine = lines[firstContentIndex].trim();
  if (/^sequenceDiagram\b/i.test(firstLine)) {
    return chart;
  }

  const shouldConvertHeader = /^(graph|flowchart)\b/i.test(firstLine);
  const shouldCleanupSequence = shouldConvertHeader || /^sequenceDiagram\b/i.test(firstLine);

  if (!shouldCleanupSequence) {
    return chart;
  }

  const updatedLines = [...lines];

  if (shouldConvertHeader) {
    updatedLines[firstContentIndex] = 'sequenceDiagram';
  }

  const cleanedLines = updatedLines.filter((line, index) => {
    if (index === firstContentIndex) {
      return true;
    }

    const trimmed = line.trim();
    if (!trimmed) {
      return true;
    }

    return !/^(subgraph|end|direction)\b/i.test(trimmed);
  });

  return cleanedLines.join('\n');
}

function normalizeMermaidDiagram(chart) {
  return normalizeFlowchartMermaid(normalizeSequenceMermaid(chart));
}

function parseAnswer(answer) {
  if (!answer) {
    return { type: 'empty', text: 'No answer yet.' };
  }

  const mermaidMatch = answer.match(/```mermaid\s*([\s\S]*?)```/i);
  if (!mermaidMatch) {
    const bareMermaid = parseBareMermaid(answer);
    if (bareMermaid) {
      return bareMermaid;
    }
    return { type: 'text', text: answer };
  }

  const before = answer.slice(0, mermaidMatch.index).trim();
  const after = answer.slice(mermaidMatch.index + mermaidMatch[0].length).trim();
  const explanation = [before, after].filter(Boolean).join('\n\n');

  return {
    type: 'mermaid',
    diagram: mermaidMatch[1].trim(),
    explanation
  };
}

function MermaidDiagramCanvas({ chart, status, error, isFullscreen = false }) {
  const containerRef = useRef(null);
  const renderId = useId().replace(/:/g, '-');

  useEffect(() => {
    let isActive = true;

    const renderChart = async () => {
      try {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'loose',
          theme: 'base',
          themeVariables: {
            background: '#0f1f2f',
            primaryColor: '#13384d',
            primaryTextColor: '#f4fbff',
            primaryBorderColor: '#61e3d0',
            lineColor: '#8ee6d6',
            secondaryColor: '#163247',
            secondaryTextColor: '#ecf8ff',
            tertiaryColor: '#102536',
            tertiaryTextColor: '#e8f7ff',
            textColor: '#eef9ff',
            mainBkg: '#0f1f2f',
            clusterBkg: '#13293c',
            clusterBorder: '#70d8c9',
            fontFamily: 'Sora, system-ui, sans-serif'
          },
          flowchart: {
            curve: 'basis',
            htmlLabels: false
          }
        });

        const normalizedChart = normalizeMermaidDiagram(chart);
        let result;

        try {
          result = await mermaid.render(`diagram-${renderId}`, chart);
        } catch (initialError) {
          if (normalizedChart === chart) {
            throw initialError;
          }

          result = await mermaid.render(`diagram-${renderId}-normalized`, normalizedChart);
        }

        if (!isActive || !containerRef.current) {
          return;
        }

        const svg = typeof result === 'string' ? result : result.svg;
        containerRef.current.innerHTML = svg;

        if (result && typeof result === 'object' && typeof result.bindFunctions === 'function') {
          result.bindFunctions(containerRef.current);
        }
      } catch (renderError) {
        if (!isActive || !containerRef.current) {
          return;
        }

        containerRef.current.innerHTML = '';
      }
    };

    renderChart();

    return () => {
      isActive = false;
    };
  }, [chart, renderId]);

  return (
    <div className={`mermaid-stage ${isFullscreen ? 'fullscreen' : ''}`}>
      {status === 'loading' ? <div className="preview-empty">Rendering Mermaid diagram...</div> : null}
      <div
        ref={containerRef}
        className={`mermaid-output ${status === 'ready' ? 'is-visible' : ''} ${isFullscreen ? 'fullscreen' : ''}`}
        aria-label="Mermaid diagram"
      />
      {status === 'error' ? (
        <div className="mermaid-fallback">
          <p className="preview-empty">{error}</p>
          <pre className="answer-box answer-box-compact">{chart}</pre>
        </div>
      ) : null}
    </div>
  );
}

function MermaidDiagram({ chart }) {
  const [status, setStatus] = useState('loading');
  const [error, setError] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  useEffect(() => {
    let isActive = true;

    const validateChart = async () => {
      setStatus('loading');
      setError('');

      try {
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: 'loose',
          theme: 'base',
          flowchart: {
            htmlLabels: false
          }
        });

        const normalizedChart = normalizeMermaidDiagram(chart);
        try {
          await mermaid.parse(chart, { suppressErrors: true });
        } catch (initialError) {
          if (normalizedChart === chart) {
            throw initialError;
          }

          await mermaid.parse(normalizedChart, { suppressErrors: true });
        }

        if (!isActive) {
          return;
        }

        setStatus('ready');
      } catch (renderError) {
        if (!isActive) {
          return;
        }
        setStatus('error');
        setError(renderError instanceof Error ? renderError.message : 'Unable to render Mermaid diagram.');
      }
    };

    validateChart();

    return () => {
      isActive = false;
    };
  }, [chart]);

  useEffect(() => {
    if (!isFullscreen) {
      return undefined;
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsFullscreen(false);
      }
    };

    window.addEventListener('keydown', handleKeyDown);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isFullscreen]);

  return (
    <>
    <div className="mermaid-card">
      <div className="mermaid-card-header">
        <div>
          <p className="section-kicker">Generated Diagram</p>
          <h3>Architecture visualization</h3>
        </div>
        <div className="mermaid-toolbar">
          <button
            className="btn secondary mermaid-expand-btn"
            type="button"
            onClick={() => setIsFullscreen(true)}
            disabled={status !== 'ready'}
          >
            Open Modal
          </button>
          <span className={`mermaid-status ${status}`}>{status === 'ready' ? 'Rendered' : status}</span>
        </div>
      </div>

      <MermaidDiagramCanvas chart={chart} status={status} error={error} />
    </div>
    {isFullscreen ? (
      <div className="mermaid-modal-backdrop" role="dialog" aria-modal="true" aria-label="Full screen diagram view">
        <div className="mermaid-modal">
          <div className="mermaid-modal-header">
            <div>
              <p className="section-kicker">Expanded Diagram</p>
              <h3>Architecture visualization</h3>
            </div>
            <div className="mermaid-toolbar">
              <span className={`mermaid-status ${status}`}>{status === 'ready' ? 'Rendered' : status}</span>
              <button className="btn secondary mermaid-expand-btn" type="button" onClick={() => setIsFullscreen(false)}>
                Close
              </button>
            </div>
          </div>
          <div className="mermaid-modal-body">
            <MermaidDiagramCanvas chart={chart} status={status} error={error} isFullscreen />
          </div>
        </div>
      </div>
    ) : null}
    </>
  );
}

export function AnswerRenderer({ answer }) {
  const parsedAnswer = useMemo(() => parseAnswer(answer), [answer]);

  if (parsedAnswer.type === 'mermaid') {
    return (
      <div className="answer-stack">
        <MermaidDiagram chart={parsedAnswer.diagram} />
        {parsedAnswer.explanation ? (
          <div className="answer-text-card">
            <div className="panel-heading compact">
              <div>
                <p className="section-kicker">Diagram Notes</p>
                <h3>Explanation</h3>
              </div>
            </div>
            <pre className="answer-box answer-box-compact">{parsedAnswer.explanation}</pre>
          </div>
        ) : null}
      </div>
    );
  }

  return <pre className="answer-box">{parsedAnswer.text}</pre>;
}
