import {useRef, useState} from 'react';
import {entityContext, loadRepositoryContext, type RepositoryContext} from './agent-context';

export default function AgentContext() {
  const [context,setContext]=useState<RepositoryContext>();
  const [selected,setSelected]=useState('');
  const [search,setSearch]=useState('');
  const [status,setStatus]=useState('');
  const [error,setError]=useState('');
  const request=useRef(0);
  async function load(files:FileList|null) {
    const id=++request.current;
    setContext(undefined);setSelected('');setSearch('');setError('');setStatus('');
    const chosen=Array.from(files??[]);
    if(!chosen.length) return;
    const manifest=chosen.find(f=>f.name==='manifest.json');
    const graph=chosen.find(f=>f.name==='graph.json');
    if(chosen.length!==2 || !manifest || !graph) {
      setError('Select manifest.json and graph.json from the same context export.');
      return;
    }
    setStatus('Verifying context files…');
    try {
      const result=await loadRepositoryContext(manifest,graph);
      if(id!==request.current) return;
      setContext(result);setSelected(result.graph.entities[0]?.id??'');setStatus('Context verified.');
    } catch {
      if(id!==request.current) return;
      setError('The context export could not be verified. Check the files, limits, and browser support.');setStatus('');
    }
  }

  const entity=context?.graph.entities.find(e=>e.id===selected);
  const matches=context?.graph.entities.filter(e=>`${e.name} ${e.path}`.toLowerCase().includes(search.toLowerCase()))??[];
  const relationships=context?.graph.relationships.filter(e=>e.source===selected || e.target===selected)??[];
  const unknowns=context?.graph.unknowns.filter(x=>x.path===entity?.path)??[];
  const names=new Map(context?.graph.entities.map(e=>[e.id,e.name]));
  let json='';
  if(context && entity) {
    try {
      json=JSON.stringify(entityContext(context,entity.id),null,2);
    } catch {
      // A verified graph can contain an entity whose projection exceeds the query cap.
    }
  }
  async function copy() {
    try {
      await navigator.clipboard.writeText(json);
      setStatus('Entity result copied.');
    } catch {
      setStatus('Clipboard unavailable. Select and copy the JSON below.');
    }
  }

  return <details className="below panel agent-context">
    <summary>Agent Context</summary>
    <p className="hint">Inspect the repository context an agent receives. Files stay in this browser.</p>
    <label htmlFor="agent-context-files">Select manifest.json and graph.json together</label>
    <input id="agent-context-files" type="file" accept=".json,application/json" multiple onChange={e=>{void load(e.currentTarget.files);}}/>
    {error && <p role="alert">{error}</p>}
    <p role="status">{status}</p>
    {context && <>
      <p>Snapshot <code>{context.snapshot_id}</code><br/>Revision <code>{context.revision}</code></p>
      <p>{context.graph.entities.length} entities · {context.graph.relationships.length} relationships · {context.graph.unknowns.length} unknowns</p>
      <label htmlFor="agent-context-search">Filter entities by name or file</label>
      <input id="agent-context-search" value={search} onChange={e=>setSearch(e.target.value)}/>
      <label htmlFor="agent-context-entity">Inspect entity</label>
      <select id="agent-context-entity" value={matches.slice(0,100).some(e=>e.id===selected)?selected:''} onChange={e=>setSelected(e.target.value)}>
        <option value="">Choose an entity</option>
        {matches.slice(0,100).map(e=><option key={e.id} value={e.id}>{e.name} · {e.path}:{e.start_line}</option>)}
      </select>
      {matches.length>100 && <p className="hint">Showing the first 100 matches. Narrow the filter for more.</p>}
      {entity && <>
        <h3>{entity.name}</h3>
        <p>{entity.kind} · <code>{entity.path}:{entity.start_line}–{entity.end_line}</code></p>
        <h3>Relationships</h3>
        {relationships.length===0 ? <p>No recorded relationships.</p>:<ul>{relationships.slice(0,100).map(e=>{
          const adjacent=e.source===selected?e.target:e.source;
          return <li key={e.id}><strong>{e.kind} · {e.status}</strong> · {e.source===selected?'Outgoing':'Incoming'} · <button type="button" onClick={()=>{setSearch('');setSelected(adjacent);}}>{names.get(adjacent)}</button> · <code>{e.path}:{e.start_line}</code></li>;
        })}</ul>}
        {relationships.length>100 && <p className="hint">Showing 100 of {relationships.length} relationships.</p>}
        <h3>Coverage and unknowns</h3>
        <ul>{context.graph.coverage.filter(c=>c.path===entity.path).map((c,i)=><li key={i}>{c.capability}: {c.status}</li>)}</ul>
        {unknowns.length>0 && <ul>{unknowns.slice(0,100).map((x,i)=><li key={i}>{x.kind} · line {x.start_line}</li>)}</ul>}
        <h3>Agent entity result</h3>
        {json ? <>
          <button type="button" onClick={()=>{void copy();}}>Copy entity JSON</button>
          <pre tabIndex={0} aria-label="Agent entity JSON">{json}</pre>
        </>:<p>The entity result exceeds the query size limit.</p>}
      </>}
    </>}
  </details>;
}
