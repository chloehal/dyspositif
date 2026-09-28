import {defineConfig} from 'vite';
import {fileURLToPath} from 'node:url';

export default defineConfig({
  root: fileURLToPath(new URL('./site/dist/', import.meta.url)),
  publicDir: fileURLToPath(new URL('./site/public/', import.meta.url)),
  base: './',
  build: {
    outDir: fileURLToPath(new URL('./dist/', import.meta.url)),
    emptyOutDir: true,
  },
});
