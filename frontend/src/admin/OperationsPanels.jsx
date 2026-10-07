import React from 'react';

export function ReportsPanel({ reports, businesses, onUpdate }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">MODERATION</p><h2>Business reports</h2></div>
      <div className="admin-record-list">
        {reports.map((report) => (
          <article className="operation-record" key={report.id}>
            <div><strong>{businesses.find((business) => business.id === report.business_id)?.name || 'Directory report'}</strong><span>{report.reason} · {report.message || 'No additional details'}</span></div>
            <select aria-label={`Report ${report.id} status`} value={report.status} onChange={(event) => onUpdate(report.id, { status: event.target.value })}>
              <option value="pending">Pending</option><option value="resolved">Resolved</option><option value="dismissed">Dismissed</option>
            </select>
          </article>
        ))}
        {!reports.length && <p className="admin-copy">No reports have been submitted.</p>}
      </div>
    </>
  );
}

export function VerificationPanel({ verifications, businesses, onUpdate }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">QUALITY CONTROL</p><h2>Business verification</h2></div>
      <div className="admin-record-list">
        {verifications.map((verification) => (
          <article className="operation-record" key={verification.id}>
            <div><strong>{businesses.find((business) => business.id === verification.business_id)?.name || `Business ${verification.business_id}`}</strong><span>{verification.notes || 'No review notes'}</span></div>
            <select aria-label={`Verification ${verification.id} status`} value={verification.status} onChange={(event) => onUpdate(verification.id, { status: event.target.value, notes: verification.notes })}>
              <option value="pending">Pending</option><option value="verified">Verified</option><option value="rejected">Rejected</option>
            </select>
          </article>
        ))}
        {!verifications.length && <p className="admin-copy">No verification requests are waiting.</p>}
      </div>
    </>
  );
}

export function UsersPanel({ users }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">ACCESS CONTROL</p><h2>Users</h2></div>
      <div className="admin-record-list">
        {users.map((user) => (
          <article className="operation-record" key={user.id}>
            <div><strong>{user.name}</strong><span>{user.email}</span></div>
            <span>{user.role?.name || user.role || 'Unassigned'} · {user.status}</span>
          </article>
        ))}
      </div>
    </>
  );
}

export function AuditPanel({ auditLogs, users }) {
  return (
    <>
      <div className="admin-section-title"><p className="admin-eyebrow">CHANGE HISTORY</p><h2>Audit log</h2></div>
      <div className="admin-record-list">
        {auditLogs.map((entry) => (
          <article className="operation-record" key={entry.id}>
            <div><strong>{entry.action} · {entry.entity_type}{entry.entity_id ? ` #${entry.entity_id}` : ''}</strong><span>{entry.details || 'No details'}</span></div>
            <span>{users.find((user) => user.id === entry.actor_id)?.name || 'System'} · {new Date(entry.created_at).toLocaleString()}</span>
          </article>
        ))}
        {!auditLogs.length && <p className="admin-copy">No audit events have been recorded.</p>}
      </div>
    </>
  );
}