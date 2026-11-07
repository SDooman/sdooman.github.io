// Compare recovered scene SVG against the independent source SVG at one scale.
const fs=require('node:fs'),path=require('node:path'),{createRequire}=require('node:module');
const sharp=createRequire(process.env.SISLEY_NODE_PACKAGES+'/package.json')('sharp');
const root=path.resolve(__dirname,'../..');
(async()=>{for(const b of ['41-58','59-80','81-100','101-119']){
 const book=path.join(root,'gat-'+b);const inv=JSON.parse(fs.readFileSync(path.join(book,'media-inventory.json')));const report=[];
 for(const a of inv.assets.filter(a=>a.conversion.kind==='vector-scene')){
  const files=['source-svg','vectors'].map(folder=>path.join(book,'assets',folder,a.id+'.svg'));
  const rasters=await Promise.all(files.map(f=>{
   let svg=fs.readFileSync(f,'utf8');const box=/viewBox="([^"]+)"/.exec(svg)[1].split(/\s+/).map(Number);
   // Poppler's root point dimensions are rounded; use the exact drawing box
   // for both previews to avoid a one-pixel height difference from rounding.
   svg=svg.replace(/width="[^"]+"/,`width="${box[2]}"`).replace(/height="[^"]+"/,`height="${box[3]}"`);
   return sharp(Buffer.from(svg),{density:144}).resize({width:1000}).flatten({background:'white'}).removeAlpha().raw().toBuffer({resolveWithObject:true});
  }));
  const [s,t]=rasters;if(s.data.length!==t.data.length)throw Error(b+' '+a.id+' dimensions differ');
  let sum=0,changed=0;for(let i=0;i<s.data.length;i++){const delta=Math.abs(s.data[i]-t.data[i]);sum+=delta;if(delta>16)changed++;}
  const row={id:a.id,mean_channel_difference:sum/s.data.length,channel_fraction_over_16:changed/s.data.length};report.push(row);
  if(row.mean_channel_difference>2||row.channel_fraction_over_16>.03)throw Error(JSON.stringify({batch:b,...row}));
 }
 fs.writeFileSync(path.join(root,'conversion-batches/checkpoints',b,'vector-fidelity.json'),JSON.stringify({scale_width_px:1000,drawings:report},null,2)+'\n');console.log(b,report.length,'SVG comparisons passed');
}})().catch(e=>{console.error(e);process.exit(1)});
