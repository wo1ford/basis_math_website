import { loadPyodide } from './python/pyodide.mjs';
let runtime;
self.onmessage=async e=>{try{if(!runtime){self.postMessage({loading:true});runtime=await loadPyodide({indexURL:new URL('./python/',import.meta.url).href});}const source=await(await fetch('./solver.py')).text();runtime.globals.set('input_json',JSON.stringify(e.data));await runtime.runPythonAsync(source);self.postMessage({result:JSON.parse(runtime.globals.get('result_json'))});}catch(e){self.postMessage({error:e.message});}};
