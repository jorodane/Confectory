// Exact shipped creation handler with an in-memory bridge and no native or account writes.
import assert from 'node:assert/strict';
import fs from 'node:fs';

const source = fs.readFileSync(process.argv[2] + '/examples/editor-home/ui/v508-runtime.js', 'utf8');
const start = 'createProject:async(input,active=()=>true)=>{';
const open = source.indexOf(start);
const close = source.indexOf('},placeHelpers:', open);
assert(open >= 0 && close > open, 'Creation handler missing');
const body = source.slice(open + start.length, close);
const codex = 'Confectory.Agent.Codex::Connection';

async function run({state, selected = [], owner = codex, withoutAI = false, proposalId = null, cancel = false} = {}) {
    const events = [];
    const current = {helperAgents: {agents: owner ? [{id: owner}] : []}};
    const helpers = [{id: 'owned', agentId: owner}];
    const view = {async call(endpoint, args) {
        if (endpoint === 'chatUse') {
            events.push('check');
            assert.equal(args.agent, codex);
            return {state};
        }
        events.push(args.action);
        return {helper: 'owned-default'};
    }};
    const native = {confectoryWebUI: {async createProject(name, description, parent, proposal) {
        events.push('native');
        assert.equal(proposal, proposalId);
        if (cancel) return {ok: true, cancelled: true};
        current.projectId = 'owned-project';
        return {ok: true, result: {projectId: 'owned-project'}};
    }}};
    const create = new Function('globalThis', 'view', 'current', 'helpers', 'recover', 'placeProjectHelpers', 'crypto',
        'chatUseFailure', `return async(input,active=()=>true)=>{${body}}`)(native, view, current, helpers,
        async () => {}, async () => events.push('place'), {randomUUID: () => 'a'.repeat(32)}, () => 'blocked');
    let error;
    try {
        await create({helpers: selected, name: 'Owned', description: '', parent: 'owned', withoutAI, proposalId});
    } catch (failure) { error = failure; }
    return {events, error};
}

let checks = 0;
async function check(options, events, blocked = false) {
    const result = await run(options);
    assert.equal(Boolean(result.error), blocked, JSON.stringify(options));
    assert.deepEqual(result.events, events, JSON.stringify(options));
    checks++;
}

for (const state of ['consent-required', 'blocked', 'not-applicable']) {
    await check({state}, ['check'], true);
    await check({state, withoutAI: true}, ['native']);
    await check({state, withoutAI: true, selected: ['owned']}, ['check'], true);
    await check({state, withoutAI: true, proposalId: 'owned-proposal'}, ['check'], true);
}
await check({state: 'granted'}, ['check', 'native', 'create', 'place']);
await check({state: 'granted', selected: ['owned']}, ['check', 'native', 'place']);
await check({state: 'granted', proposalId: 'owned-proposal'}, ['check', 'native', 'create', 'place']);
await check({selected: ['unknown']}, [], true);
await check({owner: null}, ['native']);
await check({owner: null, proposalId: 'owned-proposal'}, [], true);
await check({state: 'granted', cancel: true}, ['check', 'native']);
await check({withoutAI: true, cancel: true}, ['native']);
console.log(`PASS ${checks} shipped creation admission cases, including local creation and explicit Helper/proposal consent`);
