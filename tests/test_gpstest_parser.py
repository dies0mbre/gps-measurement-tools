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

    def test_wrapper_get_records_and_select(self) -> None:
        result = parse_gpstest_log("opensource/demoFiles/pseudoranges_log_2016_08_22_14_45_50.txt")

        raw_rows = result.get_records("Raw")
        self.assertGreater(len(raw_rows), 0)

        selected = result.select("Fix", ["Provider", "Latitude", "Longitude"])
        self.assertGreater(len(selected), 0)
        self.assertEqual(set(selected[0].keys()), {"Provider", "Latitude", "Longitude"})
        self.assertEqual(selected[0]["Provider"], "gps")


if __name__ == "__main__":
    unittest.main()
