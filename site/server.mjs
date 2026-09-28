import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
const types = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/index.html', ['index.html', 'text/html; charset=utf-8']],
  ['/styles.css', ['styles.css', 'text/css; charset=utf-8']],
  ['/app.js', ['app.js', 'text/javascript; charset=utf-8']],
  ['/puzzle.js', ['puzzle.js', 'text/javascript; charset=utf-8']],
  ['/dyspositif-skill.zip', ['dyspositif-skill.zip', 'application/zip']]
]);
export function createSiteServer(directory = new URL('../dist/', import.meta.url)) {
  return createServer(async (req, res) => {
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.writeHead(405, {Allow: 'GET, HEAD'}).end(); return;
    }
    // Une liste de fichiers publics empêche de servir les sources ou des secrets.
    const entry = types.get((req.url || '/').split('?')[0]);
    if (!entry) { res.writeHead(404).end('Page introuvable'); return; }
    try {
      const content = await readFile(new URL(entry[0], directory));
      const headers = {'Content-Type': entry[1], 'Content-Length': content.length,
        'X-Content-Type-Options': 'nosniff', 'Cache-Control': 'no-cache'};
      if (entry[0].endsWith('.zip')) headers['Content-Disposition'] = 'attachment; filename="dyspositif-skill.zip"';
      res.writeHead(200, headers).end(req.method === 'HEAD' ? undefined : content);
    } catch { res.writeHead(503).end('Site indisponible. Exécuter npm run build.'); }
  });
}
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const port = Number(process.env.PORT || 3000);
  if (!Number.isInteger(port) || port < 0 || port > 65535) throw new Error('PORT invalide');
  const folder = process.argv.includes('--dev') ? new URL('./dist/', import.meta.url) : undefined;
  createSiteServer(folder).listen(port, process.env.HOST || '0.0.0.0', () => console.log(`dyspositif écoute sur le port ${port}`));
}
