import React, { useEffect, useState, Component } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Dummy data definitions
const dummySensors = [
  { sensor_type: 'Temperature', value: 23.4, timestamp: new Date(Date.now()-11*60000).toISOString(), is_anomaly: false, anomaly_reason: '' },
  { sensor_type: 'pH Level',     value: 7.3,  timestamp: new Date(Date.now()-9*60000).toISOString(),  is_anomaly: false, anomaly_reason: '' },
  { sensor_type: 'Brightness',    value: 120, timestamp: new Date(Date.now()-7*60000).toISOString(), is_anomaly: false, anomaly_reason: '' },
  { sensor_type: 'Turbidity',    value: 4.1,  timestamp: new Date(Date.now()-7*60000).toISOString(),  is_anomaly: false, anomaly_reason: '' },
  { sensor_type: 'DO',           value: 2.2,  timestamp: new Date(Date.now()-5*60000).toISOString(),  is_anomaly: true,  anomaly_reason: 'Low dissolved oxygen' }
];
const dummyAlerts = [
  { id: 1, title: 'Low DO detected', time: '5m ago' },
  { id: 2, title: 'Rapid pH change', time: '10m ago' },
  { id: 3, title: 'High turbidity spike', time: '15m ago' }
];
const dummyFish = [
  { id: 1, name: 'Clownfish', health: 'Good' },
  { id: 2, name: 'Guppy', health: 'Fair' },
  { id: 3, name: 'Betta', health: 'Excellent' }
];
const dummyUser = { username: 'Guest', plan: 'Basic', memberSince: 'N/A' };

// Styles configuration
const styles = {
  app: { display: 'grid', gridTemplateRows: 'auto auto 1fr', height: '100vh', backgroundImage: 'url("/fish-bg.png"), linear-gradient(180deg,#204a87 0%,#1e3c72 100%)', backgroundBlendMode: 'overlay', backgroundRepeat: 'repeat', backgroundSize: '150px 150px, cover', color: '#e0f7fa', fontFamily: 'Segoe UI, sans-serif' },
  titleBar: { textAlign: 'center', padding: '1rem', background: 'rgba(0,0,50,0.6)', textShadow: '1px 1px 2px rgba(0,0,0,0.5)' },
  title: { margin: 0, fontSize: '2.5rem', fontWeight: '700' },
  subtitle: { margin: 0, fontSize: '1rem', fontStyle: 'italic' },
  nav: { display: 'flex', justifyContent: 'center', gap: '2rem', padding: '0.5rem', background: 'rgba(0,0,50,0.5)', boxShadow: '0 2px 6px rgba(0,0,0,0.4)' },
  navItem: isActive => ({ cursor: 'pointer', padding: '0.5rem 1rem', borderBottom: isActive ? '3px solid #e0f7fa' : '3px solid transparent', transition: 'color 0.3s,border-bottom 0.3s', color: isActive ? '#e0f7fa' : '#b3e5fc' }),
  content: { overflowY: 'auto', padding: '1rem' },
  grid: { display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit,minmax(220px,1fr))', marginBottom: '2rem' },
  card: { background: 'rgba(224,247,250,0.1)', borderRadius: '8px', padding: '1rem', boxShadow: '0 4px 12px rgba(0,0,0,0.3)', transition: 'transform 0.2s' },
  cardHover: { transform: 'translateY(-4px)' },
  chartContainer: { marginBottom: '2rem', padding: '1rem', background: 'rgba(224,247,250,0.1)', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.3)' },
  loader: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh', color: '#e0f7fa' },
  spinner: { width: '48px', height: '48px', border: '6px solid rgba(224,247,250,0.3)', borderTop: '6px solid #e0f7fa', borderRadius: '50%', animation: 'spin 1s linear infinite', marginBottom: '1rem' },
  errorMessage: { textAlign: 'center', color: '#ff8a65', margin: '1rem', fontWeight: 'bold' }
};

// Keyframes for spinner
const styleSheet = document.styleSheets[0]; styleSheet.insertRule('@keyframes spin { to { transform: rotate(360deg); } }', styleSheet.cssRules.length);

// Error boundary to catch UI errors
class ErrorBoundary extends Component {
  state = { hasError: false };
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(err, info) { console.error('ErrorBoundary:', err, info); }
  render() { return this.state.hasError ? <div style={styles.loader}><h2>Something went wrong.</h2></div> : this.props.children; }
}

// Loader spinner component
function Loader() { return <div style={styles.loader}><div style={styles.spinner}></div><div>Loading…</div></div>; }

  // determine day or night
  const now = new Date();
  const hours = now.getHours();
  const icon  = hours >= 6 && hours < 18 ? '☀️' : '🌙';
  const timestamp = now.toLocaleString();

// Recent Alerts page
function RecentAlerts({ alerts, recommendation }) {
  // compute icon + timestamp locally
  const now = new Date();
  const hours = now.getHours();
  const icon  = hours >= 6 && hours < 18 ? '☀️' : '🌙';
  const timestamp = now.toLocaleString();

  return (
    <div>
      <h2>Recent Alerts</h2>

      {/* current date/time with day/night icon */}
      <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
        <span style={{ fontSize: '1.25rem' }}>{icon}</span>
        <span style={{ marginLeft: '0.5rem', fontSize: '1rem' }}>
          {timestamp}
        </span>
      </div>

      {/* alert cards */}
      <div style={styles.grid}>
        {alerts.map(a => (
          <div
            key={a.id}
            style={styles.card}
            onMouseEnter={e => e.currentTarget.style.transform = styles.cardHover.transform}
            onMouseLeave={e => e.currentTarget.style.transform = 'none'}
          >
            <h3>{a.title}</h3>
            <p>{a.time}</p>
          </div>
        ))}
      </div>

      {/* LLM-driven recommendation */}
      <div style={{ ...styles.card, gridColumn: '1 / -1' }}>
        <h3>Tank Owner Tips</h3>
        <p>{recommendation}</p>
      </div>
    </div>
  );
}

