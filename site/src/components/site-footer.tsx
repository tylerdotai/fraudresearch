const REPO = 'https://github.com/tylerdotai/fraudresearch';
const groups = [
  { title: 'Toolkit', links: [ ['Quick start', `${REPO}#quick-start`], ['Install the profile', '#start'], ['Source coverage', `${REPO}/blob/main/SOURCE-REGISTRY.json`], ['Verification', `${REPO}/blob/main/docs/VERIFICATION.md`] ] },
  { title: 'Research standards', links: [ ['Evidence preservation', `${REPO}/blob/main/skills/preserve-evidence/SKILL.md`], ['Challenge findings', `${REPO}/blob/main/skills/challenge-findings/SKILL.md`], ['Privacy and data flows', `${REPO}/blob/main/docs/PRIVACY.md`], ['Official program guidance', 'https://america.gov/fraud'] ] },
  { title: 'Community', links: [ ['Contributing', `${REPO}/tree/main#help-improve-the-methods`], ['Software issues', `${REPO}/issues`], ['Security policy', `${REPO}/blob/main/SECURITY.md`], ['MIT license', `${REPO}/blob/main/LICENSE`] ] },
  { title: 'Platform', links: [ ['Hermes Agent', 'https://hermes-agent.nousresearch.com/'], ['Hermes documentation', 'https://hermes-agent.nousresearch.com/docs/'], ['Nous Research', 'https://nousresearch.com/'], ['shadcn/ui', 'https://ui.shadcn.com/'] ] },
];

export function SiteFooter() {
  return <footer className="site-footer"><div className="shell">
    <div className="footer-brand-row"><a className="footer-brand" href="#"><img src={`${import.meta.env.BASE_URL}brand-logo.webp`} alt="FraudResearch eagle and research-lens logo" width="62" height="62" loading="lazy" /><span>FraudResearch<small>AI AGAINST AMERICAN FRAUD</small></span></a><p>Public methods. Private evidence.<br /><strong>Human judgment.</strong></p></div>
    <div className="footer-columns">{groups.map(group => <nav key={group.title} aria-label={group.title}><h2>{group.title}</h2><ul>{group.links.map(([label, href]) => <li key={label}><a href={href}>{label}</a></li>)}</ul></nav>)}</div>
    <div className="footer-boundary"><strong>This is not a fraud-tip intake service.</strong><p>Do not post allegations, credentials, personal information or evidence in public issues. Use synthetic examples for software reports. Reporting decisions belong to people, not this website.</p></div>
    <div className="footer-legal"><p>Not affiliated with the U.S. government. No Nous Research endorsement is claimed. Research assistance, not legal advice or a fraud determination.</p><p>Copyright 2026 FraudResearch contributors. Platform marks retain their owners' rights.</p></div>
    <div className="footer-briefs"><a href={`${REPO}/tree/main`}>Latest source on main</a><a href={`${REPO}/actions/workflows/verify.yml?query=branch%3Amain`}>Latest build status</a><a href={`${import.meta.env.BASE_URL}llms.txt`}>Project brief for AI readers</a><a href={`${import.meta.env.BASE_URL}sitemap.xml`}>Sitemap</a><a href={`${REPO}/blob/main/site/README.md`}>Artwork and credits</a></div>
  </div></footer>;
}
