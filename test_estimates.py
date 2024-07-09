import unittest
import asyncio
from testmain_er import generate_fs_estimate, generate_fr_estimate, generate_se_report, generate_is_report, generate_ss_report

class TestEstimates(unittest.TestCase):

    def test_generate_fs_estimate(self):
        # Run the test method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(generate_fs_estimate())

        # Assertions
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIsNotNone(result[0], "summary_text should not be None")
        self.assertIsNotNone(result[1], "email_summary should not be None")
        self.assertIsNotNone(result[2], "full_evidence should not be None")
        # self.assertIsNotNone(result[3], "audio_url should not be None")
        self.assertIsNotNone(result[4], "full_arguments should not be None")
        self.assertIsNotNone(result[5], "differences should not be None")

    def test_generate_fr_estimate(self):
        # Run the test method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(generate_fr_estimate())

        # Assertions
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIsNotNone(result[0], "summary_text should not be None")
        self.assertIsNotNone(result[1], "email_summary should not be None")
        self.assertIsNotNone(result[2], "full_evidence should not be None")
        # self.assertIsNotNone(result[3], "audio_url should not be None")
        self.assertIsNotNone(result[4], "full_arguments should not be None")
        self.assertIsNotNone(result[5], "differences should not be None")

    def test_generate_se_report(self):
        # Run the test method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(generate_se_report())

        # Assertions
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIsNotNone(result[0], "summary_text should not be None")
        self.assertIsNotNone(result[1], "email_summary should not be None")
        self.assertIsNotNone(result[2], "full_evidence should not be None")
        # self.assertIsNotNone(result[3], "audio_url should not be None")
        self.assertIsNotNone(result[4], "full_arguments should not be None")
        self.assertIsNotNone(result[5], "differences should not be None")

    def test_generate_is_report(self):
        # Run the test method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(generate_is_report())

        # Assertions
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIsNotNone(result[0], "summary_text should not be None")
        self.assertIsNotNone(result[1], "email_summary should not be None")
        self.assertIsNotNone(result[2], "full_evidence should not be None")
        # self.assertIsNotNone(result[3], "audio_url should not be None")
        self.assertIsNotNone(result[4], "full_arguments should not be None")
        self.assertIsNotNone(result[5], "differences should not be None")

    def test_generate_ss_report(self):
        # Run the test method
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(generate_ss_report())

        # Assertions
        self.assertIsNotNone(result, "Result should not be None")
        self.assertIsNotNone(result[0], "summary_text should not be None")
        self.assertIsNotNone(result[1], "email_summary should not be None")
        self.assertIsNotNone(result[2], "full_evidence should not be None")
        # self.assertIsNotNone(result[3], "audio_url should not be None")
        self.assertIsNotNone(result[4], "full_arguments should not be None")
        self.assertIsNotNone(result[5], "differences should not be None")

if __name__ == '__main__':
    unittest.main()
