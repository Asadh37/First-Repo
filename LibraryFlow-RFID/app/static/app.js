const $ = (id) => document.getElementById(id);
let booksCache = [], membersCache = [], circulationMode = 'checkout';
function escapeHtml(value) { return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])); }
async function api(path, options = {}) {
  const response = await fetch(path, options);
  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json') ? await response.json() : await response.text();
  if (!response.ok) throw new Error(typeof body === 'object' ? (body.detail || JSON.stringify(body)) : body);
  return body;
}
function toast(message, type = 'success') {
  const node = document.createElement('div'); node.className = 'toast ' + type; node.textContent = message; $('toast-root').appendChild(node);
  setTimeout(() => node.remove(), 3900);
}
function showResult(target, title, data, error = false) {
  const node = $(target); node.innerHTML = '<strong>' + escapeHtml(title) + '</strong><pre>' + escapeHtml(typeof data === 'string' ? data : JSON.stringify(data, null, 2)) + '</pre>';
  node.style.borderColor = error ? '#f0d5d8' : '#dceee5';
}
function openModal(id) { $(id).classList.add('open'); }
function closeModal(id) { $(id).classList.remove('open'); }
function backdropClose(event, id) { if (event.target === $(id)) closeModal(id); }
function setCirculationMode(mode) {
  circulationMode = mode;
  document.querySelectorAll('.segment').forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
  $('circulation-submit').textContent = ({checkout:'↗ Complete checkout', checkin:'↙ Complete check-in', renew:'↻ Renew loan'})[mode];
  $('circulation-result').textContent = '';
}
async function loadBooks() {
  booksCache = await api('/api/books'); renderBooks(booksCache);
  $('accession-options').innerHTML = booksCache.map(b => '<option value="' + escapeHtml(b.accession_no) + '">' + escapeHtml(b.title) + '</option>').join('');
  if (booksCache[0]) $('gate-accession').value = booksCache[0].accession_no;
  const untagged = booksCache.find(b => !b.rfid_tag); if (untagged) $('tag-accession').value = untagged.accession_no;
  updateStats();
}
function renderBooks(items) {
  const body = $('book-table');
  if (!items.length) { body.innerHTML = '<tr><td colspan="4" class="empty-state">No matching items found.</td></tr>'; $('book-count').textContent = '0 items'; return; }
  body.innerHTML = items.slice(0, 8).map((b,i) => '<tr><td><div class="book-title"><div class="book-cover c' + ((i%4)+1) + '">▤</div><div><strong title="' + escapeHtml(b.title) + '">' + escapeHtml(b.title) + '</strong><small>' + escapeHtml(b.author || 'Author not recorded') + '</small></div></div></td><td>' + escapeHtml(b.accession_no) + '</td><td><span class="tag-status ' + (b.rfid_tag?'tagged':'untagged') + '"><i></i>' + (b.rfid_tag?'Tagged':'Untagged') + '</span></td><td><span class="avail-status ' + (b.is_available?'available':'onloan') + '"><i></i>' + (b.is_available?'Available':'On loan') + '</span></td></tr>').join('');
  $('book-count').textContent = 'Showing ' + Math.min(items.length,8) + ' of ' + items.length + ' matching items';
}
function filterBooks() { const q=$('book-search').value.trim().toLowerCase(); renderBooks(booksCache.filter(b => [b.title,b.author,b.accession_no,b.subject,b.rfid_tag].some(x=>String(x||'').toLowerCase().includes(q)))); }
async function loadMembers() {
  membersCache = await api('/api/members'); renderMembers(membersCache);
  $('member-options').innerHTML = membersCache.map(m => '<option value="' + escapeHtml(m.member_no) + '">' + escapeHtml(m.name) + '</option>').join('');
}
function initials(name){return String(name||'').split(/\s+/).filter(Boolean).slice(0,2).map(p=>p[0]).join('').toUpperCase()||'??';}
function renderMembers(items) {
  $('member-list').innerHTML = items.length ? items.slice(0,5).map((m,i) => '<div class="member-row"><div class="member-avatar m' + ((i%4)+1) + '">' + escapeHtml(initials(m.name)) + '</div><div class="member-info"><strong>' + escapeHtml(m.name) + '</strong><small>' + escapeHtml(m.member_no) + ' · fine ₹' + Number(m.fine_balance||0).toFixed(2) + '</small></div><span class="member-role">' + escapeHtml(m.role) + '</span><span class="member-flag ' + (m.blocked?'blocked':'') + '">' + (m.blocked?'Blocked':'Active') + '</span></div>').join('') : '<div class="empty-state">No members found.</div>';
  $('member-count').textContent = 'Showing ' + Math.min(items.length,5) + ' of ' + items.length + ' members';
}
function filterMembers(){const q=$('member-search').value.toLowerCase().trim();renderMembers(membersCache.filter(m=>[m.name,m.member_no,m.email,m.role].some(x=>String(x||'').toLowerCase().includes(q))));}
async function loadActivity() {
  const events=await api('/api/reports/audit?limit=8');
  $('activity-list').innerHTML = events.length ? events.slice(0,6).map((e,i)=>'<div class="activity-row"><div class="activity-icon a'+((i%4)+1)+'">'+({'book.created':'▤','circulation.checkout':'↗','circulation.checkin':'↙','rfid.tag_associated':'⌗','rfid.inventory':'⌗','gate.unauthorised_removal':'⚑','member.created':'♙'}[e.action]||'✓')+'</div><div class="activity-copy"><strong>'+escapeHtml(e.action.replaceAll('.',' · ').replaceAll('_',' '))+'</strong><p>'+escapeHtml(e.entity_type+' #'+e.entity_id+' · '+e.actor)+'</p></div><span class="activity-time">'+escapeHtml(new Date(e.at+'Z').toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'}))+'</span></div>').join('') : '<div class="empty-state">No activity has been recorded yet.</div>';
}
async function updateStats(){try{const d=await api('/api/dashboard');$('stat-books').textContent=d.total_books;$('stat-loans').textContent=d.active_loans;$('stat-tagged').textContent=d.tagged_items;$('stat-alerts').textContent=d.unauthorised_gate_events;$('tag-progress').style.width=(d.total_books?d.tagged_items/d.total_books*100:0)+'%';$('tag-coverage').textContent=(d.total_books?Math.round(d.tagged_items/d.total_books*100):0)+'% coverage';}catch(e){console.error(e)}}
$('circulation-form').addEventListener('submit', async event => {
  event.preventDefault(); const payload={accession_no:$('circulation-accession').value.trim(),member_no:$('circulation-member').value.trim()}; const route={checkout:'/api/circulation/checkout',checkin:'/api/circulation/checkin',renew:'/api/circulation/renew'}[circulationMode];
  try { const data=await api(route,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}); showResult('circulation-result','Success: '+data.status,data); toast(data.status.replace('_',' ')+' successful'); await Promise.all([loadBooks(),loadMembers(),loadActivity()]); }
  catch(error){showResult('circulation-result','Action blocked',error.message,true);toast(error.message,'error');}
});
$('book-form').addEventListener('submit',async event=>{
  event.preventDefault();const form=new FormData(event.currentTarget);const payload=Object.fromEntries(form.entries());payload.is_reference=form.get('is_reference')==='on';
  try{await api('/api/books',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});closeModal('book-modal');event.currentTarget.reset();toast('Catalog record created');await Promise.all([loadBooks(),loadActivity()]);}catch(error){toast(error.message,'error');}
});
$('member-form').addEventListener('submit',async event=>{
  event.preventDefault();const payload=Object.fromEntries(new FormData(event.currentTarget).entries());
  try{await api('/api/members',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});closeModal('member-modal');event.currentTarget.reset();toast('Member record created');await Promise.all([loadMembers(),loadActivity()]);}catch(error){toast(error.message,'error');}
});
async function runInventory(){const shelf=$('inventory-shelf').value.trim()||'CS-01';try{const data=await api('/api/rfid/inventory?shelf='+encodeURIComponent(shelf),{method:'POST'});showResult('workflow-result','Inventory scan · '+shelf,data);toast('Mock inventory scan complete');await loadActivity();}catch(e){showResult('workflow-result','Inventory scan failed',e.message,true);toast(e.message,'error')}}
async function runGate(){const accession_no=$('gate-accession').value.trim();try{const data=await api('/api/rfid/gate-event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({accession_no,authorised:false})});showResult('workflow-result','Security gate · unauthorised removal',data);toast('Mock gate alert queued');await Promise.all([updateStats(),loadActivity()]);}catch(e){showResult('workflow-result','Gate simulation failed',e.message,true);toast(e.message,'error')}}
async function tagItem(){const accession_no=$('tag-accession').value.trim();const tag_id=$('tag-id').value.trim()||'MOCK-TAG-'+Date.now().toString().slice(-7);try{const data=await api('/api/rfid/tag',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({accession_no,tag_id})});showResult('workflow-result','RFID tag association complete',data);toast('Mock RFID tag associated');await Promise.all([loadBooks(),loadActivity()]);}catch(e){showResult('workflow-result','Tagging failed',e.message,true);toast(e.message,'error')}}
async function smartCardLogin(){const form=new FormData();form.append('card_id',$('smart-card-id').value.trim());try{const data=await api('/api/rfid/smart-card-login',{method:'POST',body:form});showResult('workflow-result','Smart-card validation result',data);toast('Mock login validated: '+data.role);await loadActivity();}catch(e){showResult('workflow-result','Smart-card rejected',e.message,true);toast(e.message,'error')}}
$('migration-file').addEventListener('change',()=>{$('migration-file-name').textContent=$('migration-file').files[0]?.name||'No file selected'});
$('migration-form').addEventListener('submit',async event=>{
  event.preventDefault();const file=$('migration-file').files[0];if(!file)return toast('Choose an .xlsx file first','error');const form=new FormData();form.append('file',file);$('migration-result').textContent='Staging and validating spreadsheet…';
  try{const data=await api('/api/migration/stage',{method:'POST',body:form});showResult('migration-result','Batch #'+data.batch_id+' staged',data);$('latest-batch').textContent='Batch #'+data.batch_id+' · '+data.status;$('latest-batch-detail').textContent=data.valid_rows+' valid · '+data.rejected_rows+' rejected · '+data.duplicate_rows+' duplicates';$('migration-file-name').textContent='Choose another spreadsheet';event.currentTarget.reset();await loadBatches();toast('Spreadsheet staged; review before committing');}catch(e){$('migration-result').textContent='Could not stage spreadsheet: '+e.message;toast(e.message,'error');}
});
async function loadBatches(){try{const batches=await api('/api/migration/batches');$('batch-list').innerHTML=batches.length?batches.slice(0,5).map(b=>'<div class="batch-row"><div><strong>Batch #'+b.id+'</strong><br><span>'+escapeHtml(b.source_name)+' · '+b.source_rows+' source rows</span></div><span class="batch-state">'+escapeHtml(b.status)+'</span><span>'+b.valid_rows+' valid · '+b.rejected_rows+' rejected · '+b.duplicate_rows+' duplicate</span><div class="batch-actions">'+(b.status==='staged'?'<button class="btn btn-small btn-primary" onclick="commitBatch('+b.id+')">Commit valid</button>':'')+(b.status==='committed'?'<button class="btn btn-small btn-secondary" onclick="rollbackBatch('+b.id+')">Rollback</button>':'')+'<button class="btn btn-small btn-secondary" onclick="viewBatch('+b.id+')">Details</button></div></div>').join(''):'<div class="empty-state">No migration batches yet.</div>';}catch(e){console.error(e)}}
async function commitBatch(id){if(!confirm('Commit valid rows from migration batch #'+id+'? This adds new records to the prototype database.'))return;try{const data=await api('/api/migration/batches/'+id+'/commit',{method:'POST'});showResult('migration-result','Migration committed',data);toast('Migration committed: '+data.created_count+' records');await Promise.all([loadBatches(),loadBooks(),loadActivity()]);}catch(e){toast(e.message,'error');showResult('migration-result','Commit failed',e.message,true)}}
async function rollbackBatch(id){if(!confirm('Roll back records introduced by migration batch #'+id+'? Only audit-tracked import records will be considered.'))return;try{const data=await api('/api/migration/batches/'+id+'/rollback',{method:'POST'});showResult('migration-result','Migration rollback finished',data);toast('Batch rollback completed');await Promise.all([loadBatches(),loadBooks(),loadActivity()]);}catch(e){toast(e.message,'error');showResult('migration-result','Rollback refused',e.message,true)}}
async function viewBatch(id){try{const data=await api('/api/migration/batches/'+id);showResult('migration-result','Batch #'+id+' details',data);}catch(e){toast(e.message,'error')}}
async function loadIntegrations(){const data=await api('/api/rfid/devices');const icons={'staff-reader':'⌗','handheld-reader':'⌗','security-gate':'⚑','smart-card':'▣','printer':'▤','camera':'▧','ilms_adapter':'⇄','notifications':'✉'};$('integration-list').innerHTML=Object.entries(data).map(([name,value])=>'<div class="integration-row"><div class="integration-symbol">'+(icons[name]||'⌘')+'</div><div class="integration-copy"><strong>'+escapeHtml(name.replaceAll('_',' '))+'</strong><small>'+escapeHtml(typeof value==='object'?(value.status||value.device_id||Object.keys(value).join(', ')):value)+'</small></div><span class="status-pill status-success"><i></i> Mock</span></div>').join('')}
function downloadReport(){api('/api/dashboard').then(d=>{const report={generated_at:new Date().toISOString(),prototype:'LibraryFlow RFID',warning:'Synthetic demonstration only; not production evidence.',dashboard:d,books:booksCache,members:membersCache};const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='libraryflow-summary.json';a.click();URL.revokeObjectURL(url);toast('Summary exported')}).catch(e=>toast(e.message,'error'))}
(async function init(){try{await Promise.all([loadBooks(),loadMembers(),loadActivity(),loadIntegrations(),loadBatches(),updateStats()]);}catch(error){toast('Startup check: '+error.message,'error')}})();
