import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const styles = {
  page: { minHeight: '100vh', background: 'var(--bg)', padding: '20px' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', maxWidth: '1000px', margin: '0 auto 24px' },
  headerLeft: { display: 'flex', alignItems: 'center', gap: '12px' },
  title: { fontSize: '24px', fontWeight: '700' },
  headerBtn: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '8px 16px', color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '13px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', maxWidth: '1000px', margin: '0 auto 24px' },
  statCard: { background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', padding: '20px' },
  statLabel: { fontSize: '13px', color: 'var(--text-secondary)', marginBottom: '4px' },
  statValue: { fontSize: '28px', fontWeight: '700' },
  statHighlight: { fontSize: '28px', fontWeight: '700', color: 'var(--primary)' },
  section: { maxWidth: '1000px', margin: '0 auto 24px' },
  sectionTitle: { fontSize: '16px', fontWeight: '600', marginBottom: '12px' },
  table: { width: '100%', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', overflow: 'hidden' },
  th: { padding: '12px 16px', textAlign: 'left', fontSize: '12px', color: 'var(--text-secondary)', fontWeight: '500', borderBottom: '1px solid var(--border)', background: 'var(--bg-elevated)' },
  td: { padding: '12px 16px', fontSize: '13px', borderBottom: '1px solid var(--border)' },
  badge: (color) => ({ background: `${color}20`, color, padding: '2px 8px', borderRadius: '12px', fontSize: '11px', fontWeight: '500' }),
  empty: { padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '14px' },
  catBar: { display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' },
  catLabel: { fontSize: '13px', color: 'var(--text-secondary)', width: '100px', flexShrink: 0 },
  catBarFill: (pct, color) => ({ height: '8px', borderRadius: '4px', background: color, width: `${Math.max(pct, 3)}%`, transition: 'width 0.5s ease' }),
  catValue: { fontSize: '12px', color: 'var(--text-muted)', minWidth: '60px', textAlign: 'right' },
};

const CAT_COLORS = { fuel: '#f59e0b', raw_material: '#3b82f6', utility: '#8b5cf6', salary: '#ef4444', travel: '#06b6d4', food: '#10b981', misc: '#6b7280' };

export default function Dashboard({ handleLogout }) {
  const [summary, setSummary] = useState(null);
  const [expenses, setExpenses] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sumRes, expRes, invRes] = await Promise.all([
          api.get('/api/expenses/summary/monthly'),
          api.get('/api/expenses/?limit=10'),
          api.get('/api/invoices/?limit=10'),
        ]);
        setSummary(sumRes.data);
        setExpenses(expRes.data);
        setInvoices(invRes.data);
      } catch (err) {
        console.error('Dashboard load failed:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div style={{ ...styles.page, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><div style={{ color: 'var(--text-muted)' }}>Loading dashboard...</div></div>;

  const s = summary || { total_amount: 0, expense_count: 0, gst_total: 0, by_category: {}, top_vendors: [] };
  const maxCat = Math.max(...Object.values(s.by_category || {}), 1);

  return (
    <div style={styles.page}>
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <h1 style={styles.title}>📊 <span className="text-gradient">Dashboard</span></h1>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button style={styles.headerBtn} onClick={() => navigate('/chat')}>💬 Chat</button>
          <button style={{ ...styles.headerBtn, borderColor: 'var(--danger)', color: 'var(--danger)' }} onClick={handleLogout}>↪ Logout</button>
        </div>
      </div>

      <div style={styles.grid}>
        <div style={styles.statCard}><div style={styles.statLabel}>Total Spent (This Month)</div><div style={styles.statHighlight}>₹{s.total_amount.toLocaleString()}</div></div>
        <div style={styles.statCard}><div style={styles.statLabel}>Expenses</div><div style={styles.statValue}>{s.expense_count}</div></div>
        <div style={styles.statCard}><div style={styles.statLabel}>GST Input Credit</div><div style={styles.statValue}>₹{s.gst_total.toLocaleString()}</div></div>
        <div style={styles.statCard}><div style={styles.statLabel}>Top Vendor</div><div style={styles.statValue}>{s.top_vendors?.[0] || '—'}</div></div>
      </div>

      {Object.keys(s.by_category || {}).length > 0 && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Category Breakdown</h2>
          <div style={{ ...styles.statCard, padding: '20px' }}>
            {Object.entries(s.by_category).sort((a, b) => b[1] - a[1]).map(([cat, amt]) => (
              <div key={cat} style={styles.catBar}>
                <span style={styles.catLabel}>{cat}</span>
                <div style={{ flex: 1, background: 'var(--bg-input)', borderRadius: '4px', height: '8px' }}>
                  <div style={styles.catBarFill(amt / maxCat * 100, CAT_COLORS[cat] || '#6b7280')} />
                </div>
                <span style={styles.catValue}>₹{amt.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Recent Expenses</h2>
        <div style={styles.table}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={styles.th}>Date</th>
                <th style={styles.th}>Description</th>
                <th style={styles.th}>Category</th>
                <th style={styles.th}>Amount</th>
              </tr>
            </thead>
            <tbody>
              {expenses.length === 0 ? (
                <tr><td colSpan="4" style={styles.empty}>No expenses yet. Start by recording one in chat!</td></tr>
              ) : expenses.map((exp) => (
                <tr key={exp.id}>
                  <td style={styles.td}>{exp.date}</td>
                  <td style={styles.td}>{exp.description}</td>
                  <td style={styles.td}><span style={styles.badge(CAT_COLORS[exp.category] || '#6b7280')}>{exp.category}</span></td>
                  <td style={styles.td}>₹{exp.amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Recent Invoices</h2>
        <div style={styles.table}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={styles.th}>Invoice #</th>
                <th style={styles.th}>Customer</th>
                <th style={styles.th}>Status</th>
                <th style={styles.th}>Total</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr><td colSpan="4" style={styles.empty}>No invoices yet. Create one from chat!</td></tr>
              ) : invoices.map((inv) => (
                <tr key={inv.id}>
                  <td style={styles.td}>{inv.invoice_number || `#${inv.id}`}</td>
                  <td style={styles.td}>{inv.customer_name}</td>
                  <td style={styles.td}><span style={styles.badge(inv.status === 'paid' ? '#10b981' : inv.status === 'overdue' ? '#ef4444' : '#f59e0b')}>{inv.status}</span></td>
                  <td style={styles.td}>₹{inv.total_amount.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
