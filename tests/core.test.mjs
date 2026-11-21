import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const html = fs.readFileSync(path.join(here, '..', 'index.html'), 'utf8');
const match = html.match(/<script id="core-logic">([\s\S]*?)<\/script>/);
assert.ok(match, 'index.html must contain pure core logic');
const context = {};
vm.createContext(context);
vm.runInContext(`${match[1]}; globalThis.RadarCore = RadarCore;`, context);
const core = context.RadarCore;

const opportunity = {
  id: 'opp-1', name: 'Example', source: { label: 'Official repo', url: 'https://github.com/example/example' },
  signal: 'A verifiable public signal.', hypothesis: 'A hypothesis to validate.', buyer: 'Operations lead',
  nextAction: 'Interview one builder.', status: 'pending', scores: { signal: 4, fit: 5, timing: 3, access: 2 }
};
const growth = {
  id: 'growth-1', lesson: 'Write testable constraints.', project: 'Radar automation',
  conversation: '2026-11-18 17:30 / prompt revision', evidence: 'A revised prompt was executed.',
  businessLink: 'Better report acceptance criteria.', nextExperiment: 'Apply a zero-diff check next week.'
};

test('normalizeConfig keeps a custom identity and clamps card limit', () => {
  const config = core.normalizeConfig({ name: '  API商机雷达  ', focus: ' AI API ', period: '本周', maxCards: 99 });
  assert.equal(config.name, 'API商机雷达');
  assert.equal(config.focus, 'AI API');
  assert.equal(config.maxCards, 10);
  assert.equal(core.normalizeConfig({}).name, 'AI 商机雷达');
});

test('opportunity validation requires evidence and a next action', () => {
  assert.deepEqual(Array.from(core.validateOpportunity(opportunity)), []);
  assert.ok(core.validateOpportunity({ ...opportunity, hypothesis: '' }).includes('hypothesis'));
  assert.ok(core.validateOpportunity({ ...opportunity, source: { url: 'http://unsafe.test' } }).includes('source.url'));
});

test('growth validation requires traceability and rejects raw transcripts', () => {
  assert.deepEqual(Array.from(core.validateGrowth(growth)), []);
  assert.ok(core.validateGrowth({ ...growth, project: '' }).includes('project'));
  assert.ok(core.validateGrowth({ ...growth, rawTranscript: 'private chat' }).includes('rawTranscript'));
});

test('score is deterministic and archived signals are held', () => {
  assert.equal(core.scoreOpportunity(opportunity), 70);
  const archived = { ...opportunity, archived: true };
  assert.equal(core.reviewSuggestion(archived), 'hold');
});

test('status transitions never invent a commercial result', () => {
  const next = core.setReviewStatus(opportunity, 'follow');
  assert.equal(next.status, 'follow');
  assert.equal(opportunity.status, 'pending');
  assert.throws(() => core.setReviewStatus(opportunity, 'closed-won'));
});

test('summary counts review states', () => {
  const summary = core.summarize([opportunity, { ...opportunity, id: '2', status: 'follow' }, { ...opportunity, id: '3', status: 'hold' }]);
  assert.deepEqual({ ...summary }, { total: 3, pending: 1, follow: 1, hold: 1 });
});

test('markdown keeps sources, review status, growth evidence and disclaimer', () => {
  const md = core.buildMarkdown(core.normalizeConfig({ name: 'API商机雷达', period: '2026.11' }), [{ ...opportunity, status: 'follow' }], [growth]);
  assert.match(md, /# API商机雷达/);
  assert.match(md, /https:\/\/github.com\/example\/example/);
  assert.match(md, /进入跟进/);
  assert.match(md, /人的成长/);
  assert.match(md, /Radar automation/);
  assert.match(md, /假设待人工验证/);
});

test('HTML escaping protects user-configurable content', () => {
  assert.equal(core.escapeHtml('<img src=x onerror=alert(1)>'), '&lt;img src=x onerror=alert(1)&gt;');
});
