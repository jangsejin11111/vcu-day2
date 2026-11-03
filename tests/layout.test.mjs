import test from 'node:test';
import assert from 'node:assert/strict';
import {boardPositions} from '../board-layout.mjs';
test('mobile and desktop fill separated slots before overlap, with stable additions',()=>{
 for(const width of [280,320,440,540,680]){
  const height=240,capacity=Math.floor(width/112)*2;
  const initial=boardPositions(capacity,width,height),crowded=boardPositions(50,width,height);
  assert.deepEqual(crowded.slice(0,capacity),initial);
  for(let i=0;i<initial.length;i++)for(let j=0;j<i;j++)assert.ok(Math.abs(initial[i].x-initial[j].x)>=112||Math.abs(initial[i].y-initial[j].y)>=100);
  assert.ok(crowded.every(p=>p.x>=50&&p.x<=width-50&&p.y>=45&&p.y<=height-45));
 }
});
