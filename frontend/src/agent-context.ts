const VERSION = 'repository-context/1.0';
const MAX_GRAPH = 16 * 1024 * 1024;
const MAX_MANIFEST = 16 * 1024;
const MAX_RESULT = 64 * 1024;
const SHA256 = /^[0-9a-f]{64}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;

type FileRecord = {path:string; sha256:string; language:string};
type Span = {path:string; start_line:number; end_line:number};
type Entity = Span & {id:string; kind:string; name:string};
type Relationship = Span & {id:string; kind:string; source:string; target:string; status:string};
type Coverage = {path:string; capability:string; status:string};
type Unknown = {path:string; start_line:number; kind:string};
type ContextGraph = {
  files:FileRecord[]; entities:Entity[]; relationships:Relationship[]; coverage:Coverage[]; unknowns:Unknown[];
};
export type RepositoryContext = {snapshot_id:string; revision:string; graph:ContextGraph};

const record = (x:unknown): x is Record<string,unknown> => typeof x==='object' && x!==null && !Array.isArray(x);
const text = (x:unknown): x is string => typeof x==='string' && x.length>0 && (x.length<=512 || (x.length<=1024 && [...x].length<=512));
const keys = (x:Record<string,unknown>, expected:string) => Object.keys(x).sort().join(',')===expected;
const sha = (x:unknown): x is string => text(x) && SHA256.test(x);
const line = (x:unknown): x is number => typeof x==='number' && Number.isSafeInteger(x) && x>0;
// eslint-disable-next-line no-control-regex -- Reject control characters in repository paths.
const path = (x:unknown): x is string => text(x) && !/[\\:\x00-\x1f]/.test(x) && x.split('/').every(p=>p && p!=='.' && p!=='..');
const span = (x:Record<string,unknown>) => line(x.start_line) && line(x.end_line) && x.start_line<=x.end_line;
const parse = (bytes:ArrayBuffer):unknown => JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
function rows<T>(data:unknown, limit:number, fields:string, validate:(x:Record<string,unknown>)=>boolean):T[] {
  if(!Array.isArray(data) || data.length>limit || !data.every(x=>record(x) && keys(x,fields) && validate(x))) throw new Error('Invalid context records');
  return data as T[];
}
function unique(values:string[]) {
  if(new Set(values).size!==values.length) throw new Error('Duplicate context identity');
}
function artifact(x:unknown):x is {size:number;sha256:string} {
  return record(x) && keys(x,'sha256,size') && line(x.size) && x.size<=MAX_GRAPH && sha(x.sha256);
}

export async function loadRepositoryContext(manifestFile:File, graphFile:File):Promise<RepositoryContext> {
  if(manifestFile.size>MAX_MANIFEST || graphFile.size>MAX_GRAPH) throw new Error('Context files exceed size limits');
  const manifest=parse(await manifestFile.arrayBuffer());
  if(!record(manifest) || !keys(manifest,'artifacts,git_commit,revision,schema_version,snapshot_id') ||
    !text(manifest.git_commit) || !/^[0-9a-f]{40,64}$/.test(manifest.git_commit) || manifest.schema_version!==VERSION || !text(manifest.snapshot_id) ||
    !UUID.test(manifest.snapshot_id) || !sha(manifest.revision) || !record(manifest.artifacts) ||
    Object.keys(manifest.artifacts).sort().join(',')!=='graph.json,schema.json' ||
    !artifact(manifest.artifacts['graph.json']) || !artifact(manifest.artifacts['schema.json'])) {
    throw new Error('Invalid context manifest');
  }
  const expected=manifest.artifacts['graph.json'];
  if(graphFile.size!==expected.size) throw new Error('Context graph size does not match the manifest');
  const bytes=await graphFile.arrayBuffer();
  const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
  if(digest!==expected.sha256 || digest!==manifest.revision) throw new Error('Context graph hash does not match the manifest');
  const raw=parse(bytes);
  if(!record(raw) || !keys(raw,'coverage,entities,files,relationships,unknowns')) throw new Error('Invalid context graph');
  const files=rows<FileRecord>(raw.files,500,'language,path,sha256',x=>path(x.path) && sha(x.sha256) && text(x.language));
  if(!files.length) throw new Error('Missing context file records');
  unique(files.map(f=>f.path));
  const paths=new Set(files.map(f=>f.path));
  const hasPath=(x:unknown) => path(x) && paths.has(x);
  const entities=rows<Entity>(raw.entities,25000,'end_line,id,kind,name,path,start_line',x=>text(x.id) &&
    ['FILE','MODULE','DEFINITION'].some(kind=>kind===x.kind) && text(x.name) && hasPath(x.path) && span(x));
  const entityIds=new Set(entities.map(e=>e.id));
  const relationships=rows<Relationship>(raw.relationships,100000,'end_line,id,kind,path,source,start_line,status,target',x=>text(x.id) &&
    ['CONTAINS','IMPORTS','CALLS'].some(kind=>kind===x.kind) &&
    ['OBSERVED','INFERRED','UNKNOWN','UNRESOLVED'].some(status=>status===x.status) &&
    text(x.source) && text(x.target) && entityIds.has(x.source) && entityIds.has(x.target) && hasPath(x.path) && span(x));
  unique([...entities,...relationships].map(x=>x.id));
  const coverage=rows<Coverage>(raw.coverage,5000,'capability,path,status',x=>hasPath(x.path) && text(x.capability) && text(x.status));
  const unknowns=rows<Unknown>(raw.unknowns,100000,'kind,path,start_line',x=>hasPath(x.path) && line(x.start_line) && text(x.kind));
  return {snapshot_id:manifest.snapshot_id,revision:manifest.revision,graph:{files,entities,relationships,coverage,unknowns}};
}

export function entityContext(context:RepositoryContext,id:string) {
  const entity=context.graph.entities.find(e=>e.id===id);
  if(!entity) throw new Error('Unknown entity ID');
  const file=context.graph.files.find(f=>f.path===entity.path)!;
  const result={
    schema_version:VERSION,
    snapshot_id:context.snapshot_id,
    revision:context.revision,
    operation:'entity',
    records:[{...entity,file_sha256:file.sha256}],
    coverage:context.graph.coverage.filter(c=>c.path===file.path),
    next_cursor:null,
  };
  // Match the ASCII JSON byte budget of the backend query.
  const ascii=JSON.stringify(result).replace(/[^ -~]/g,c=>`\\u${c.charCodeAt(0).toString(16).padStart(4,'0')}`);
  if(ascii.length>MAX_RESULT) throw new Error('Context entity result exceeds query size limits');
  return result;
}
