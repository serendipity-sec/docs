const {chromium}=require('playwright');
const fs=require('node:fs');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const assert=require('node:assert/strict');
const {createHash}=require('node:crypto');
(async()=>{
 const file=process.argv[2]?path.resolve(process.argv[2]):path.join(__dirname,'flowdelta-weekly-2026-10-15.html');
 const out=path.join(__dirname,'.qa-output');
 fs.mkdirSync(out,{recursive:true});
 const channel=process.env.PLAYWRIGHT_CHANNEL;
 const browser=await chromium.launch({headless:true,...(channel?{channel}:{})});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(file).href);
 await page.screenshot({path:path.join(out,'desktop-top.png')});
 await page.screenshot({path:path.join(out,'desktop-full.png'),fullPage:true});
 await page.locator('.story-case').screenshot({path:path.join(out,'purpose-example.png')});
 for(let i=0;i<4;i++){
  await page.locator('#relay-'+i).click();
  assert.equal(await page.locator('#relay-'+i).getAttribute('aria-selected'),'true');
  assert.equal(await page.locator('.relay-panel:visible').count(),1);
  const panel=page.locator('#relay-panel-'+i);
  assert.equal(await panel.isVisible(),true);
  assert.match(await panel.innerText(),/이번 주 완료/);
  assert.match(await panel.innerText(),/다음에 붙일 기능/);
  await panel.screenshot({path:path.join(out,'relay-'+i+'.png')});
 }
 await page.locator('#relay-3').press('Home');
 assert.equal(await page.locator('#relay-0').getAttribute('aria-selected'),'true');
 await page.locator('#relay-0').press('ArrowRight');
 assert.equal(await page.locator('#relay-1').getAttribute('aria-selected'),'true');
 await page.locator('#relay-1').press('End');
 assert.equal(await page.locator('#relay-3').getAttribute('aria-selected'),'true');
 await page.locator('.actual-details summary').click();
 assert.equal(await page.locator('.actual-content').isVisible(),true);
 await page.locator('.actual-details summary').click();
 for(let i=0;i<5;i++){
  await page.locator('#week-'+i).click();
  assert.equal(await page.locator('#week-'+i).getAttribute('aria-selected'),'true');
  assert.equal(await page.locator('.roadmap-panel:visible').count(),1);
  assert.equal(await page.locator('#week-panel-'+i).isVisible(),true);
 }
 await page.locator('#week-4').press('Home');
 assert.equal(await page.locator('#week-0').getAttribute('aria-selected'),'true');
 await page.locator('#week-0').press('ArrowRight');
 assert.equal(await page.locator('#week-1').getAttribute('aria-selected'),'true');
 for(const [version,text] of [['before','기준 결과 확보'],['fixed','시험 내 개선 확인'],['changed','노출 관측']]){
  await page.locator('#version-'+version).click();
  assert.match(await page.locator('#result-label').innerText(),new RegExp(text));
 }
 await page.locator('#product').screenshot({path:path.join(out,'final-preview.png')});
 await page.locator('#next-week').screenshot({path:path.join(out,'next-week.png')});
 const layouts=[];
 for(const width of [1440,1024,768,390,360]){
  await page.setViewportSize({width,height:1000});
  await page.goto(pathToFileURL(file).href);
  const dimensions=await page.evaluate(()=>({viewport:innerWidth,scroll:document.documentElement.scrollWidth,body:document.body.scrollWidth}));
  assert.ok(dimensions.scroll<=width,JSON.stringify(dimensions));
  // Relay arrows intentionally extend into the gap; check their text spans separately.
  const overflow=await page.locator('h1,h2,h3,p,button:not(.relay-tab),.relay-name,.relay-question,.relay-pass,.path-node,.response').evaluateAll(elements=>elements.filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2).map(e=>e.textContent.slice(0,60)));
  assert.deepEqual(overflow,[],`overflow at ${width}: ${overflow}`);
  for(let i=0;i<4;i++){
   await page.locator('#relay-'+i).click();
   const roleOverflow=await page.locator('#relay-panel-'+i+' strong, #relay-panel-'+i+' p').evaluateAll(elements=>elements.filter(e=>e.getClientRects().length&&e.scrollWidth>e.clientWidth+2).map(e=>e.textContent.slice(0,60)));
   assert.deepEqual(roleOverflow,[],`role ${i} overflow at ${width}: ${roleOverflow}`);
  }
  layouts.push(dimensions);
  if(width===390){
   await page.locator('#relay-0').click();
   await page.locator('.relay-panel:visible').screenshot({path:path.join(out,'mobile-role.png')});
   await page.evaluate(()=>window.scrollTo(0,0));
   await page.screenshot({path:path.join(out,'mobile-top.png')});
  }
 }
 await page.setViewportSize({width:1100,height:1000});
 await page.emulateMedia({media:'print'});
 assert.equal(await page.locator('.roadmap-panel:visible').count(),5);
 assert.equal(await page.locator('.relay-panel:visible').count(),4);
 assert.equal(await page.locator('.print-versions').isVisible(),true);
 assert.equal(await page.locator('.topnav').isVisible(),false);
 await page.emulateMedia({media:'screen'});
 await page.evaluate(()=>{window.print=()=>{window.__printTriggered=true}});
 await page.locator('#print-button').click();
 assert.equal(await page.evaluate(()=>window.__printTriggered),true);
 const anchors=await page.locator('a[href^="#"]').evaluateAll(elements=>elements.map(e=>({href:e.getAttribute('href'),exists:!!document.getElementById(e.hash.slice(1))})));
 assert.ok(anchors.every(a=>a.exists));
 assert.deepEqual(errors,[]);
 const result={
  status:'passed',file:path.basename(file),
  sha256:createHash('sha256').update(fs.readFileSync(file)).digest('hex'),
  checkedAt:new Date().toISOString(),browser:channel||'chromium',browserVersion:browser.version(),
  layouts,roleTabs:4,roadmapTabs:5,versionStates:3,keyboard:true,print:true,
  consoleErrors:errors,localAnchors:anchors,
  scope:'Report layout and interactions only; not FlowDelta security detection performance.'
 };
 fs.writeFileSync(path.join(out,'verification.json'),JSON.stringify(result,null,2)+'\n');
 console.log(JSON.stringify(result));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
