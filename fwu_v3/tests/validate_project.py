"""Static project checks. Run: python fwu_v2/tests/validate_project.py"""
import ast
import csv
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
POINT_APIS = {'READPOINT': 0, 'READPOINT_ALARM': 0, 'WRITEPOINT': 0,
              'WRITEPOINT_PRI': 0, 'RELEASE_PRI': 0, 'LOOP2': 2}

def validate():
    rows = list(csv.DictReader((ROOT/'POINT_RENAME_MAP.csv').open(encoding='utf-8-sig')))
    rename = {r['old_name']: r['new_name'] for r in rows}
    assert len(rename) == len(rows)
    assert len(set(rename.values())) == len(rows)
    # v3 관제점·장치명 변경 (2026-11-23, Naming_Rule_점검.xlsx 수정안 적용)
    v3_rows = list(csv.DictReader((ROOT/'POINT_RENAME_MAP_V3.csv').open(encoding='utf-8-sig')))
    dev_rows = list(csv.DictReader((ROOT/'DEVICE_RENAME_MAP_V3.csv').open(encoding='utf-8-sig')))
    v3_old = {r['old_name'] for r in v3_rows} | {r['old_name'] for r in dev_rows}
    assert len(v3_old) == len(v3_rows) + len(dev_rows)
    rename_old = set(rename) | v3_old
    points = []
    xml_paths = list(ROOT.rglob('*.xml'))
    for path in xml_paths:
        tree = ET.parse(path)
        for node in tree.iter():
            for value in node.attrib.values():
                assert value not in rename_old, (path, value)
            if path.parent.name == 'ControlPoint' and node.get('pointType') and node.get('name'):
                points.append(node.attrib)
    names = [p['name'] for p in points]
    ids = [p['id'] for p in points if p.get('id')]
    assert len(names) == len(set(names)), 'duplicate point name'
    assert len(ids) == len(set(ids)), 'duplicate point id'
    assert not any(' ' in n for n in names)
    by_name = {p['name']: p for p in points}
    for row in rows:
        if row['definition_file'] == 'UNBOUND_DI':
            continue
        p = by_name[row['new_name']]
        assert p.get('id', '') == row['point_id']
        assert p.get('address', '') == row['address']
    for row in v3_rows:
        p = by_name[row['new_name']]
        assert p.get('id', '') == row['point_id'] and p.get('address', '') == row['address'], row
    units = {n.get('name') for f in (ROOT/'ControlPoint').glob('*.xml') for n in ET.parse(f).iter('modbusSlaveUnit')}
    for row in dev_rows:
        assert row['new_name'] in units, row
    refs, timers, loops = set(), {}, {}
    logic_paths = sorted((ROOT/'Logic').glob('*.py'))
    for path in logic_paths:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        constants = {}
        # Coding Rule(code rule.pptx 3번 슬라이드, 2026-11-23 적용):
        # - 상수: 모두 대문자 + 밑줄. 숫자 상수 또는 READPOINT로 읽는 설정값(refac 예제 NO_FLOW 방식)
        # - 변수: PascalCase. 들여쓰기 0에서 대입하는 전역변수는 m, Boolean은 b 접두어 (예: mbRATValid)
        # - engine = ddc_logic()은 LDPL 표준 표기라 예외
        global_names, local_names = set(), set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        (global_names if node.col_offset == 0 else local_names).add(name)
                        if name == 'engine':
                            continue
                        assert re.fullmatch(r'[A-Z][A-Z0-9_]*|m?b?[A-Z][A-Za-z0-9]*', name), (path, name)
                        if re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
                            v = node.value
                            is_setting = (isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute)
                                          and v.func.attr == 'READPOINT' and len(v.args) == 1
                                          and isinstance(v.args[0], ast.Constant) and isinstance(v.args[0].value, str))
                            assert isinstance(v, ast.Constant) or is_setting, (path, name)
                            if isinstance(v, ast.Constant):
                                constants[name] = v.value
                            continue
                        is_bool = isinstance(node.value, (ast.Compare, ast.BoolOp)) or (
                            isinstance(node.value, ast.Name) and node.value.id in ('TRUE', 'FALSE'))
                        if is_bool:
                            assert re.match(r'm?b[A-Z]', name), (path, name)
        for name in global_names - {'engine'}:
            if not re.fullmatch(r'[A-Z][A-Z0-9_]*', name):
                assert name.startswith('m'), (path, name, 'global needs m prefix')
        for name in local_names - global_names:
            assert not re.match(r'm[bA-Z]', name), (path, name, 'local must not use m prefix')
        timer_ids, loop_ids = {}, {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            method = node.func.attr
            if method in POINT_APIS:
                arg = node.args[POINT_APIS[method]]
                assert isinstance(arg, ast.Constant) and isinstance(arg.value, str), (path, method)
                assert arg.value not in rename_old and ' ' not in arg.value, (path, arg.value)
                refs.add(arg.value)
                if method == 'LOOP2':
                    for idx in (1, 3):
                        ref = node.args[idx]
                        assert isinstance(ref, ast.Constant) and isinstance(ref.value, str)
                        assert ref.value not in rename_old and ' ' not in ref.value
                        refs.add(ref.value)
            if method in ('SECTIMER', 'LOOP2', 'LOOP2_INIT'):
                # 타이머·LOOP2 번호는 숫자 대신 이름 있는 상수로 쓴다 (code rule.pptx 4번 슬라이드 예시)
                arg = node.args[11 if method == 'LOOP2' else 0]
                assert isinstance(arg, ast.Name) and arg.id in constants, (path, method)
                value = constants[arg.id]
                if method == 'SECTIMER':
                    assert 0 <= value <= 9, (path, value)
                    timer_ids[arg.id] = value
                else:
                    loop_ids[arg.id] = value
        assert len(timer_ids.values()) == len(set(timer_ids.values())), (path, timer_ids)
        assert len(loop_ids.values()) == len(set(loop_ids.values())), (path, loop_ids)
        timers[path.stem], loops[path.stem] = timer_ids, loop_ids
    missing = sorted(refs-set(names))
    mapping = list(csv.DictReader((ROOT/'PICV_POINT_MAPPING.csv').open(encoding='utf-8-sig')))
    declared_unbound = sorted(r['point_name'] for r in mapping)
    assert len(declared_unbound) == len(set(declared_unbound)) == 12
    assert missing == [], missing   # 2026-11-24 FWU_LEAK_DETECT를 IO.xml(CPU00-DI1)에 등록해 미등록 참조 없음
    assert all(name in by_name and by_name[name].get('category') == 'Modbus' for name in declared_unbound)
    registered = [n.get('name') for n in ET.parse(ROOT/'DDC.xml').findall('logicInfo')]
    assert len(registered) == 14 and len(set(registered)) == 14
    assert set(registered) == {p.stem for p in logic_paths}
    expected_main = ['Initialization', 'PICV Control', 'SF Control', 'Sensor Limit Alarm', 'Fan Damper Alarm',
                     'Leak Filter Alarm', 'Comm Fault Alarm', 'Remote Shutdown', 'Failover']
    assert registered[-9:] == expected_main, registered
    assert registered.index('PICV Feedback') < registered.index('SF Control')
    assert by_name['VP_FWU_Smoke_Action_Set']['relinguishDefault'] == '0'
    return {
        'status': 'DRAFT_NOT_COMMISSIONED', 'python_parse': 'PASS', 'xml_parse': 'PASS',
        'point_name_id_uniqueness': 'PASS', 'rename_map_consistency': 'PASS',
        'variable_naming': 'PASS', 'logic_registration': 'PASS',
        'logic_count': len(logic_paths), 'xml_count': len(xml_paths),
        'renamed_points_including_unbound': len(rows),
        'new_unbound_physical_references': [], 'picv_profile_defined': declared_unbound, 'inherited_undefined_references': [],
        'unexpected_undefined_references': [],
        'timers': timers, 'loops': loops,
        'limitations': ['DDC firmware, PI dynamics and hardware not tested',
                       'Fan CH1, ATS CH2, PICV CH3 profile defined; hardware commissioning not performed',
                       'FWU_LEAK_DETECT, FWU_CONDENSATE_PUMP_ALARM, FWU_CHW_ENT/LVG_TEMP use proposed CPU terminals; match wiring and sensor signal',
                       'PICV XML uses Belimo EPIV V4.3.0 profile and station plan 1..4; verify actual firmware/settings',
                       'PICV first-response/freshness guarantee not verified by LDPL code',
                       'External HMI/BMS projects not updated; rename map supplied']
    }

if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
