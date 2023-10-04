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
        if "ah" in str.lower(bet_class) and str(bet_type) == "2":
            self.mod = mod * -1
            self.display_team = away_team

        if "ou" in str.lower(bet_class):
            if mod.is_integer():  # Check if the mod value is a whole number
                self.mod = format(int(mod), "d")
            if str.lower(bet_type) == "o":
                self.bet_type = "Over"
            if str.lower(bet_type) == "u":
                self.bet_type = "Under"

        if "1x2" in str.lower(bet_class):
            if str(bet_type) == "1":
                self.mod = -0.5
            if str(bet_type) == "2":
                self.mod = -0.5
                self.display_team = away_team
            if str.lower(str(bet_type)) == "x":
                self.mod = 0
                self.display_team = "Draw"

    def get_sign(self):
        # check if mod is null, then replace it with number null
        if self.mod is None:
            self.mod = 0
        if float(self.mod) > 0:
            if "ou" in str.lower(self.bet_class):
                return ""
            return "+"
        return ""

    def display_mod(self):
        if "1x2" in str.lower(self.bet_class):
            if str.lower(str(self.bet_type)) == "x":
                return ""
        if "corners_ou" in str.lower(self.bet_class):
            return str(self.mod) + " Corners "
        return str(self.mod) + " "

    def what_to_display(self):
        if "ou" in str.lower(self.bet_class):
            return self.bet_type
        return self.display_team

    def get_placed_text(self):
        if self.placed_count == 0:
            return "\n"
        return f"_Already placed before @ {escape(self.placed_price)}_\n\n"
