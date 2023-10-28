selected_fields = ['pin_fix', 'league', 'home_team', 'away_team', 'bet_class', 'bet_type', 'mod', 'price']


def compute_bet_model_hash(bet):
    # Create a copy without the fields to discard
    item_copy = {k: v for k, v in bet.items() if k in selected_fields}
    return str(hash(frozenset(item_copy.items())))

