import {cp, mkdir} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
const source = new URL('./dist/', import.meta.url);
const target = new URL('../dist/', import.meta.url);
await mkdir(target, {recursive: true});
for (const name of ['index.html','styles.css','app.js','puzzle.js','dyspositif-skill.zip']) {
  await cp(new URL(name, source), new URL(name, target));
}
console.log(`Site prêt : ${fileURLToPath(target)}`);
