import { useEffect, useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend,
} from 'chart.js';
import { getKPIs, getReadings, KPISummary, SensorReading } from '../api/client';
import KpiCard from '../components/KpiCard';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPISummary | null>(null);
  const [readings, setReadings] = useState<SensorReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([getKPIs(), getReadings({ limit: 200 })])
      .then(([k, r]) => {
        setKpis(k);
        setReadings(r);
      })
      .catch(() => setError('Could not reach the API. Is the backend running on :8000?'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="p-6 text-t2">Loading dashboard…</div>;
  if (error) return <div className="p-6 text-red">{error}</div>;
  if (!kpis) return null;

  const chartData = {
    labels: readings.slice().reverse().map(r => new Date(r.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Output Rate (uph)',
        data: readings.slice().reverse().map(r => r.output_rate),
        borderColor: '#2ec4b6',
        backgroundColor: 'rgba(46,196,182,0.1)',
        fill: true,
        tension: 0.3,
        pointRadius: 0,
      },
    ],
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-xl font-semibold">Executive Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <KpiCard label="OEE" value={`${kpis.oee}%`} tone={kpis.oee >= 85 ? 'good' : kpis.oee >= 60 ? 'warn' : 'bad'} />
        <KpiCard label="Production Today" value={kpis.production_today.toLocaleString()} />
        <KpiCard label="Downtime" value={`${kpis.downtime_hours_today} hrs`} tone={kpis.downtime_hours_today > 4 ? 'bad' : 'good'} />
        <KpiCard label="Machine Health" value={`${kpis.machine_health_pct}%`} />
        <KpiCard label="Active Alarms" value={kpis.active_alarms} tone={kpis.active_alarms > 0 ? 'warn' : 'good'} />
        <KpiCard label="Quality Rate" value={`${kpis.quality_rate}%`} tone={kpis.quality_rate >= 95 ? 'good' : 'warn'} />
        <KpiCard label="Energy Consumption" value={`${kpis.energy_kwh_today.toLocaleString()} kWh`} />
      </div>

      <div className="bg-bg1 border border-line rounded-lg p-4">
        <h2 className="text-sm font-semibold mb-3 text-t1">Recent Output Rate</h2>
        <div className="h-64">
          <Line
            data={chartData}
            options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }}
          />
        </div>
      </div>
    </div>
  );
}
