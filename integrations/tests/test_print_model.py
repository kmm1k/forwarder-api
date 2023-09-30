import unittest

from integrations.print_model import PrintModel


# Import PrintModel here...

class TestPrintModel(unittest.TestCase):

    def test_get_markdown_for_ah_class_bet_type_string_2(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "2", -0.5, 2.0, "ah")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\+0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ah_class_bet_type_int_2(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 2, -0.5, 2.0, "ah")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\+0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ah_class_bet_type_1(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 1, 0, 1.9, "ah")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam 0 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_class_over(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "o", 2.5, 1.9, "ou")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Over 2\\.5 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_class_under(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "u", 2.25, 1.9, "ou")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 2\\.25 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_home_win(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "1", -0.5, 2.0, "1x2")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam \\-0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_away_win(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "2", -0.5, 1.9, "1x2")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_draw(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "x", 0, 3.0, "1x2")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw @ 3\\.0\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_sus1x2_case_home(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 1, 0, 2.9, "1x2")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam \\-0\\.5 @ 2\\.9\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_sus1x2_case_away(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 2, 0, 2.9, "1x2")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 2\\.9\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_with_text(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "U", 10.5, 2.0, "corners_ou")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 10\\.5 Corners @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_another_ou_testcase(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "U", 4.0, 1.85, "ou")
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 4 @ 1\\.85\n"
        self.assertEqual(model.get_markdown(), expected_output)


if __name__ == '__main__':
    unittest.main()
