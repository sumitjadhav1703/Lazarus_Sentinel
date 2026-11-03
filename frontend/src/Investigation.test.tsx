// @vitest-environment jsdom
import React from 'react';
import {afterEach, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import graph from './testdata/graph.json';
import record from './testdata/investigation.json';
import Investigation from './Investigation';
import type {Demo, Item} from './validation';

afterEach(cleanup);
const demo={graph} as unknown as Demo;
const investigation=record as unknown as Item;

it('replays steps in order and selecting a step highlights its node',()=>{
  const select=vi.fn();
  render(<Investigation demo={demo} investigation={investigation} onSelectNode={select}/>);
  expect(screen.getByText('Agent investigation · offline mock rehearsal')).toBeTruthy();
  expect(screen.getByText(/6 model calls/)).toBeTruthy();
  const steps=screen.getAllByRole('listitem').filter(li=>li.closest('ol'));
  expect(steps.map(li=>li.querySelector('code')?.textContent)).toEqual(['get_finding','get_node','get_neighbors','get_evidence','get_node','submit_investigation']);
  const step=screen.getByRole('button',{name:/get_node/});
  fireEvent.click(step);
  expect(select).toHaveBeenCalledWith(investigation.steps[1].arguments.node_id);
  expect(step.getAttribute('aria-pressed')).toBe('true');
  expect(screen.getByRole('button',{name:/get_finding/}).getAttribute('aria-pressed')).toBe('false');
  expect(screen.getByText('Tool error: UNKNOWN_ID')).toBeTruthy();
  expect(screen.getByText('Confirm runtime authorization for this route.')).toBeTruthy();
  expect(screen.queryByText(/USD/)).toBeNull();
});

it('labels a live record with its model and estimated cost',()=>{
  const live={...investigation,provider:'meta',model:'muse-spark-1.3',generation:'live',usage:{...investigation.usage,estimated_micro_usd:42000}};
  render(<Investigation demo={demo} investigation={live} onSelectNode={()=>{}}/>);
  expect(screen.getByText('Recorded live agent investigation')).toBeTruthy();
  expect(screen.getByText(/muse-spark-1.3 · 6 model calls · USD 0.0420 estimated · UNREVIEWED/)).toBeTruthy();
});
