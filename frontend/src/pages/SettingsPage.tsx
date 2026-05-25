export default function SettingsPage() {
  return (
    <div>
      <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Settings</h2>

      <div className="section-card">
        <div className="section-card-title">Notification Channels</div>
        {[
          { name: 'DingTalk', url: 'https://oapi.dingtalk.com/robot/...', type: 'Webhook', enabled: true },
          { name: 'Email', url: 'ops-team@example.com', type: 'SMTP', enabled: true },
          { name: 'Feishu', url: 'Not configured', type: 'Webhook', enabled: false },
        ].map(ch => (
          <div key={ch.name} style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '6px 8px',
            background: '#0f172a', borderRadius: 3, marginBottom: 6,
          }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: ch.enabled ? '#22c55e' : '#334155' }} />
            <span style={{ color: ch.enabled ? '#e2e8f0' : '#64748b', fontSize: 10, flex: 1 }}>{ch.name}</span>
            <span style={{ color: '#64748b', fontSize: 9, background: '#1e293b', padding: '2px 8px', borderRadius: 3 }}>{ch.url}</span>
            <span style={{ color: '#64748b', fontSize: 9 }}>{ch.type}</span>
            <button className="btn-primary" style={{ fontSize: 9, padding: '2px 8px' }}>
              {ch.enabled ? 'Edit' : '+ Add'}
            </button>
          </div>
        ))}
      </div>

      <div className="section-card">
        <div className="section-card-title">Global Parameters</div>
        <div className="config-row">
          {[
            { label: 'Alert Cooldown (min)', value: '5' },
            { label: 'Data Retention (days)', value: '90' },
            { label: 'Retrain Interval (days)', value: '30' },
          ].map(field => (
            <div className="config-field" key={field.label}>
              <div className="form-label">{field.label}</div>
              <input className="form-input" defaultValue={field.value} />
            </div>
          ))}
          <button className="btn-primary" style={{ alignSelf: 'flex-end' }}>Save</button>
        </div>
      </div>
    </div>
  )
}
