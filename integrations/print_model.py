import re


def escape(text):
    """Escape the characters that have a special meaning in Telegram's MarkdownV2."""
    escape_chars = r'_*\[\]()~>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', str(text))


def hours_and_minutes(number):
    hours = int(number)
    minutes = int((number - hours) * 60)
    return f"{hours}h {minutes}min"


class PrintModel:
    def __init__(self, page_name, hours_to_start, league, home_team, away_team, bet_type, mod, price, bet_class,
                 placed_count, placed_price="NaN"):
        self.page_name = page_name
        self.hours_to_start = hours_to_start
        self.league = league
        self.bet_type = bet_type
        self.home_team = home_team
        self.away_team = away_team
        self.display_team = home_team
        self.mod = mod
        self.price = price
        self.bet_class = bet_class
        self.placed_count = placed_count
        self.placed_price = placed_price

        self.remodel_based_on_bet_data(bet_class, bet_type, mod, away_team)

    def get_markdown(self):
        formatted_time = hours_and_minutes(self.hours_to_start)
        return f"__{escape(self.page_name)}__\n" \
               f"{self.get_placed_text()}" \
               f"_\\({escape(formatted_time)}\\)_\n" \
               f"*{escape(self.league)}*\n" \
               f"{escape(self.home_team)} / {escape(self.away_team)}" \
               f" \\- {escape(self.what_to_display())} {escape(self.get_sign())}{escape(self.display_mod())}@ {escape(self.price)}\n"

    def remodel_based_on_bet_data(self, bet_class, bet_type, mod, away_team):
        parsed_bet_class = str.lower(bet_class).strip()
        parsed_bet_type = str.lower(str(bet_type)).strip()
        bet_changed = False

        if parsed_bet_class == "ah" or parsed_bet_class == "asian_handicap":
            bet_changed = True

        if parsed_bet_type == "2" and "1x2" not in parsed_bet_class and "ml" not in parsed_bet_class and "asian" not in parsed_bet_class and "ah" not in parsed_bet_class and "asian_handicap" not in parsed_bet_class:
            self.mod = mod * -1
            bet_changed = True

        if parsed_bet_type == "2" and "1x2" not in parsed_bet_class and "ml":
            self.display_team = away_team
            bet_changed = True

        if "ou" in parsed_bet_class or "overunder" in parsed_bet_class or "overunder_corners" in parsed_bet_class:
            if mod.is_integer():  # Check if the mod value is a whole number
                self.mod = format(int(mod), "d")
                bet_changed = True
            if parsed_bet_type == "o" or parsed_bet_type == "corners_o":
                self.bet_type = "Over"
                bet_changed = True
            if parsed_bet_type == "u" or parsed_bet_type == "corners_u":
                self.bet_type = "Under"
                bet_changed = True

        if "asian_corners" in parsed_bet_class:
            if parsed_bet_type == "corners_2":
                self.display_team = away_team
            if mod.is_integer():  # Check if the mod value is a whole number
                self.mod = format(int(mod), "d")
                bet_changed = True

        if "1x2" in parsed_bet_class or "ml" in parsed_bet_class:
            self.mod = -0.5
            bet_changed = True
            if parsed_bet_type == "l":
                self.display_team = away_team
            if parsed_bet_type == "2":
                self.display_team = away_team
            if parsed_bet_type == "x" or parsed_bet_type == "d":
                self.mod = 0
                self.display_team = "Draw"

        if "asian" in parsed_bet_class:
            bet_changed = True

        if not bet_changed:
            self.page_name = "Error: bet not changed"

    def get_sign(self):
        parsed_bet_class = str.lower(self.bet_class).strip()
        # check if mod is null, then replace it with number null
        if self.mod is None:
            self.mod = 0
        if float(self.mod) > 0:
            if "ou" in parsed_bet_class or "overunder" in parsed_bet_class or "overunder_corners" in parsed_bet_class or "asian_corners" in parsed_bet_class:
                return ""
            return "+"
        return ""

    def display_mod(self):
        parsed_bet_class = str.lower(self.bet_class).strip()
        parsed_bet_type = str.lower(str(self.bet_type)).strip()
        if "1x2" in parsed_bet_class:
            if parsed_bet_type == "x" or parsed_bet_type == "d":
                return ""
        if "asian_corners" in parsed_bet_class:
            if parsed_bet_type == "corners_2":
                return str(self.mod) + " Corner Handicap "
            if parsed_bet_type == "corners_1":
                return str(self.mod) + " Corners "
        if "corners_ou" in parsed_bet_class or "overunder_corners" in parsed_bet_class:
            return str(self.mod) + " Corners "
        return str(self.mod) + " "

    def what_to_display(self):
        parsed_bet_class = str.lower(self.bet_class).strip()
        if "ou" in parsed_bet_class or "overunder" in parsed_bet_class or "overunder_corners" in parsed_bet_class:
            return self.bet_type
        return self.display_team

    def get_placed_text(self):
        if self.placed_count == 0:
            return "\n"
        return f"_Already placed before @ {escape(self.placed_price)}_\n\n"
