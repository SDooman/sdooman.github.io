const fs=require('fs');const sharp=require('sharp');
(async()=>{let files=fs.readdirSync('gat-1-20/assets').filter(f=>f.endsWith('.svg'));for(let f of files){await sharp('gat-1-20/assets/'+f,{density:288}).png().toFile('.conversion-work/'+f.replace('.svg','-equation.png'));} console.log('Rendered '+files.length+' equations');})();
