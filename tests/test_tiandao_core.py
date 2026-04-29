"""
天道核心系统测试
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import unittest
from tiandao_core.core.y_value import YValueSystem, YValueConfig, TriggerType, CompensationType
from tiandao_core.core.mbti import MBTISystem, MBTIType
from tiandao_core.core.profile import CharacterProfile
from tiandao_core.rendao.weight_network import WeightNetwork, CharacterClass
from tiandao_core.rendao.lao_tian_qi import LaoTianQi, ActionValue


class TestYValueSystem(unittest.TestCase):
    """Y值系统测试"""

    def test_y_value_creation(self):
        config = YValueConfig(base_y=70)
        y = YValueSystem(config)
        self.assertEqual(y.Y, 70)
        self.assertEqual(y.state.baseline_y, 70)

    def test_breakthrough_trigger(self):
        config = YValueConfig(base_y=70)
        y = YValueSystem(config)

        result = y.trigger_breakthrough(95, 60)
        self.assertTrue(result.triggered)
        self.assertEqual(y.state.is_compensating, True)
        self.assertEqual(y.state.compensation_type, CompensationType.BREAKTHROUGH_COMP)

    def test_no_breakthrough_below_threshold(self):
        config = YValueConfig(base_y=70)
        y = YValueSystem(config)

        result = y.trigger_breakthrough(75, 65)
        self.assertFalse(result.triggered)

    def test_compensation_and_rebound(self):
        config = YValueConfig(base_y=70)
        y = YValueSystem(config)

        y.trigger_breakthrough(95, 60)

        for i in range(5):
            y.process_compensation()
            y.process_rebound()

        self.assertFalse(y.state.is_compensating)


class TestMBTISystem(unittest.TestCase):
    """MBTI系统测试"""

    def test_mbti_creation(self):
        mbti = MBTISystem('INTJ')
        self.assertEqual(mbti.mbti_type, 'INTJ')

    def test_mbti_full_profile(self):
        mbti = MBTISystem('ENTP')
        profile = mbti.get_full_profile()
        self.assertEqual(profile['mbti_type'], 'ENTP')
        self.assertIn('big_five', profile)

    def test_baseline_y_from_mbti(self):
        mbti = MBTISystem('INTJ')
        baseline = mbti.get_baseline_y()
        self.assertIsInstance(baseline, int)
        self.assertGreater(baseline, 0)


class TestCharacterProfile(unittest.TestCase):
    """角色画像测试"""

    def test_create_profile(self):
        profile = CharacterProfile.create('test_char', '测试角色', 70, 'ENTP')
        self.assertEqual(profile.info.name, '测试角色')
        self.assertEqual(profile.info.mbti_type, 'ENTP')

    def test_calculate_response(self):
        profile = CharacterProfile.create('test', '测试', 65, 'ENTP')
        result = profile.calculate_response('主角遇到强敌', interaction_y=80)
        self.assertIn('y_value', result)
        self.assertIn('emotional_state', result)


class TestWeightNetwork(unittest.TestCase):
    """权重关系网测试"""

    def test_register_characters(self):
        wn = WeightNetwork()
        wn.register_character('主角', CharacterClass.PROTAGONIST, 90)
        wn.register_character('反派', CharacterClass.ANTAGONIST, 85)
        wn.register_character('配角', CharacterClass.MAIN, 60)

        summary = wn.get_network_summary()
        self.assertEqual(summary['total_characters'], 3)

    def test_weight_rankings(self):
        wn = WeightNetwork()
        wn.register_character('主角', CharacterClass.PROTAGONIST, 90)
        wn.register_character('反派', CharacterClass.ANTAGONIST, 85)
        wn.register_character('配角', CharacterClass.MAIN, 60)

        rankings = wn.get_weight_rankings(10)
        self.assertEqual(rankings[0][0], '主角')
        self.assertEqual(rankings[0][1], 90)


class TestLaoTianQi(unittest.TestCase):
    """老天气变量测试"""

    def test_evaluate_action(self):
        ltq = LaoTianQi()
        judgment = ltq.evaluate_action('帮助陌生人', 'ENFP', 70)
        self.assertIsInstance(judgment.action_value, ActionValue)


if __name__ == '__main__':
    unittest.main()
