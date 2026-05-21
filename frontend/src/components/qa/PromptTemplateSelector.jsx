import React from 'react';

export function PromptTemplateSelector({
  isBusy,
  onApplyTemplate,
  onRunTemplate,
  selectedTemplateId,
  templates
}) {
  const groupedTemplates = templates.reduce((groups, template) => {
    const key = template.category;
    groups[key] = groups[key] || [];
    groups[key].push(template);
    return groups;
  }, {});

  const selectedTemplate = templates.find((template) => template.id === selectedTemplateId) || null;

  return (
    <section className="panel">
      <div className="panel-heading compact">
        <div>
          <p className="section-kicker">Predefined AI Prompts</p>
          <h2>Repository analysis templates</h2>
        </div>
      </div>

      <select
        className="template-select"
        value={selectedTemplateId}
        onChange={(event) => onApplyTemplate(event.target.value)}
      >
        <option value="">Select a predefined prompt</option>
        {Object.entries(groupedTemplates).map(([category, categoryTemplates]) => (
          <optgroup key={category} label={category}>
            {categoryTemplates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.title}
              </option>
            ))}
          </optgroup>
        ))}
      </select>

      {selectedTemplate ? (
        <div className="template-card">
          <div className="chip-row">
            <span className="chip">{selectedTemplate.category}</span>
            <span className="chip subtle">{selectedTemplate.output_format}</span>
          </div>
          <div className="button-row">
            <button
              className="btn"
              type="button"
              onClick={() => onRunTemplate(selectedTemplate.id)}
              disabled={isBusy}
            >
              Run Template
            </button>
          </div>
        </div>
      ) : null}
    </section>
  );
}
