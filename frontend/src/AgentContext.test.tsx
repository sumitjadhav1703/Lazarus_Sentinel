// @vitest-environment jsdom
import {webcrypto} from 'node:crypto';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, expect, it, vi} from 'vitest';
import AgentContext from './AgentContext';

afterEach(()=>{cleanup();vi.unstubAllGlobals();});

function file(name:string,value:unknown) {
  const bytes=new TextEncoder().encode(JSON.stringify(value));
  return {name,size:bytes.byteLength,arrayBuffer:async()=>bytes.buffer} as File;
}

it('inspects a local entity and clears it when another selection cannot be verified',async()=>{
  vi.stubGlobal('crypto',webcrypto);
  const path='scripts/example.py';
  const entity={id:'entity:one',kind:'DEFINITION',name:'build',path,start_line:1,end_line:2};
  const coverage=[{path,capability:'AST',status:'PARTIAL'}];
  const hash='a'.repeat(64);
  const graph=file('graph.json',{
    files:[{path,sha256:hash,language:'python'}],entities:[entity],
    relationships:[],coverage,unknowns:[{path,start_line:2,kind:'UNRESOLVED_CALL'}],
  });
  const revision=Buffer.from(await webcrypto.subtle.digest('SHA-256',await graph.arrayBuffer())).toString('hex');
  const snapshot_id='37a8b240-2f8c-48fa-aa9d-992fa13ae517';
  const manifest=file('manifest.json',{
    schema_version:'repository-context/1.0',snapshot_id,revision,git_commit:'b'.repeat(40),
    artifacts:{'graph.json':{size:graph.size,sha256:revision},'schema.json':{size:1,sha256:hash}},
  });
  render(<AgentContext/>);
  fireEvent.click(screen.getByText('Agent Context'));
  const picker=screen.getByLabelText('Select manifest.json and graph.json together');
  fireEvent.change(picker,{target:{files:[manifest,graph]}});
  await screen.findByRole('heading',{name:'build'});
  expect(screen.getByText('UNRESOLVED_CALL · line 2')).toBeTruthy();
  expect(JSON.parse(screen.getByLabelText('Agent entity JSON').textContent!)).toEqual({
    schema_version:'repository-context/1.0',snapshot_id,revision,operation:'entity',
    records:[{...entity,file_sha256:hash}],coverage,next_cursor:null,
  });
  fireEvent.change(picker,{target:{files:[manifest,file('graph.json',{})]}});
  expect(await screen.findByRole('alert')).toBeTruthy();
  expect(screen.queryByRole('heading',{name:'build'})).toBeNull();
  expect(screen.queryByRole('button',{name:'Copy entity JSON'})).toBeNull();
});
