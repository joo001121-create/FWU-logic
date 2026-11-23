"""Follow-up agreed behavior tests; no real DDC or hardware access."""
import unittest
from test_control import Engine

class FollowupTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine()

    def prepare_limits(self):
        e = self.e
        e.set('VP_FWU_SF_Status', 1)
        for kind in ('SAT', 'RAT', 'SAH', 'RAH'):
            e.set('FWU_' + kind, 25 if kind.endswith('T') else 50)
            e.set('VP_FWU_' + kind + '_Low_Alarm_SP', 10 if kind.endswith('T') else 20)
            e.set('VP_FWU_' + kind + '_High_Alarm_SP', 30 if kind.endswith('T') else 80)
        e.run('Alarm-1')

    def test_invalid_reading_clears_limits_before_failure_confirmation(self):
        self.prepare_limits()
        e = self.e
        e.tick(301)
        e.run('Alarm-1')
        for kind in ('SAT', 'RAT', 'SAH', 'RAH'):
            e.set('FWU_' + kind, -20 if kind.endswith('T') else 0)
            for limit in ('High', 'Low'):
                e.WRITEPOINT('VP_FWU_' + kind + '_' + limit + '_Alarm', 1)
        e.run('Alarm-1')
        for elapsed, expected_fault in [(0, 0), (20, 0), (1, 1)]:
            e.tick(elapsed)
            e.run('Alarm-1')
            for kind in ('SAT', 'RAT', 'SAH', 'RAH'):
                for limit in ('High', 'Low'):
                    self.assertEqual(e.READPOINT(f'VP_FWU_{kind}_{limit}_Alarm'), 0)
                self.assertEqual(e.READPOINT(f'VP_FWU_{kind}_Failure_Alarm'), expected_fault)
        # At the validity boundary, valid low measurements still raise low alarms.
        for kind in ('SAT', 'RAT', 'SAH', 'RAH'):
            e.set('FWU_' + kind, 0 if kind.endswith('T') else 5)
        e.run('Alarm-1')
        for kind in ('SAT', 'RAT', 'SAH', 'RAH'):
            self.assertEqual(e.READPOINT(f'VP_FWU_{kind}_Failure_Alarm'), 0)
            self.assertEqual(e.READPOINT(f'VP_FWU_{kind}_Low_Alarm'), 1)

    def test_invalid_sensor_does_not_hide_other_valid_sensor_alarm(self):
        self.prepare_limits()
        e = self.e
        e.tick(301)
        e.set('FWU_SAT', -20)
        e.set('FWU_RAT', 40)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_Low_Alarm'), 0)
        self.assertEqual(e.READPOINT('VP_FWU_RAT_High_Alarm'), 1)

    def test_limit_run_delay_stop_clear_and_temperature_hysteresis(self):
        self.prepare_limits()
        e = self.e
        e.set('FWU_SAT', 9)
        e.tick(300)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_Low_Alarm'), 0)
        e.tick(1)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_Low_Alarm'), 1)
        e.set('FWU_SAT', 10.5)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_Low_Alarm'), 1)
        e.set('FWU_SAT', 10.6)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_Low_Alarm'), 0)
        e.set('FWU_SAT', 31)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_High_Alarm'), 1)
        e.set('VP_FWU_SF_Status', 0)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_High_Alarm'), 0)
        e.set('VP_FWU_SF_Status', 1)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAT_High_Alarm'), 0)

    def test_humidity_hysteresis_and_invalid_clear_during_startup(self):
        self.prepare_limits()
        e = self.e
        e.WRITEPOINT('VP_FWU_SAH_Low_Alarm', 1)
        e.set('FWU_SAH', 0)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAH_Low_Alarm'), 0)
        e.tick(301)
        e.set('FWU_SAH', 19)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAH_Low_Alarm'), 1)
        e.set('FWU_SAH', 25)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAH_Low_Alarm'), 1)
        e.set('FWU_SAH', 26)
        e.run('Alarm-1')
        self.assertEqual(e.READPOINT('VP_FWU_SAH_Low_Alarm'), 0)

    def test_leak_filter_delays_auto_clear_and_no_stop(self):
        e = self.e
        e.set('VP_FWU_Command', 1)
        e.set('FWU_LEAK_DETECT', 1)
        e.set('FWU_FILTER_ALARM', 1)
        e.run('Alarm-2')
        for delta, leak, filt in [(5, 0, 0), (1, 1, 0), (24, 1, 0), (1, 1, 1)]:
            e.tick(delta); e.run('Alarm-2')
            self.assertEqual(e.READPOINT('VP_FWU_Leak_Alarm'), leak)
            self.assertEqual(e.READPOINT('VP_FWU_Filter_Alarm'), filt)
            self.assertEqual(e.READPOINT('VP_FWU_Command'), 1)
        e.set('FWU_LEAK_DETECT', 0); e.set('FWU_FILTER_ALARM', 0)
        e.run('Alarm-2')
        self.assertEqual(e.READPOINT('VP_FWU_Leak_Alarm'), 0)
        self.assertEqual(e.READPOINT('VP_FWU_Filter_Alarm'), 0)
        e.set('FWU_LEAK_DETECT', 1); e.run('Alarm-2')
        self.assertEqual(e.READPOINT('VP_FWU_Leak_Alarm'), 0)

    def test_fan_ats_comm_delay_recovery_and_ao_return(self):
        e = self.e
        e.set('VP_FWU_Operation_Mode', 1)
        e.set('VP_FWU_Command', 1)
        e.set('VP_FWU_SF_Status', 1)
        e.set('VP_FWU_SF_Control_Select', 0)
        e.set('VP_FWU_Speed_SP', 65)
        e.point_alarms['FWU_SF-1.Current_RPM'] = 8
        e.point_alarms['FWU-ATS.Current_Power'] = 8
        e.run('Alarm-3'); e.run('SF Control')
        e.tick(10); e.run('Alarm-3')
        self.assertEqual(e.READPOINT('VP_FWU_SF_Comm_Fault'), 0)
        self.assertEqual(e.READPOINT('VP_FWU_ATS_Comm_Fault'), 0)
        e.tick(1); e.run('Alarm-3'); e.run('SF Control')
        self.assertEqual(e.READPOINT('VP_FWU_SF_Comm_Fault'), 1)
        self.assertEqual(e.READPOINT('VP_FWU_ATS_Comm_Fault'), 1)
        self.assertGreater(e.READPOINT('FWU_SF-1_4_SPEED_CONTROL'), 0)
        self.assertEqual(e.READPOINT('FWU_SF-1.Target_RPM_Set'), 0)
        e.point_alarms.clear(); e.run('Alarm-3')
        self.assertEqual(e.READPOINT('VP_FWU_SF_Comm_Fault'), 0)
        self.assertEqual(e.READPOINT('VP_FWU_ATS_Comm_Fault'), 0)
        e.tick(6); e.run('SF Control')
        self.assertEqual(e.READPOINT('FWU_SF-1_4_SPEED_CONTROL'), 0)
        self.assertGreater(e.READPOINT('FWU_SF-1.Target_RPM_Set'), 0)

    def test_smoke_option_confirmation_and_auto_clear(self):
        for action in (0, 1):
            with self.subTest(action=action):
                e = Engine()
                e.set('VP_FWU_Smoke_Action_Set', action)
                e.set('FWU_PICV_CONTROL', 70, 5)
                e.set('FWU_FIRE_ALARM', 1)
                e.run('Remote Shutdown'); e.tick(3); e.run('Remote Shutdown')
                self.assertEqual(e.READPOINT('VP_FWU_Fire_Alarm'), 0)
                e.tick(1); e.run('Remote Shutdown')
                self.assertEqual(e.READPOINT('VP_FWU_Fire_Alarm'), 1)
                self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 0 if action else 70)
                e.set('FWU_FIRE_ALARM', 0); e.run('Remote Shutdown')
                self.assertEqual(e.READPOINT('VP_FWU_Fire_Alarm'), 0)
                self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 70)

    def test_shutdown_applies_in_all_modes_and_p1_wins(self):
        for local_remote in (0, 1):
            for operation in (0, 1):
                with self.subTest(remote=local_remote, operation=operation):
                    e = Engine()
                    e.set('REMOTE_SELECTION', local_remote)
                    e.set('VP_FWU_Operation_Mode', operation)
                    e.set('VP_FWU_Remote_Shutdown_Command', 1)
                    e.set('FWU_PICV_CONTROL', 75, 5)
                    e.set('FWU_PICV_CONTROL', 20, 1)  # Distinct synthetic P1 to test priority.
                    e.run('Remote Shutdown')
                    self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 20)
                    e.RELEASE_PRI('FWU_PICV_CONTROL', 1)
                    self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 0)
                    for i in range(1, 9):
                        self.assertEqual(e.READPOINT(f'FWU_SF-{i}.Run_Command'), 0)

    def test_shutdown_release_retains_higher_priority_command_and_damper_sequence(self):
        e = self.e
        e.set('VP_FWU_Command', 1, 5)
        e.set('FWU_PICV_CONTROL', 75, 5)
        e.set('FWU_SAD-1_4_COMMAND', 1, 5)
        e.set('VP_FWU_SF_Status', 1)
        e.set('VP_FWU_Remote_Shutdown_Command', 1)
        e.run('Remote Shutdown')
        self.assertEqual(e.READPOINT('VP_FWU_Command'), 1)
        self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 0)
        self.assertEqual(e.READPOINT('FWU_SAD-1_4_COMMAND'), 1)
        e.set('VP_FWU_SF_Status', 0); e.run('Remote Shutdown')
        self.assertEqual(e.READPOINT('FWU_SAD-1_4_COMMAND'), 0)
        e.set('VP_FWU_Remote_Shutdown_Command', 0); e.run('Remote Shutdown')
        self.assertEqual(e.READPOINT('FWU_PICV_CONTROL'), 75)
        self.assertEqual(e.READPOINT('FWU_SAD-1_4_COMMAND'), 1)

    def test_failover_three_causes_delay_and_stop_once(self):
        for cause in ('SAD_Not_Open', 'SAD_Full_Close', 'SF_Failure'):
            with self.subTest(cause=cause):
                e = Engine()
                e.set('VP_FWU_Command', 1)
                e.set(f'VP_FWU_{cause}_Alarm', 1)
                e.run('Failover'); e.tick(5); e.run('Failover')
                self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 0)
                e.tick(1); e.run('Failover')
                self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 1)
                self.assertEqual(e.READPOINT('VP_FWU_Command'), 0)
                e.WRITEPOINT_PRI('VP_FWU_Command', 1, 11)
                e.writes.clear(); e.tick(10); e.run('Failover')
                self.assertEqual(e.writes, [])
                self.assertEqual(e.READPOINT('VP_FWU_Command'), 1)

    def test_failover_latch_reset_and_reset_hold(self):
        e = self.e
        e.set('VP_FWU_SF_Failure_Alarm', 1)
        e.run('Failover'); e.tick(6); e.run('Failover')
        e.set('VP_FWU_Failover_Reset', 1)
        e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 1)
        e.set('VP_FWU_SF_Failure_Alarm', 0)
        e.set('VP_FWU_Failover_Reset', 0); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 1)
        e.set('VP_FWU_Failover_Reset', 1); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 0)
        e.tick(5); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Reset'), 1)
        e.tick(1); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Reset'), 0)

    def test_failover_excludes_group_and_individual_new_alarms(self):
        e = self.e
        e.set('VP_FWU_Group_Control_Mode', 1)
        e.set('VP_FWU_Command', 0)
        for i in range(1, 5):
            e.set(f'VP_FWU_PICV-{i}_Alarm', 1)
            e.set(f'VP_FWU_SAD-{i}_Signal_Conflict_Alarm', 1)
            e.set(f'VP_FWU_SAD-{i}_Position_Unknown_Alarm', 1)
        e.run('Failover'); e.tick(200); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 0)

    def test_failover_p11_does_not_override_p5_and_reset_writer_must_release(self):
        e = self.e
        e.set('VP_FWU_Command', 1, 5)
        e.set('VP_FWU_SF_Failure_Alarm', 1)
        e.run('Failover'); e.tick(6); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Command'), 1)
        self.assertEqual(e.values['VP_FWU_Command'][11], 0)
        e.set('VP_FWU_SF_Failure_Alarm', 0)
        e.set('VP_FWU_Failover_Reset', 1, 5)
        e.run('Failover'); e.tick(6); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Reset'), 1)
        self.assertEqual(e.values['VP_FWU_Failover_Reset'][11], 0)
        e.RELEASE_PRI('VP_FWU_Failover_Reset', 5)
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Reset'), 0)

    def test_interrupted_failover_condition_restarts_delay(self):
        e = self.e
        e.set('VP_FWU_SF_Failure_Alarm', 1); e.run('Failover')
        e.tick(4); e.set('VP_FWU_SF_Failure_Alarm', 0); e.run('Failover')
        e.set('VP_FWU_SF_Failure_Alarm', 1); e.run('Failover')
        e.tick(5); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 0)
        e.tick(1); e.run('Failover')
        self.assertEqual(e.READPOINT('VP_FWU_Failover_Alarm'), 1)

if __name__ == '__main__':
    unittest.main()
