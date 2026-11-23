"""Checks logic against known API surface; not a DDC compiler or hardware test."""
import ast
import hashlib
import json
import unittest
from test_control import Engine, ROOT


class LdplAuditTests(unittest.TestCase):
    def test_only_picv_feedback_changed(self):
        old = json.loads((ROOT/'SOURCE_LOGIC_SHA256.json').read_text())['sha256']
        changed = [p.name for p in (ROOT/'Logic').glob('*.py')
                   if hashlib.sha256(p.read_bytes()).hexdigest() != old[p.name]]
        self.assertEqual(changed, ['PICV Feedback.py'])

    def test_all_blocks_use_only_existing_api_and_basic_statements(self):
        arities = {'READPOINT': {1}, 'WRITEPOINT': {2}, 'WRITEPOINT_PRI': {3},
                   'RELEASE_PRI': {2}, 'READPOINT_ALARM': {1}, 'SECTIMER': {2},
                   'MAX': set(range(1, 6)), 'MIN': set(range(1, 6)),
                   'LOOP2': {13}, 'LOOP2_INIT': {1}}
        for path in (ROOT/'Logic').glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text())):
                self.assertNotIsInstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef,
                                               ast.AsyncFunctionDef, ast.ClassDef, ast.Await))
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        self.assertEqual(node.func.id, 'ddc_logic')
                    else:
                        self.assertIsInstance(node.func, ast.Attribute)
                        self.assertEqual(node.func.value.id, 'engine')
                        self.assertIn(node.func.attr, arities, path.name)
                        self.assertIn(len(node.args), arities[node.func.attr], path.name)

    def test_no_adapter_or_sample_counter_dependency(self):
        for p in (ROOT/'Logic').glob('*.py'):
            tree = ast.parse(p.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    for retired in ('_Input_OK', '_Sample_Seq', '_Sample_Prev', 'PICV_Input_Timeout'):
                        self.assertNotIn(retired, node.value)


class PicvInputTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine()
        self.e.set('VP_FWU_PICV_Input_Enable', 1)
        self.e.set('VP_FWU_PICV_Control_Mode', 1)
        for i in range(1, 5):
            for q, value in [('Position', 0), ('Flow', 0), ('Temperature', 20)]:
                point = f'FWU_PICV-{i}.{q}'
                self.e.set(point, value)
                self.e.point_alarms[point] = 0

    def run_feedback(self):
        self.e.run('PICV Feedback')

    def get(self, p):
        return self.e.READPOINT(p)

    def test_disabled_does_not_require_physical_point_reads(self):
        e = self.e
        e.set('VP_FWU_PICV_Input_Enable', 0)
        for p in list(e.defaults):
            if p.startswith('FWU_PICV-'):
                del e.defaults[p]
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 0)
        self.assertEqual(self.get('VP_FWU_PICV_Alarm'), 1)

    def test_every_valve_and_quantity_alarm_blocks_closed(self):
        for i in range(1, 5):
            for q in ('Position', 'Flow', 'Temperature'):
                for alarm in (1, 2, 4, 8, 9, 12):
                    with self.subTest(valve=i, quantity=q, alarm=alarm):
                        p = f'FWU_PICV-{i}.{q}'
                        self.e.point_alarms[p] = alarm
                        self.run_feedback()
                        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 0)
                        self.assertEqual(self.get(f'VP_FWU_PICV-{i}_Feedback_Valid'), 0)
                        self.assertEqual(self.get(f'VP_FWU_PICV-{i}_Comm_Fault'), 1)
                        self.assertEqual(self.get('VP_FWU_Flow_Comm_Fault'), 1)
                        for j in range(1, 5):
                            if j != i:
                                self.assertEqual(self.get(f'VP_FWU_PICV-{j}_Feedback_Valid'), 1)
                        self.e.point_alarms[p] = 0
                        self.run_feedback()
                        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 1)
                        self.assertEqual(self.get('VP_FWU_Flow_Comm_Fault'), 0)

    def test_same_values_do_not_create_false_timeout(self):
        self.run_feedback()
        self.e.tick(10000)
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 1)

    def test_raw_points_drive_existing_display_points(self):
        for q, value in [('Position', 45), ('Flow', 123), ('Temperature', 27)]:
            self.e.set(f'FWU_PICV-3.{q}', value)
        self.run_feedback()
        for q, value in [('Position', 45), ('Flow', 123), ('Temperature', 27)]:
            self.assertEqual(self.get(f'VP_FWU_PICV-3_{q}'), value)
        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 0)

    def test_invalid_position_range_blocks_closed(self):
        for pos, valid, closed in [(-1, 0, 0), (0, 1, 1), (4.99, 1, 1),
                                   (5, 1, 0), (100, 1, 0), (101, 0, 0)]:
            self.e.set('FWU_PICV-4.Position', pos)
            self.run_feedback()
            self.assertEqual(self.get('VP_FWU_PICV-4_Feedback_Valid'), valid)
            self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), closed)

    def test_flow_check_remains_optional_and_individual(self):
        e = self.e
        e.set('FWU_PICV-2.Position', 40)
        e.set('FWU_PICV_CONTROL', 40)
        e.set('VP_FWU_Chilled_Water_Supply_Condition', 1)
        e.set('VP_FWU_PICV_No_Flow_Set', 30)
        e.set('VP_FWU_PICV_Leak_Flow_Set', 10)
        e.set('VP_FWU_PICV_Flow_Check_Enable', 0)
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV-2_Alarm'), 0)
        e.set('VP_FWU_PICV_Flow_Check_Enable', 1)
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV-2_Alarm'), 1)
        e.set('FWU_PICV-2.Flow', 30)
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV-2_Alarm'), 0)
        e.set('FWU_PICV-1.Flow', 11)
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV-1_Alarm'), 1)
        self.assertEqual(self.get('VP_FWU_PICV-2_Alarm'), 0)

    def test_fault_holds_normal_stop_but_remote_shutdown_still_stops(self):
        e = self.e
        e.set('VP_FWU_Operation_Mode', 1)
        e.set('VP_FWU_Command', 0)
        e.set('VP_FWU_SF_Status', 1)
        e.set('VP_FWU_SF_Speed_Value', 65)
        e.point_alarms['FWU_PICV-1.Position'] = 8
        self.run_feedback()
        e.run('SF Control')
        self.assertEqual(self.get('VP_FWU_SF_Speed_Value'), 65)
        e.set('VP_FWU_Remote_Shutdown_Command', 1)
        e.run('Remote Shutdown')
        for i in range(1, 9):
            self.assertEqual(self.get(f'FWU_SF-{i}.Run_Command'), 0)
        self.assertEqual(self.get('FWU_PICV_CONTROL'), 0)

    def test_driver_zero_is_not_independent_freshness_evidence(self):
        # Documents the boundary: LDPL cannot tell a fresh 0 from a cached 0
        # when the DDC itself reports no alarm. This is NOT a safety guarantee.
        self.run_feedback()
        self.assertEqual(self.get('VP_FWU_PICV_All_Closed'), 1)


if __name__ == '__main__':
    unittest.main()
