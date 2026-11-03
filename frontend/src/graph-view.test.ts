import {expect, it} from 'vitest';
import graph from './testdata/graph.json';
import {projectGraph} from './graph-view';
it('preserves exact candidate path identities and order',()=>{const f=graph.findings[0];const v=projectGraph(graph,f,'path',f.entry_node_id);expect(v.nodes.map(n=>n.id)).toEqual(f.path_node_ids);expect(v.edges.map(e=>e.id)).toEqual(f.path_edge_ids);});
it('keeps every overview identity deterministically without mutation',()=>{const before=JSON.stringify(graph);const v=projectGraph(graph,undefined,'overview','');expect(v.nodes.map(n=>n.id).sort()).toEqual(graph.nodes.map(n=>n.id).sort());expect(v.edges.map(e=>e.id).sort()).toEqual(graph.edges.map(e=>e.id).sort());expect(v).toEqual(projectGraph(graph,undefined,'overview',''));expect(JSON.stringify(graph)).toBe(before);});
it('noncandidate context follows real HANDLES/CALLS only',()=>{const endpoint=graph.nodes.find(n=>n.name==='GET /protected')!;const v=projectGraph(graph,undefined,'path',endpoint.id);expect(v.nodes[0].id).toBe(endpoint.id);expect(v.nodes.map(n=>n.name)).toContain('export_records');expect(v.edges.every(e=>['HANDLES','CALLS'].includes(e.type))).toBe(true);expect(v.nodes.some(n=>n.name==='authorize_export')).toBe(false);expect(v.edges.every(e=>graph.edges.some(s=>s.id===e.id))).toBe(true);});
it('mobile orientation preserves order and identity',()=>{const f=graph.findings[0];const h=projectGraph(graph,f,'path',f.entry_node_id);const v=projectGraph(graph,f,'path',f.entry_node_id,true);expect(v.nodes.map(n=>n.id)).toEqual(h.nodes.map(n=>n.id));expect(v.positions[v.nodes[1].id].y).toBeGreaterThan(v.positions[v.nodes[0].id].y);expect(h.positions[h.nodes[1].id].x).toBeGreaterThan(h.positions[h.nodes[0].id].x);});
it('does not collapse parallel relationships with distinct stored IDs',()=>{
  const f=graph.findings[0];
  const first=graph.edges.find(e=>e.id===f.path_edge_ids[0])!;
  const parallel={...first,id:'edge:parallel-test'};
  const input={nodes:graph.nodes,edges:[...graph.edges,parallel]};
  const context=projectGraph(input,undefined,'path',f.entry_node_id);
  expect(context.edges.filter(e=>e.source===first.source&&e.target===first.target).map(e=>e.id)).toEqual([first.id,parallel.id]);
  expect(projectGraph(input,undefined,'overview','').edges).toHaveLength(graph.edges.length+1);
});
it('keeps uncertain handler and call edges out of focused paths',()=>{
  const f=graph.findings[0];
  const first=graph.edges.find(e=>e.id===f.path_edge_ids[0])!;
  const call=graph.edges.find(e=>e.id===f.path_edge_ids[1])!;
  const inferred={...first,id:'edge:inferred-test',fact_status:'INFERRED'};
  const unresolved={...call,id:'edge:unresolved-test',fact_status:'UNRESOLVED'};
  const input={nodes:graph.nodes,edges:[...graph.edges,inferred,unresolved]};
  const focused=projectGraph(input,undefined,'path',f.entry_node_id);
  expect(focused.edges.every(e=>e.fact_status==='OBSERVED')).toBe(true);
  expect(focused.edges.map(e=>e.id)).toContain(first.id);
  expect(projectGraph(input,undefined,'overview','').edges).toEqual(input.edges);
});
