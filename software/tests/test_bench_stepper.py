"""Offline tests; does not import the application or access hardware."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

spec = importlib.util.spec_from_file_location(
    'bench', Path(__file__).resolve().parents[1] / 'scripts' / 'bench_stepper.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


class BenchTests(unittest.TestCase):
    def test_sensor_decode_and_fault_bits(self):
        bus = Mock()
        bus.read_i2c_block_data.return_value = [0x20, 0x0F, 0xFF]
        reading = bench.read_sensor(bus)
        self.assertEqual(reading['raw'], 4095)
        self.assertTrue(bench.magnet_ok(reading))
        for status in (0, 0x30, 0x28):
            bus.read_i2c_block_data.return_value = [status, 0, 0]
            self.assertFalse(bench.magnet_ok(bench.read_sensor(bus)))

    def test_stop_attempts_deenergize_after_halt_failure(self):
        with patch.object(bench, 'tic', side_effect=[OSError('USB lost'), '']) as call:
            self.assertFalse(bench.stop(Mock()))
        self.assertEqual(call.call_args_list[1].args[1], '--deenergize')

    def test_motion_requires_explicit_flag(self):
        with patch('sys.argv', ['bench', 'jog', '--serial', '123']), \
                self.assertRaises(SystemExit) as raised:
            bench.main()
        self.assertEqual(raised.exception.code, 2)


if __name__ == '__main__':
    unittest.main()
