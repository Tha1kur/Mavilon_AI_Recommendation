// Execute the real TypeScript API wrapper with isolated HTTP/storage boundaries.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const ts = require('typescript');
const path = require('node:path');

const source = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../../lib/api/user.ts'), 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
}).outputText;
const key = 'mavilon_session_id';
function wrapper(client, stored) {
    const values = new Map(stored ? [[key, stored]] : []);
    const exports = {};
    const localStorage = {
        getItem: k => values.get(k) ?? null,
        setItem: (k, v) => values.set(k, v),
        removeItem: k => values.delete(k),
    };
    vm.runInNewContext(source, {
        exports, localStorage, console,
        require: name => {
            if (name === './client') return { default: client };
            if (name === 'axios') return { isAxiosError: e => e.isAxiosError === true };
            throw new Error(`Unexpected dependency: ${name}`);
        },
    });
    return { api: exports, values };
}
const response = id => ({ data: { session_id: id, user_id: 'test-user', is_new: false } });
const failure = status => Object.assign(new Error('private request data'), {
    isAxiosError: true, response: status ? { status } : undefined,
});

test('return sends JSON only and stores/uses the authoritative response', async () => {
    const calls = [];
    const { api, values } = wrapper({ post: async (...args) => { calls.push(args); return response('returned-id'); } }, 'stored-id');
    assert.equal(await api.getOrCreateSession(), 'returned-id');
    assert.equal(values.get(key), 'returned-id');
    assert.equal(calls.length, 1);
    assert.equal(calls[0][0], '/api/users/session');
    assert.equal(JSON.stringify(calls[0][1]), '{"session_id":"stored-id"}');
});

test('concurrent new-session requests share one server identity', async () => {
    let calls = 0;
    const { api, values } = wrapper({ post: async (url, body) => {
        calls++;
        assert.equal(url, '/api/users/session');
        assert.equal(body, undefined);
        return response('new-id');
    } });
    assert.deepEqual(await Promise.all([api.getOrCreateSession(), api.getOrCreateSession(), api.getOrCreateSession()]), ['new-id', 'new-id', 'new-id']);
    assert.equal(calls, 1);
    assert.equal(values.get(key), 'new-id');
});

for (const status of [404, 422]) {
    test(`invalid identity (${status}) is replaced using a new-session request`, async () => {
        const calls = [];
        const { api, values } = wrapper({ post: async (...args) => {
            calls.push(args);
            if (calls.length === 1) throw failure(status);
            return response('replacement');
        } }, 'invalid-id');
        assert.equal(await api.getOrCreateSession(), 'replacement');
        assert.equal(calls.length, 2);
        assert.equal(calls[1][1], undefined);
        assert.equal(values.get(key), 'replacement');
    });
}

for (const status of [undefined, 500, 503, 403]) {
    test(`session failure (${status}) preserves identity and permits retry`, async () => {
        let calls = 0;
        const { api, values } = wrapper({ post: async () => {
            calls++;
            if (calls === 1) throw failure(status);
            return response('existing');
        } }, 'existing');
        await assert.rejects(api.getOrCreateSession(), { message: 'Unable to establish session' });
        assert.equal(values.get(key), 'existing');
        assert.equal(calls, 1);
        assert.equal(await api.getOrCreateSession(), 'existing');
    });
}

test('failed new session does not invent a local identity', async () => {
    const { api, values } = wrapper({ post: async () => { throw failure(500); } });
    await assert.rejects(api.getOrCreateSession(), { message: 'Unable to establish session' });
    assert.equal(values.has(key), false);
});

test('profile preserves score maps and uses the returned session', async () => {
    const profile = { favorite_genres: { Drama: 1.95 }, favorite_moods: { Calm: 0.5 }, interaction_count: 2 };
    const { api } = wrapper({
        post: async () => response('confirmed'),
        get: async url => { assert.equal(url, '/api/users/confirmed/profile'); return { data: profile }; },
    }, 'stored');
    assert.deepEqual(await api.getUserProfile(), profile);
});

test('failed profile rejects instead of returning a fabricated empty profile', async () => {
    const { api } = wrapper({
        post: async () => response('confirmed'),
        get: async () => { throw failure(500); },
    }, 'stored');
    await assert.rejects(api.getUserProfile(), { message: 'Unable to load taste profile' });
});

test('session validation failures never print identity-bearing response data', async () => {
    const clientSource = ts.transpileModule(fs.readFileSync(path.join(__dirname, '../../lib/api/client.ts'), 'utf8'), {
        compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
    }).outputText;
    let rejectResponse;
    const logged = [];
    const mockClient = { interceptors: { response: { use: (_, reject) => { rejectResponse = reject; } } } };
    vm.runInNewContext(clientSource, {
        exports: {}, process: { env: {} },
        console: { error: (...args) => logged.push(args) },
        require: name => {
            assert.equal(name, 'axios');
            return { default: { create: () => mockClient } };
        },
    });
    const error = { config: { url: '/api/users/session' }, response: {
        status: 422, data: { detail: [{ input: 'private-test-session' }] },
    } };
    await assert.rejects(rejectResponse(error), e => e === error);
    assert.equal(JSON.stringify(logged), '[["API Error:","Session request failed"]]');
});
