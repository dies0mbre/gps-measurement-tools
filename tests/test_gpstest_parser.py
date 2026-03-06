import unittest

from gpstest_parser import parse_gpstest_log


class GpsTestParserTests(unittest.TestCase):
    def test_parses_metadata_and_raw_rows(self) -> None:
        result = parse_gpstest_log("opensource/demoFiles/pseudoranges_log_2016_08_22_14_45_50.txt")

        self.assertEqual(result.version, "1.4.0.0")
        self.assertEqual(result.platform, "N")
        self.assertIn("Raw", result.records)
        self.assertGreater(len(result.records["Raw"]), 0)

        first = result.records["Raw"][0]
        self.assertIn("TimeNanos", first)
        self.assertIsInstance(first["TimeNanos"], int)
        self.assertIn("PseudorangeRateMetersPerSecond", first)
        self.assertIsInstance(first["PseudorangeRateMetersPerSecond"], float)

    def test_parses_fix_rows(self) -> None:
        result = parse_gpstest_log("opensource/demoFiles/pseudoranges_log_2016_08_22_14_45_50.txt")

        self.assertIn("Fix", result.records)
        self.assertGreater(len(result.records["Fix"]), 0)
        first_fix = result.records["Fix"][0]
        self.assertEqual(first_fix["Provider"], "gps")
        self.assertIsInstance(first_fix["Latitude"], float)


if __name__ == "__main__":
    unittest.main()
