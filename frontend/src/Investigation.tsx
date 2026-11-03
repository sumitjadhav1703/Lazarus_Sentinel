import {useState} from 'react';
import type {Demo, Item} from './validation';

type Props={demo:Demo; investigation:Item; onSelectNode:(id:string)=>void};

// The graph node a step looked at, so selecting the step can highlight it.
function stepNode(demo:Demo, step:Item):string|undefined {
  if(step.status!=='OK') return undefined;
  const args=step.arguments as Record<string,string>;
  if(args.node_id) return args.node_id;
  if(args.finding_id) return demo.graph.findings.find(f=>f.id===args.finding_id)?.entry_node_id;
  if(args.evidence_id) return demo.graph.nodes.find(n=>n.evidence_ids.includes(args.evidence_id))?.id ?? demo.graph.edges.find(e=>e.evidence_ids.includes(args.evidence_id))?.source;
  return undefined;
}

function outcome(step:Item):string {
  const r=step.result;
  if(step.status!=='OK') return `Tool error: ${r.error}`;
  switch(step.tool){
    case 'get_finding': return r.title;
    case 'get_node': return `${r.type} · ${r.name}`;
    case 'get_neighbors': return `${r.edges.length} recorded relationships`;
    case 'get_evidence': return `${r.file_path}:${r.start_line}–${r.end_line}`;
    case 'list_endpoints': return `${r.endpoints.length} endpoints`;
    default: return `${r.coverage.length} coverage records, ${r.diagnostics.length} diagnostics`;
  }
}

export default function Investigation({demo, investigation:v, onSelectNode}:Props){
  const [active,setActive]=useState(0);
  const live=v.generation==='live';
  const cost=(v.usage.estimated_micro_usd/1e6).toFixed(4);
  return <details className="investigation" open><summary>{live?'Recorded live agent investigation':'Agent investigation · offline mock rehearsal'}</summary>
    <p className="hint">{v.provider} · {v.model} · {v.usage.calls} model calls{live && <> · USD {cost} estimated</>} · UNREVIEWED</p>
    <p className="hint">Investigation notes, not a verdict. Each step is a read-only lookup in the committed graph, replayed by the bundle verifier. Select a step to highlight it.</p>
    <ol className="investigation-steps">{v.steps.map((s:Item)=>{const target=stepNode(demo,s); const text=<><code>{s.tool}</code> <span>{outcome(s)}</span></>;
      return <li key={s.index}>{target ? <button aria-pressed={active===s.index} onClick={()=>{setActive(s.index); onSelectNode(target);}}>{text}</button> : <div className={s.status==='OK'?'step-static':'step-static step-error'}>{text}</div>}</li>;})}
      <li><div className="step-static"><code>submit_investigation</code> <span>Final notes below</span></div></li></ol>
    <h4>Summary</h4><p>{v.response.summary}</p>
    <h4>Why it matters</h4><p>{v.response.why_it_matters}</p>
    <h4>Reviewer checklist</h4><ul>{v.response.reviewer_checklist.map((x:string)=><li key={x}>{x}</li>)}</ul>
    <h4>Limitations</h4><ul>{v.response.limitations.map((x:string)=><li key={x}>{x}</li>)}</ul>
    <h4>Cited evidence</h4><ul>{Array.from(new Set<string>(v.response.evidence_ids.map((id:string)=>{const e=demo.graph.evidence.find(x=>x.id===id); return e ? `${e.file_path}:${e.start_line}–${e.end_line}` : id;}))).map(x=><li key={x}>{x}</li>)}</ul>
  </details>;
}
