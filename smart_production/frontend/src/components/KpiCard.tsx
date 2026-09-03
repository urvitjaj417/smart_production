interface KpiCardProps {
  label: string;
  value: string | number;
  delta?: string;
  tone?: 'good' | 'warn' | 'bad' | 'neutral';
}

const toneClasses: Record<NonNullable<KpiCardProps['tone']>, string> = {
  good: 'text-green',
  warn: 'text-orange',
  bad: 'text-red',
  neutral: 'text-acc',
};

export default function KpiCard({ label, value, delta, tone = 'neutral' }: KpiCardProps) {
  return (
    <div className="bg-bg1 border border-line rounded-lg p-4 shadow-sm">
      <div className="text-[0.7rem] uppercase tracking-wide text-t2 mb-1">{label}</div>
      <div className={`text-2xl font-semibold ${toneClasses[tone]}`}>{value}</div>
      {delta && <div className="text-xs text-t2 mt-1">{delta}</div>}
    </div>
  );
}
