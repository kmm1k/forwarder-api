import unittest

from integrations.print_model import PrintModel


# Import PrintModel here...

class TestPrintModel(unittest.TestCase):

    def test_get_markdown_for_ah_class_bet_type_string_2(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "2", -0.5, 2.0, "ah", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\+0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ah_class_bet_type_int_2(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 2, -0.5, 2.0, "ah", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\+0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ah_class_bet_type_1(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 1, 0, 1.9, "ah", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam 0 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_class_over(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "o", 2.5, 1.9, "ou", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Over 2\\.5 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_class_under(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "u", 2.25, 1.9, "ou", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 2\\.25 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_home_win(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "1", -0.5, 2.0, "1x2", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam \\-0\\.5 @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_away_win(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "2", -0.5, 1.9, "1x2", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 1\\.9\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_away_win_with_some_other_syntax(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", 2, None, 2.63, "1x2 ", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ml_class_away_lose(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", "L", None, 2.63, "ml", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ml_class_away_anything_else(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", "d", None, 2.63, "ml", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw 0 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ml_class_draw(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", "x", None, 2.63, "ml", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw 0 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_draw(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "x", 0, 3.0, "1x2", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw @ 3\\.0\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_sus1x2_case_home(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 1, 0, 2.9, "1x2", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam \\-0\\.5 @ 2\\.9\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_sus1x2_case_away(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", 2, 0, 2.9, "1x2", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 2\\.9\n"
        print(expected_output)
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_with_text(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "U", 10.5, 2.0, "corners_ou", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 10\\.5 Corners @ 2\\.0\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_another_ou_testcase(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "U", 4.0, 1.85, "ou", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 4 @ 1\\.85\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_another_ou_testcase_already_placed(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "U", 4.0, 1.85, "ou", 1, 0.5)
        expected_output = "__TestPage__\n_Already placed before @ 0\\.5_\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Under 4 @ 1\\.85\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_asian_bet_class_flipper(self):
        model = PrintModel("Bet365", 15.5, "Erovnuli Liga Georgia", "FC Telavi", "FC Saburtalo Tbilisi", 2, -0.25, 1.83, "asian", 0)
        expected_output = "__Bet365__\n\n_\\(15h 30min\\)_\n*Erovnuli Liga Georgia*\nFC Telavi / FC Saburtalo Tbilisi \\- FC Saburtalo Tbilisi \\+0\\.25 @ 1\\.83\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_random_bet_class_flipper(self):
        model = PrintModel("Bet365", 15.5, "Erovnuli Liga Georgia", "FC Telavi", "FC Saburtalo Tbilisi", 2, -0.25, 1.83, "randomx2", 0)
        expected_output = "__Bet365__\n\n_\\(15h 30min\\)_\n*Erovnuli Liga Georgia*\nFC Telavi / FC Saburtalo Tbilisi \\- FC Saburtalo Tbilisi \\+0\\.25 @ 1\\.83\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_1x2_class_away_win_with_ml(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", 2, None, 2.63, "ml", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- AwayTeam \\-0\\.5 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ml_class_draw_spaces(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", " x ", None, 2.63, " ml ", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw 0 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_d_class_draw(self):
        model = PrintModel("TestPage", 1.175, "TestLeague", "HomeTeam", "AwayTeam", "D", None, 2.63, "ml", 0)
        expected_output = "__TestPage__\n\n_\\(1h 10min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Draw 0 @ 2\\.63\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_asian_ou_with_text(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "corners_2", -3.0, 1.95, "asian_corners", 0)
        expected_output = "__TestPage__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- Corner Handicap \\-3\\.0 @ 1\\.95\n"
        self.assertEqual(model.get_markdown(), expected_output)

    def test_get_markdown_for_ou_with_random_text_should_show_err(self):
        model = PrintModel("TestPage", 2.5, "TestLeague", "HomeTeam", "AwayTeam", "corners_2", -3.0, 1.95, "random_corners", 0)
        expected_output = "__Error: bet not changed__\n\n_\\(2h 30min\\)_\n*TestLeague*\nHomeTeam / AwayTeam \\- HomeTeam \\-3\\.0 @ 1\\.95\n"
        self.assertEqual(model.get_markdown(), expected_output)


if __name__ == '__main__':
    unittest.main()
