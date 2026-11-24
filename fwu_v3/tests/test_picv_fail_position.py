"""PICV Control: SAT 센서 고장 시 밸브 마지막/안전 위치 선택 보호 기능 (JSY 2026-11-23, QTS RFP 2.3.E.7과는 별개)."""
import unittest
from test_control import Engine


class PicvFailPositionTests(unittest.TestCase):
    def setUp(self):
        self.e = Engine()
        # 자동 운전, 운전 명령 ON, 팬 운전 중, 비상정지 아님
        for p, v in [('FWU_EMERGENCY', 0), ('VP_FWU_Operation_Mode', 1), ('VP_FWU_Command', 1), ('VP_FWU_SF_Status', 1)]:
            self.e.set(p, v)

    def run_picv(self):
        self.e.run('PICV Control')

    def test_default_is_safe_position_100(self):
        # 기본값(Fail_Mode 1, Safe_Position 100)은 기존 동작과 같다
        self.assertEqual(self.e.READPOINT('VP_FWU_PICV_Fail_Mode'), 1)
        self.assertEqual(self.e.READPOINT('VP_FWU_PICV_Safe_Position'), 100)
        self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('FWU_PICV_CONTROL'), 100)

    def test_safe_position_follows_setting(self):
        self.e.set('VP_FWU_PICV_Fail_Mode', 1)
        self.e.set('VP_FWU_PICV_Safe_Position', 60)
        self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('FWU_PICV_CONTROL'), 60)
        self.assertEqual(self.e.values['FWU_PICV_CONTROL'][11], 60)   # P11에도 같은 값

    def test_last_position_keeps_previous_pi_output(self):
        # PI가 한 번 돈 뒤 SAT 고장 → 고장 직전 출력 유지 (안전 위치 60과 구분되게 설정)
        self.e.set('VP_FWU_PICV_Fail_Mode', 0)
        self.e.set('VP_FWU_PICV_Safe_Position', 60)
        self.run_picv()                                   # SAT 정상: PI 실행
        self.assertEqual(self.e.READPOINT('VP_FWU_PICV_PI_Started'), 1)
        before = self.e.READPOINT('FWU_PICV_CONTROL')
        self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('FWU_PICV_CONTROL'), before)
        self.assertNotEqual(before, 60)

    def test_last_mode_at_startup_goes_to_safe_position(self):
        # 운전 시작 직후 PI가 한 번도 안 돈 상태에서 SAT 고장 → 직전 명령이 없으므로 안전 위치
        self.e.set('VP_FWU_PICV_Fail_Mode', 0)
        self.e.set('VP_FWU_PICV_Safe_Position', 60)
        self.e.set('FWU_PICV_CONTROL', 37, 5)             # 이전 운전에서 남은 값
        self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('FWU_PICV_CONTROL'), 60)

    def test_pi_started_cleared_when_command_off(self):
        self.e.set('VP_FWU_PICV_Fail_Mode', 0)
        self.e.set('VP_FWU_PICV_Safe_Position', 60)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('VP_FWU_PICV_PI_Started'), 1)
        self.e.set('VP_FWU_Command', 0)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('VP_FWU_PICV_PI_Started'), 0)
        # 다시 운전 시작, PI 돌기 전에 SAT 고장 → 안전 위치
        self.e.set('VP_FWU_Command', 1)
        self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
        self.run_picv()
        self.assertEqual(self.e.READPOINT('FWU_PICV_CONTROL'), 60)

    def test_no_pi_control_while_sat_failed(self):
        for mode in (0, 1):
            self.e.loops.clear()
            self.e.set('VP_FWU_PICV_Fail_Mode', mode)
            self.e.set('VP_FWU_SAT_Failure_Alarm', 1)
            self.run_picv()
            self.assertEqual(self.e.loops, [])

    def test_sat_recovers_pi_control_resumes(self):
        self.e.set('VP_FWU_PICV_Fail_Mode', 0)
        self.e.set('VP_FWU_SAT_Failure_Alarm', 0)
        self.run_picv()
        self.assertEqual(len(self.e.loops), 1)


if __name__ == '__main__':
    unittest.main()
