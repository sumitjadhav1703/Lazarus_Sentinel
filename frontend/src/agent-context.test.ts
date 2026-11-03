import {webcrypto} from 'node:crypto';
import {afterEach, beforeEach, expect, it, vi} from 'vitest';
import {entityContext, loadRepositoryContext} from './agent-context';

const id='4ef5ba94-9222-4f9e-a243-f057774a2846';
const hash='b'.repeat(64);
const src='backend/src/example.py';
const entity={id:'function:one',kind:'DEFINITION',name:'one',path:src,start_line:2,end_line:4};
const coverage=[{path:src,capability:'CALLS',status:'PARTIAL'}];
const graph={
  files:[{path:src,sha256:hash,language:'python'}],
  entities:[entity],
  relationships:[],
  coverage,
  unknowns:[{path:src,start_line:3,kind:'UNRESOLVED_CALL'}],
};
function file(name:string,value:unknown) {
  const data=new TextEncoder().encode(JSON.stringify(value));
  return {name,size:data.byteLength,arrayBuffer:async()=>data.buffer} as File;
}
async function files(data:unknown) {
  const content=file('graph.json',data);
  const bytes=await content.arrayBuffer();
  const sha256=Buffer.from(await webcrypto.subtle.digest('SHA-256',bytes)).toString('hex');
  const manifest=file('manifest.json',{
    schema_version:'repository-context/1.0',snapshot_id:id,revision:sha256,git_commit:'a'.repeat(40),
    artifacts:{'graph.json':{size:content.size,sha256},'schema.json':{size:1,sha256:hash}},
  });
  return [manifest,content] as const;
}
beforeEach(()=>vi.stubGlobal('crypto',webcrypto));
afterEach(()=>vi.unstubAllGlobals());

it('produces the exact agent entity query fields from a verified export',async()=>{
  const context=await loadRepositoryContext(...await files(graph));
  expect(entityContext(context,entity.id)).toEqual({
    schema_version:'repository-context/1.0',snapshot_id:id,revision:context.revision,operation:'entity',
    records:[{...entity,file_sha256:hash}],coverage,next_cursor:null,
  });
});

it('rejects corrupted bytes even when the file size matches',async()=>{
  const [manifest,content]=await files(graph);
  const corrupt=file('graph.json',{...graph,entities:[{...entity,name:'two'}]});
  expect(corrupt.size).toBe(content.size);
  await expect(loadRepositoryContext(manifest,corrupt)).rejects.toThrow('hash');
});

it('rejects rehashed dangling relationship references',async()=>{
  const input={...graph,relationships:[{id:'edge:one',kind:'CALLS',status:'OBSERVED',
    source:entity.id,target:'missing',path:src,start_line:2,end_line:2}]};
  await expect(loadRepositoryContext(...await files(input))).rejects.toThrow('records');
});

it('rejects oversized local files before reading them',async()=>{
  const [manifest]=await files(graph);
  const read=vi.fn();
  const oversized={size:16*1024*1024+1,arrayBuffer:read} as unknown as File;
  await expect(loadRepositoryContext(manifest,oversized)).rejects.toThrow('limits');
  expect(read).not.toHaveBeenCalled();
});
