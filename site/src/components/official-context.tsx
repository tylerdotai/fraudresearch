import context from '@/content/official-context.json';

export function OfficialContext() {
  return <section className="official-section" aria-labelledby="official-heading"><div className="shell">
    <div className="official-intro"><div><p className="eyebrow">GOVERNMENT-REPORTED CONTEXT</p><h2 id="official-heading">The scale.<br /><em>The responsibility.</em></h2></div><p>Our mission is to help tackle fraud in America with AI: preserve the public record, test specific questions and give people evidence they can review.</p></div>
    <dl className="official-metrics">{context.metrics.map(metric => <div key={metric.label}><dt>{metric.label}<span>{metric.period}</span></dt><dd>{metric.display}</dd></div>)}</dl>
    <p className="official-citation"><a href={context.source_url}>America.gov partner-agency totals</a>, snapshot retrieved {context.retrieved_at.slice(0, 10)} UTC. Different measures and periods; do not add them. Not independently audited here. <strong>Not results from FraudResearch.</strong> <a href={`${import.meta.env.BASE_URL}official-context.json`}>Source record and original checksum</a>.</p>
  </div></section>;
}
