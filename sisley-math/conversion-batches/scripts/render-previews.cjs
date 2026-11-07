// Direct QuickDraw preview rendering. Uses the configured Sharp installation.
const fs=require('node:fs'),path=require('node:path');
const sharp=require(process.env.SISLEY_NODE_PACKAGES+'/sharp');
const root=path.resolve(__dirname,'../..');
(async()=>{
for(const batch of process.argv.slice(2)){
 const book=path.join(root,'gat-'+batch),check=path.join(root,'conversion-batches/checkpoints',batch);
 const rows=JSON.parse(fs.readFileSync(path.join(check,'assets.json')));
 for(const row of rows){
  if(row.source_kind!=='quickdraw-preview')continue;
  await sharp(path.join(book,'assets/source-svg',row.id+'.svg'),{density:216}).flatten({background:'white'}).png().toFile(path.join(book,'assets/source-png',row.id+'.png'));
 }
 console.log(batch+': rendered QuickDraw source previews');
}
})().catch(e=>{console.error(e);process.exit(1)});
