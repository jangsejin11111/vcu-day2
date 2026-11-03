import http from 'node:http';
import {createServer} from 'vite';
import {handler} from './api.mjs';
import {diskStore} from './disk.mjs';
try { process.loadEnvFile('.env'); } catch(e) { if(e.code!=='ENOENT') throw e; }
const env={...process.env,VCU_ADMIN_PASSWORD:process.env.VCU_ADMIN_PASSWORD||'local-preview-only',VCU_AUTH_SECRET:process.env.VCU_AUTH_SECRET||'local-only-development-secret-32-characters'};
const api=handler(diskStore('.data'),env),vite=await createServer({server:{middlewareMode:true},appType:'spa'});
http.createServer(async(req,res)=>{if(req.url.startsWith('/api/')){try{let body='';for await(const chunk of req){body+=chunk;if(body.length>2000000){res.writeHead(413).end();return}}const response=await api(new Request('http://'+req.headers.host+req.url,{method:req.method,headers:req.headers,...(req.method!=='GET'?{body}: {})}));res.writeHead(response.status,Object.fromEntries(response.headers));res.end(await response.text())}catch{res.writeHead(500).end('Server error')}}else vite.middlewares(req,res)}).listen(5174,'0.0.0.0',()=>console.log('Local: http://localhost:5174'));
