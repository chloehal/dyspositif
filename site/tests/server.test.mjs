import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createSiteServer} from '../server.mjs';

test('le serveur expose le site et le téléchargement, jamais les sources', async () => {
  const server = createSiteServer(new URL('../../dist/', import.meta.url));
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const origin = `http://127.0.0.1:${server.address().port}`;
  try {
    const page = await fetch(origin);
    assert.equal(page.status, 200);
    const html = await page.text();
    assert.ok(html.indexOf('id="utiliser"') < html.indexOf('id="generateur"'));
    assert.match(html, /href="dyspositif-skill.zip" download/);
    assert.match(html, /Personnaliser → Skills/);
    const js = await fetch(origin + '/app.js');
    assert.equal(js.status, 200);
    assert.match(js.headers.get('content-type'), /javascript/);
    const zip = await fetch(origin + '/dyspositif-skill.zip');
    assert.equal(zip.status, 200);
    assert.match(zip.headers.get('content-disposition'), /attachment/);
    assert.equal(Buffer.from(await zip.arrayBuffer()).subarray(0, 2).toString(), 'PK');
    assert.equal((await fetch(origin, {method:'HEAD'})).status, 200);
    for (const path of ['/package.json','/SKILL.md','/.env','/%2e%2e/package.json','/missing']) assert.equal((await fetch(origin + path)).status, 404);
    assert.equal((await fetch(origin, {method:'POST'})).status, 405);
  } finally { await new Promise(resolve => server.close(resolve)); }
});
