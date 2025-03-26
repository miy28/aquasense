import React, { useEffect, useState } from 'react';

function App() {
  const [sensorData, setSensorData] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5000/api/data')
      .then(res => res.json())
      .then(data => setSensorData(data))
      .catch(err => console.error('Failed to fetch:', err));
  }, []);

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>AquaSense Dashboard 💧</h1>
      {sensorData.length > 0 ? (
        <ul>
          {sensorData.map((row, i) => (
            <li key={i}>
              <strong>{row.sensor_type}</strong>: {row.value} @ {row.timestamp}
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading data...</p>
      )}
    </div>
  );
}

export default App;
