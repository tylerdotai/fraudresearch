import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowDown, ArrowRight, ArrowUpRight, Check, CheckCheck, Copy, FileCheck2, Fingerprint, FolderLock, Menu, Search, Terminal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Progress } from '@/components/ui/progress';
import { OfficialContext } from '@/components/official-context';
import { SiteFooter } from '@/components/site-footer';
import './index.css';
import './brand.css';
import './enhancements.css';

const REPO = 'https://github.com/tylerdotai/fraudresearch';
const SOURCE = `${REPO}/tree/main`;
const INSTALL = 'hermes profile install github.com/tylerdotai/fraudresearch --name fraudresearch-starter';
const WORKBENCH = 'git clone https://github.com/tylerdotai/fraudresearch.git\ncd fraudresearch\nuv sync --frozen --group dev';
const links = [{ label: 'The method', href: '#method' }, { label: 'The toolkit', href: '#toolkit' }, { label: 'Get started', href: '#start' }, { label: 'Questions', href: '#questions' }];

const steps = [
  { title: 'Ask a question you can disprove.', text: 'Define the program, period and population. Decide what evidence would change your mind before searching for a subject.' },
  { title: 'Keep the source, not just the summary.', text: 'Preserve original bytes, retrieval dates and checksums. Trace each material statement to an exact page, row or line.' },
  { title: 'Challenge the apparent contradiction.', text: 'Check identifiers, dates, payment units and the strongest lawful explanation. An outlier is a question, not a verdict.' },
  { title: 'Put the limits beside the finding.', text: 'Keep contrary evidence, unresolved links and originality gaps visible. Prepare a private draft for human review, or document why the lead stops.' },
];

