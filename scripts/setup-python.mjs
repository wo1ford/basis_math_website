import { copyFile, mkdir } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';

const require = createRequire(import.meta.url);
const pythonPackage = dirname(require.resolve('pyodide/package.json'));
const target = fileURLToPath(new URL('../public/python/', import.meta.url));
const files = ['pyodide.asm.wasm', 'python_stdlib.zip', 'pyodide-lock.json', 'pyodide.mjs', 'pyodide.asm.js'];
await mkdir(target, { recursive: true });
await Promise.all(files.map(name => copyFile(join(pythonPackage, name), join(target, name))));
console.log('Python runtime ready in public/python');
