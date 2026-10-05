import os, tempfile
DB = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False); DB.close()
os.environ['DATABASE_URL'] = f'sqlite:///{DB.name}'
from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def setup_module():
    with TestClient(app) as c:
        c.get('/api/health')

def test_health_has_mock_adapters():
    response=client.get('/api/health')
    assert response.status_code==200
    payload=response.json()
    assert payload['status']=='ok'
    assert payload['adapters']['handheld-reader']['mock'] is True

def test_seeded_catalog_and_member_data():
    assert len(client.get('/api/books').json()) >= 8
    assert any(m['member_no']=='STU-2026-001' for m in client.get('/api/members').json())

def test_reference_item_checkout_is_blocked():
    response=client.post('/api/circulation/checkout',json={'accession_no':'ACC-1002','member_no':'STU-2026-001'})
    assert response.status_code==409
    assert 'Reference-only' in response.json()['detail']

def test_blocked_member_checkout_is_blocked():
    response=client.post('/api/circulation/checkout',json={'accession_no':'ACC-1001','member_no':'STU-2026-003'})
    assert response.status_code==403

def test_checkout_checkin_and_audit():
    response=client.post('/api/circulation/checkout',json={'accession_no':'ACC-1005','member_no':'STU-2026-001'})
    assert response.status_code==200
    assert response.json()['integration']['protocol'].startswith('simulated')
    checkin=client.post('/api/circulation/checkin',json={'accession_no':'ACC-1005','member_no':'STU-2026-001'})
    assert checkin.status_code==200
    assert checkin.json()['status']=='checked_in'
    audit=client.get('/api/reports/audit').json()
    assert any(x['action']=='circulation.checkout' for x in audit)

def test_tag_association_and_duplicate_tag_guard():
    response=client.post('/api/rfid/tag',json={'accession_no':'ACC-1005','tag_id':'TEST-TAG-555'})
    assert response.status_code==200
    duplicate=client.post('/api/rfid/tag',json={'accession_no':'ACC-1007','tag_id':'TEST-TAG-555'})
    assert duplicate.status_code==409

def test_gate_event_has_camera_and_notification_mock():
    response=client.post('/api/rfid/gate-event',json={'accession_no':'ACC-1001','authorised':False})
    assert response.status_code==200
    payload=response.json()
    assert payload['cctv']['reference'].startswith('mock://camera/')
    assert payload['notification']['status']=='queued (mock)'

def test_smart_card_role_permissions():
    response=client.post('/api/rfid/smart-card-login',data={'card_id':'CARD-FAC-2026-001'})
    assert response.status_code==200
    payload=response.json()
    assert payload['authenticated'] is True
    assert payload['permissions']['circulation'] is True

def test_search_endpoint():
    results=client.get('/api/catalog/search?q=Clean').json()
    assert any(x['title']=='Clean Code' for x in results)

def test_migration_stage_commit_rollback_preserves_preexisting_records():
    from openpyxl import Workbook
    import io
    workbook=Workbook(); sheet=workbook.active
    sheet.append(['accession_no','title','author','shelf'])
    sheet.append(['TEST-IMPORT-001','Synthetic imported title','Demo Author','A-99'])
    sheet.append(['','Invalid row should be rejected','Demo Author','A-99'])
    sheet.append(['TEST-IMPORT-001','Duplicate within sheet','Demo Author','A-99'])
    stream=io.BytesIO(); workbook.save(stream); stream.seek(0)
    staged=client.post('/api/migration/stage',files={'file':('migration-test.xlsx',stream.getvalue(),'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
    assert staged.status_code==200, staged.text
    payload=staged.json(); assert (payload['valid_rows'],payload['rejected_rows'],payload['duplicate_rows'])==(1,1,1)
    batch_id=payload['batch_id']
    committed=client.post(f'/api/migration/batches/{batch_id}/commit')
    assert committed.status_code==200, committed.text
    assert committed.json()['created_count']==1 and committed.json()['reconciled'] is True
    assert any(b['accession_no']=='TEST-IMPORT-001' for b in client.get('/api/books').json())
    rolled=client.post(f'/api/migration/batches/{batch_id}/rollback')
    assert rolled.status_code==200, rolled.text
    assert rolled.json()['removed_count']==1
    assert not any(b['accession_no']=='TEST-IMPORT-001' for b in client.get('/api/books').json())
    assert any(b['accession_no']=='ACC-1001' for b in client.get('/api/books').json())