function App() {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const [installMode, setInstallMode] = useState('hermes');
  const [readingProgress, setReadingProgress] = useState(0);
  useEffect(() => {
    const update = () => {
      const available = document.documentElement.scrollHeight - window.innerHeight;
      setReadingProgress(available > 0 ? Math.min(100, Math.round(window.scrollY / available * 100)) : 0);
    };
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (entry.isIntersecting) { entry.target.classList.add('is-visible'); observer.unobserve(entry.target); }
    }), { threshold: 0.08 });
    document.querySelectorAll('main section').forEach(section => { section.classList.add('motion-section'); observer.observe(section); });
    update();
    window.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update);
    return () => { observer.disconnect(); window.removeEventListener('scroll', update); window.removeEventListener('resize', update); };
  }, []);
  async function copyCommand() {
    try { await navigator.clipboard.writeText(installMode === 'hermes' ? INSTALL : WORKBENCH); setCopied(true); setCopyError(false); }
    catch { setCopyError(true); }
  }
  return <>
    <a href="#main" className="skip-link">Skip to content</a>
    <Progress value={readingProgress} className="reading-progress" aria-label="Page reading progress" />
    <div className="civic-rule" aria-hidden="true" />
    <header className="site-header">
      <div className="shell header-inner">
        <a className="wordmark" href="#" aria-label="FraudResearch home"><img className="graphic-logo" src={`${import.meta.env.BASE_URL}brand-logo.webp`} alt="Eagle and research-lens logo" width="54" height="54" />FraudResearch<span className="wordmark-label">PUBLIC METHODS</span></a>
        <nav className="desktop-nav" aria-label="Main navigation">{links.map(link => <a key={link.href} href={link.href}>{link.label}</a>)}</nav>
        <Button asChild variant="outline" className="header-source"><a href={SOURCE}>GitHub <ArrowUpRight aria-hidden="true" /></a></Button>
        <Sheet><SheetTrigger asChild><Button variant="outline" size="icon" className="mobile-nav-trigger" aria-label="Open navigation"><Menu /></Button></SheetTrigger>
          <SheetContent><SheetHeader><SheetTitle>Navigation</SheetTitle><SheetDescription>Explore the research method and open-source toolkit.</SheetDescription></SheetHeader>
            <nav className="mobile-links" aria-label="Mobile navigation">{links.map(link => <SheetClose asChild key={link.href}><a href={link.href}>{link.label}<ArrowUpRight aria-hidden="true" /></a></SheetClose>)}<a href={SOURCE}>GitHub<ArrowUpRight aria-hidden="true" /></a></nav>
          </SheetContent>
        </Sheet>
      </div>
    </header>
    <main id="main">
      <div className="hero-stage"><section className="shell hero" aria-labelledby="hero-heading">
        <div className="hero-copy">
          <p className="eyebrow"><span />PUBLIC RECORDS. PRIVATE EVIDENCE.</p>
          <h1 id="hero-heading">AI against <span>American</span> <em>fraud.</em></h1>
          <p className="hero-description">Put AI to work for the public interest. Trace the records, challenge the story and help protect America's public programs. Evidence first. Always.</p>
          <div className="hero-actions"><Button asChild size="lg"><a href="#start">Explore the toolkit <ArrowRight aria-hidden="true" /></a></Button><Button asChild variant="outline" size="lg"><a href={SOURCE}>View source <ArrowUpRight aria-hidden="true" /></a></Button></div>
          <a className="hermes-lockup" href="https://hermes-agent.nousresearch.com/"><img src={`${import.meta.env.BASE_URL}nous-girl.svg`} alt="Nous girl, the Hermes host-platform brand mark" width="40" height="40" /><span>POWERED BY <strong>HERMES</strong></span><ArrowUpRight aria-hidden="true" /></a>
          <p className="hero-note">Community built. Research only. Human review required.</p>
        </div>
        <figure className="eagle-hero">
          <div className="mascot-eyebrow"><span>THE EVIDENCE EAGLE</span><span>FRAUDRESEARCH</span></div>
          <img className="mascot-image" src={`${import.meta.env.BASE_URL}eagle-mascot.webp`} alt="Eagle investigator mascot with an American flag, a magnifying glass and a records folder" width="1024" height="1536" fetchPriority="high" />
          <div className="mascot-tagline">FOR THE PUBLIC.<br /><span>FOR THE RECORD.</span></div>
          <figcaption>A fictional community mascot, not a government investigator or an official seal.</figcaption>
        </figure>
      </section></div>
      <div className="shell"><Separator /></div>
      <section className="shell standards" aria-label="Research boundaries">
        <div><FolderLock aria-hidden="true" /><p><strong>Private evidence</strong><span>No cases or identifying records bundled.</span></p></div>
        <div><Fingerprint aria-hidden="true" /><p><strong>Traceable methods</strong><span>Original bytes, exact locators and checksums.</span></p></div>
        <div><CheckCheck aria-hidden="true" /><p><strong>Human judgment</strong><span>No automatic accusations or submissions.</span></p></div>
      </section>
      <OfficialContext />
      <div className="shell"><Separator /></div>
      <section id="method" className="shell method section-space" aria-labelledby="method-heading">
        <div className="section-intro"><p className="eyebrow">01 / THE METHOD</p><h2 id="method-heading">Curiosity is the start.<br /><em>Proof is the standard.</em></h2><p>FraudResearch helps you organize a defensible investigation. It also helps you recognize when the public record cannot support a conclusion.</p><a className="text-link" href={`${REPO}/blob/main/skills/run-investigations/SKILL.md`}>Read the investigation workflow <ArrowUpRight aria-hidden="true" /></a></div>
        <ol className="method-list">{steps.map((step, index) => <li key={step.title}><span className="step-number">{String(index + 1).padStart(2, '0')}</span><div><h3>{step.title}</h3><p>{step.text}</p></div></li>)}</ol>
      </section>
      <section className="patriotic-band" aria-label="Project mission"><div className="shell"><div className="mission-banner"><img src={`${import.meta.env.BASE_URL}patriotic-banner.webp`} alt="Fictional eagle illustration flying before an American flag" width="2057" height="765" loading="lazy" /><div className="mission-banner-copy"><p>LESS GUESSWORK.<br /><strong>MORE EVIDENCE.</strong></p><span>AI-assisted research. Human-led accountability.</span></div></div></div></section>
      <section id="toolkit" className="toolkit-section section-space" aria-labelledby="toolkit-heading">
        <div className="shell">
          <div className="section-topline"><div><p className="eyebrow">02 / THE TOOLKIT</p><h2 id="toolkit-heading">Useful tools.<br /><em>Explicit limits.</em></h2></div><p>A Python workbench and a focused Hermes profile. Use them together, or start with the offline example. No evidence is preloaded.</p></div>
          <div className="tool-row"><div className="tool-title"><Search aria-hidden="true" /><div><h3>Find and preserve</h3><span>OFFICIAL PUBLIC SOURCES</span></div></div><p>Discover CMS and OIG sources, preserve originals and separate extracted text from source bytes.</p><span className="limit-note">A directory is not a claims ledger.</span></div>
          <div className="tool-row"><div className="tool-title"><Terminal aria-hidden="true" /><div><h3>Reproduce the analysis</h3><span>BOUNDED DATA WORKBENCH</span></div></div><p>Use string-preserving Parquet, exact identifier joins, Decimal calculations and integrity checks.</p><span className="limit-note">Matching values do not prove misconduct.</span></div>
          <div className="tool-row"><div className="tool-title"><FileCheck2 aria-hidden="true" /><div><h3>Prepare for review</h3><span>13 LINKED RESEARCH SKILLS</span></div></div><p>Map claims to evidence, challenge alternatives and export private drafts with visible blockers.</p><span className="limit-note">A structural pass is not a legal finding.</span></div>
          <a className="text-link toolkit-link" href={`${REPO}#official-source-connectors`}>See source coverage and current limitations <ArrowUpRight aria-hidden="true" /></a>
        </div>
      </section>
      <section className="hermes-feature" aria-labelledby="hermes-heading"><div className="shell hermes-feature-grid"><figure><img src={`${import.meta.env.BASE_URL}nous-mascot.webp`} alt="Nous-inspired adult research mascot with black bob hair, a white wing clip and an open notebook" width="1024" height="1536" loading="lazy" /><figcaption>Original community artwork inspired by the Nous girl identity.</figcaption></figure><div><p className="eyebrow">HERMES BRAINS. AMERICAN WINGS.</p><h2 id="hermes-heading">An open agent.<br /><em>A public purpose.</em></h2><p>Built as a focused profile for Hermes Agent by Nous Research. The model helps organize the work. The method keeps the evidence, contradictions and limits in view.</p><ul><li>13 linked research skills, not a one-line accusation prompt.</li><li>Private evidence storage, separate from public methods.</li><li>Human review before any contact, publication or submission.</li></ul><Button asChild variant="outline" size="lg"><a href="https://hermes-agent.nousresearch.com/">Meet Hermes Agent <ArrowUpRight aria-hidden="true" /></a></Button><p className="community-note">Independent community project. No Nous Research endorsement is claimed.</p></div></div></section>
      <section id="start" className="shell section-space start-section" aria-labelledby="start-heading">
        <div className="section-topline"><div><p className="eyebrow">03 / GET STARTED</p><h2 id="start-heading">Start small.<br /><em>Keep it reproducible.</em></h2></div><p>The first example uses two clearly invented records. It calculates a total, exports an incomplete private draft and verifies its attachments. No real subjects. No network requests from the demo.</p></div>
        <div className="installation">
          <div className="installation-heading"><div><span className="terminal-dot" aria-hidden="true" /><span>CHOOSE YOUR SETUP</span></div><Badge variant="outline">MIT licensed</Badge></div>
          <Tabs value={installMode} onValueChange={value => { setInstallMode(value); setCopied(false); setCopyError(false); }}><TabsList aria-label="Installation method"><TabsTrigger value="hermes">Hermes profile</TabsTrigger><TabsTrigger value="workbench">Python workbench</TabsTrigger></TabsList>{[['hermes', INSTALL], ['workbench', WORKBENCH]].map(([mode, command]) => <TabsContent key={mode} value={mode}><div className="command-row"><code>{command}</code><Tooltip><TooltipTrigger asChild><Button variant="outline" onClick={copyCommand} aria-label="Copy install command">{copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}{copied ? 'Copied' : 'Copy'}</Button></TooltipTrigger><TooltipContent>Copy this setup command</TooltipContent></Tooltip></div></TabsContent>)}</Tabs>
          <div className="installation-footer"><p>{installMode === 'hermes' ? 'Requires Hermes and uv. Configure your own model and optional local web services.' : 'Requires Python 3.11+, uv and Git. Hermes is optional. The offline example needs no model.'}</p><span role="status" aria-live="polite">{copyError ? 'Select and copy the command manually.' : copied ? 'Copied to clipboard.' : ''}</span></div>
        </div>
        <div className="start-actions"><Button asChild size="lg"><a href={`${REPO}#quick-start`}>Run the offline example <ArrowUpRight aria-hidden="true" /></a></Button><a className="text-link" href={`${REPO}/blob/main/docs/SETUP.md`}>Read the setup guide <ArrowRight aria-hidden="true" /></a></div>
        <div className="research-note"><span className="note-line" aria-hidden="true" /><p><strong>A useful result can be “no supported finding.”</strong> Keep rejected leads and contrary evidence. Do not adjust a method just to make someone look suspicious.</p></div>
      </section>
      <section id="questions" className="questions-section section-space" aria-labelledby="questions-heading"><div className="shell questions-grid"><div><p className="eyebrow">04 / BEFORE YOU BEGIN</p><h2 id="questions-heading">A few important<br /><em>distinctions.</em></h2><p className="question-intro">Good public-interest research starts with clear boundaries.</p></div>
        <Accordion type="single" collapsible>
          <AccordionItem value="verdict"><AccordionTrigger>Does this software determine whether someone committed fraud?</AccordionTrigger><AccordionContent>No. It organizes research and checks structure, not guilt. Names, shared addresses, registry entries and outliers are not proof. A qualified human must assess source meaning, context and any legal conclusion.</AccordionContent></AccordionItem>
          <AccordionItem value="data"><AccordionTrigger>Are real investigations or personal records included?</AccordionTrigger><AccordionContent>No. The release contains code, generic methods and synthetic examples. Newly acquired public records can still contain personal information. Store them privately, minimize what you send to models and never post evidence in repository issues.</AccordionContent></AccordionItem>
          <AccordionItem value="official"><AccordionTrigger>Is this an official government project or reporting channel?</AccordionTrigger><AccordionContent>No. This is an independent open-source project. It does not accept fraud tips, file reports or contact subjects. Use current official guidance and obtain appropriate advice before any human-directed reporting decision.</AccordionContent></AccordionItem>
          <AccordionItem value="rewards"><AccordionTrigger>Does using the toolkit qualify me for a reward?</AccordionTrigger><AccordionContent>No reward or commission is promised. Current written agency terms govern eligibility, originality and required milestones. Social-media announcements, structural checks and public anomalies do not establish entitlement. <a href="https://www.justice.gov/fraud/whistleblower">Read current DOJ guidance.</a></AccordionContent></AccordionItem>
          <AccordionItem value="privacy"><AccordionTrigger>Does local storage mean no information leaves my machine?</AccordionTrigger><AccordionContent>No. Your selected model may receive prompts and tool output. Search engines and source websites receive queries or requests. This landing page includes no forms or analytics; GitHub Pages may log hosting requests. <a href={`${REPO}/blob/main/docs/PRIVACY.md`}>Read the full data-flow guide.</a></AccordionContent></AccordionItem>
        </Accordion>
      </div></section>
      <section className="community-section"><div className="shell community-grid"><div><p className="eyebrow">OPEN METHODS, BETTER QUESTIONS</p><h2>Same public interest.<br /><em>Stronger together.</em></h2><p>Contribute a source correction, a better falsification example or a synthetic test. Keep real subjects and identifying evidence out of public contributions.</p><Button asChild variant="outline" size="lg"><a href={`${SOURCE}#help-improve-the-methods`}>Contribute on GitHub <ArrowUpRight aria-hidden="true" /></a></Button></div><img src={`${import.meta.env.BASE_URL}community-duo.webp`} alt="Fictional Nous-inspired character and eagle mascot working together with records and a magnifying glass" width="1254" height="1254" loading="lazy" /></div></section>
    </main>
    <SiteFooter />
    <a href="#method" className="sr-only">Continue to the method <ArrowDown aria-hidden="true" /></a>
  </>;
}

createRoot(document.getElementById('root')!).render(<TooltipProvider delayDuration={250}><App /></TooltipProvider>);
