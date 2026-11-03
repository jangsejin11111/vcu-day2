import {mkdir,readFile,writeFile,readdir} from 'node:fs/promises';
import {randomUUID} from 'node:crypto';
export function diskStore(dir){
 let queue=Promise.resolve();const file=k=>dir+'/'+encodeURIComponent(k)+'.json';
 const getWithMetadata=async k=>{try{return JSON.parse(await readFile(file(k),'utf8'))}catch(e){if(e.code==='ENOENT')return null;throw e}};
 return {getWithMetadata,get:async k=>(await getWithMetadata(k))?.data||null,list:async({prefix})=>{await mkdir(dir,{recursive:true});return {blobs:(await readdir(dir)).filter(n=>n.endsWith('.json')).map(n=>({key:decodeURIComponent(n.slice(0,-5))})).filter(b=>b.key.startsWith(prefix))}},setJSON:(k,data,opts={})=>{const task=queue.then(async()=>{await mkdir(dir,{recursive:true});const old=await getWithMetadata(k);if(opts.onlyIfNew&&old||opts.onlyIfMatch&&old?.etag!==opts.onlyIfMatch)return {modified:false};await writeFile(file(k),JSON.stringify({data,etag:randomUUID()}));return {modified:true}});queue=task.catch(()=>{});return task}};
}
