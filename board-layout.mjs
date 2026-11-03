// Fixed footprints include the nickname circle, emotion label and rotation margin.
export function boardPositions(count,width,height){
 const cols=Math.max(1,Math.floor(width/112)),rows=Math.max(1,Math.floor(height/100));
 const points=[],available=[];
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++)available.push({x:(c+.5)*width/cols,y:(r+.5)*height/rows});
 const distance=p=>points.length?Math.min(...points.map(q=>(p.x-q.x)**2+(p.y-q.y)**2)):-((p.x-width/2)**2+(p.y-height/2)**2);
 while(points.length<count){
  // Exhaust all non-overlapping cells before using denser, overlapping positions.
  if(!available.length){
   const layer=Math.floor(points.length/(cols*rows))+1;
   for(let r=0;r<rows*layer;r++)for(let c=0;c<cols*layer;c++){
    const p={x:56+(width-112)*(c+.5)/(cols*layer),y:50+(height-100)*(r+.5)/(rows*layer)};
    if(!points.some(q=>Math.abs(q.x-p.x)<1&&Math.abs(q.y-p.y)<1))available.push(p);
   }
  }
  let best=0;for(let i=1;i<available.length;i++)if(distance(available[i])>distance(available[best]))best=i;
  points.push(available.splice(best,1)[0]);
 }
 return points;
}
