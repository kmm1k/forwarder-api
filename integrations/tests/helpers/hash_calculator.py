fields_to_discard = ['placed_count', 'hours_to_start']


def compute_bet_model_hash(bet):
    # Create a copy without the fields to discard
    item_copy = {k: v for k, v in bet.items() if k not in fields_to_discard}
    return str(hash(frozenset(item_copy.items())))

