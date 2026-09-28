import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';

test('la publication statique contient la page, ses assets et la skill complète', async () => {
  const output = new URL('../../dist/', import.meta.url);
  const html = await readFile(new URL('index.html', output), 'utf8');
  assert.ok(html.indexOf('id="utiliser"') >= 0);
  assert.ok(html.indexOf('id="utiliser"') < html.indexOf('id="generateur"'));
  assert.match(html, /href="dyspositif-skill.zip" download/);
  assert.match(html, /Personnaliser → Skills/);
  const assets = [...html.matchAll(/(?:src|href)="(\.\/assets\/[^"?]+)"/g)].map(m => m[1]);
  assert.ok(assets.some(name => name.endsWith('.js')));
  assert.ok(assets.some(name => name.endsWith('.css')));
  for (const asset of assets) assert.ok((await readFile(new URL(asset, output))).length > 0);
  assert.deepEqual(await readFile(new URL('dyspositif-skill.zip', output)),
    await readFile(new URL('../public/dyspositif-skill.zip', import.meta.url)));
  assert.deepEqual((await readdir(output)).sort(), ['assets', 'dyspositif-skill.zip', 'index.html']);
});