// Data Dashboard page
function DataDashboard({ sensors }) {
  const types = [...new Set(sensors.map(s => s.sensor_type))];
  const history = types.reduce((acc, type) => { acc[type] = sensors.filter(s => s.sensor_type === type).map(s => ({ time: new Date(s.timestamp).toLocaleTimeString(), value: s.value })); return acc; }, {});
  return (<div><h2>Data Dashboard</h2><div style={styles.grid}>{sensors.map((s,i) => (<div key={i} style={styles.card} onMouseEnter={e => e.currentTarget.style.transform = styles.cardHover.transform} onMouseLeave={e => e.currentTarget.style.transform = 'none'}><h3>{s.sensor_type}</h3><p style={{fontSize:'2rem'}}>{s.value}</p><small>{new Date(s.timestamp).toLocaleTimeString()}</small>{s.is_anomaly&&<p style={{color:'#ff8a65',marginTop:'0.5rem'}}>🚨 {s.anomaly_reason}</p>}</div>))}</div>{types.map(type => (<div key={type} style={styles.chartContainer}><h3>{type} Trend</h3><ResponsiveContainer width="100%" height={200}><LineChart data={history[type]} margin={{top:5,right:20,left:0,bottom:5}}><CartesianGrid strokeDasharray="3 3" stroke="rgba(224,247,250,0.2)"/><XAxis dataKey="time" stroke="#e0f7fa"/><YAxis stroke="#e0f7fa"/><Tooltip/><Legend/><Line type="monotone" dataKey="value" stroke="#ffeb3b" strokeWidth={2} dot={false}/></LineChart></ResponsiveContainer></div>))}</div>);
}

// My Account page
function MyAccount({ user }) { return (<div><h2>My Account</h2><div style={styles.grid}><div style={styles.card}><h3>Username</h3><p>{user.username}</p></div><div style={styles.card}><h3>Plan</h3><p>{user.plan}</p></div><div style={styles.card}><h3>Member Since</h3><p>{user.memberSince}</p></div></div></div>); }

// My Fish page
function MyFish({ fish }) { return (<div><h2>My Fish</h2><div style={styles.grid}>{fish.map(f => (<div key={f.id} style={styles.card} onMouseEnter={e => e.currentTarget.style.transform = styles.cardHover.transform} onMouseLeave={e => e.currentTarget.style.transform = 'none'}><h3>{f.name}</h3><p>Health: {f.health}</p></div>))}</div></div>); }



// Main App component with live API and dummy fallback
export default function App() {
  const [page, setPage] = useState('Recent Alerts');
  const [sensors, setSensors] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [fish, setFish] = useState([]);
  const [user, setUser] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [recommendation, setRecommendation] = useState('Loading tips...');

  useEffect(() => {
    async function fetchData() {
      try {
        const res = await fetch('http://localhost:5000/api/data');
        if (!res.ok) throw new Error(res.statusText);
        const data = await res.json();
        setSensors(data);
        // once we have sensor data, request LLM tips:
        const temp  = data.find(s => s.sensor_type === 'Temperature')?.value;
        const ph    = data.find(s => s.sensor_type === 'pH Level')?.value;
        const light = data.find(s => s.sensor_type === 'Brightness')?.value;
        try {
          const recRes = await fetch('http://localhost:5000/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ temp, ph, light })
          });
          if (!recRes.ok) throw new Error(recRes.statusText);
          const recJson = await recRes.json();
          setRecommendation(recJson.recommendation || recJson.text || 'No tips available.');
        } catch {
          setRecommendation('Unable to load recommendations.');
        }
      } catch (e) {
        console.error(e);
        setError('Failed to fetch sensor data');
        setSensors(dummySensors);
        setRecommendation('Showing default tips.');
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  const pages = {
    'Recent Alerts': () => <RecentAlerts alerts={error ? dummyAlerts : alerts} recommendation={recommendation} />,    
    'Data Dashboard': () => <DataDashboard sensors={error ? dummySensors : sensors} />,    
    'My Account':    () => <MyAccount user={error ? dummyUser : user} />,    
    'My Fish':       () => <MyFish fish={error ? dummyFish : fish} />
  };
  const PageComponent = pages[page];

  return (
    <ErrorBoundary>
      <div style={styles.app}>
        <div style={styles.titleBar}>
          <h1 style={styles.title}>AquaSense</h1>
          <h4 style={styles.subtitle}>by 93 Boyz</h4>
        </div>
        <nav style={styles.nav}>
          {Object.keys(pages).map(p => (
            <div key={p} style={styles.navItem(page === p)} onClick={() => setPage(p)}>{p}</div>
          ))}
        </nav>
        <main style={styles.content}>
          {loading ? <Loader /> : (
            <>
              {error && <div style={styles.errorMessage}>{error}</div>}
              <PageComponent />
            </>
          )}
        </main>
      </div>
    </ErrorBoundary>
  );
}
