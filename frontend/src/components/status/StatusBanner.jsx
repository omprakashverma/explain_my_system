import React from 'react';

export function StatusBanner({ error }) {
  if (!error) return null;
  return (
    <section className="panel panel-alert">
      <p className="panel-alert-title">Action error</p>
      <p>{error}</p>
    </section>
  );
}
