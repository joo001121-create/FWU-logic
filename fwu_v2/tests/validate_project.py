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
    points = []
    xml_paths = list(ROOT.rglob('*.xml'))
    for path in xml_paths:
        tree = ET.parse(path)
        for node in tree.iter():
            for value in node.attrib.values():
                assert value not in rename, (path, value)
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
    refs, timers, loops = set(), {}, {}
    logic_paths = sorted((ROOT/'Logic').glob('*.py'))
    for path in logic_paths:
        tree = ast.parse(path.read_text(encoding='utf-8'))
        constants = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        name = target.id
                        assert re.fullmatch(r'[a-z][a-z0-9_]*|[A-Z][A-Z0-9_]*', name), (path, name)
                        if name.isupper():
                            assert isinstance(node.value, ast.Constant), (path, name)
                            constants[name] = node.value.value
                        if isinstance(node.value, (ast.Compare, ast.BoolOp)):
                            assert name.startswith('b_'), (path, name)
        timer_ids, loop_ids = {}, {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
                continue
            method = node.func.attr
            if method in POINT_APIS:
                arg = node.args[POINT_APIS[method]]
                assert isinstance(arg, ast.Constant) and isinstance(arg.value, str), (path, method)
                assert arg.value not in rename and ' ' not in arg.value, (path, arg.value)
                refs.add(arg.value)
                if method == 'LOOP2':
                    for idx in (1, 3):
                        ref = node.args[idx]
                        assert isinstance(ref, ast.Constant) and isinstance(ref.value, str)
                        assert ref.value not in rename and ' ' not in ref.value
                        refs.add(ref.value)
            if method in ('SECTIMER', 'LOOP2', 'LOOP2_INIT'):
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
    assert missing == ['FWU_LEAK_DETECT'], missing
    registered = [n.get('name') for n in ET.parse(ROOT/'DDC.xml').findall('logicInfo')]
    assert len(registered) == 13 and len(set(registered)) == 13
    assert set(registered) == {p.stem for p in logic_paths}
    expected_main = ['Initialization', 'PICV Control', 'SF Control', 'Alarm-1', 'Alarm-2', 'Alarm-3', 'Remote Shutdown', 'Failover']
    assert registered[-8:] == expected_main, registered
    assert registered.index('PICV Feedback') < registered.index('SF Control')
    assert by_name['VP_FWU_Smoke_Action_Set']['relinguishDefault'] == '0'
    return {
        'status': 'DRAFT_NOT_COMMISSIONED', 'python_parse': 'PASS', 'xml_parse': 'PASS',
        'point_name_id_uniqueness': 'PASS', 'rename_map_consistency': 'PASS',
        'variable_naming': 'PASS', 'logic_registration': 'PASS',
        'logic_count': len(logic_paths), 'xml_count': len(xml_paths),
        'renamed_points_including_unbound': len(rows),
        'new_undefined_references': [], 'inherited_undefined_references': missing,
        'timers': timers, 'loops': loops,
        'limitations': ['DDC firmware, PI dynamics and hardware not tested',
                       'Physical maps retain old ports/registers/scales; point names updated only',
                       'FWU_LEAK_DETECT remains unbound',
                       'External HMI/BMS projects not updated; rename map supplied']
    }

if __name__ == '__main__':
    print(json.dumps(validate(), ensure_ascii=False, indent=2))
