def parse_file(path):
    with open(path) as fh:
        lines = fh.readlines()
    deck_dict = {}
    attributes = ['name', 'number', 'type', 'cost', 'power', 'toughness', 'rules']
    for line in lines[1:]:
        items = line.strip().split('\t')
        inner_dict = {}
        for i, val in enumerate(items):
            if attributes[i] == 'cost':
                val = parse_cost(val)
            if attributes[i] in ['number', 'power', 'toughness']:
                try:
                    val = int(val)
                except ValueError:
                    pass
            inner_dict[attributes[i]] = val
        deck_dict[items[0]] = inner_dict
    return deck_dict

def parse_cost(costs):
    costs_split = costs.split(' ')
    cost_dict = {}
    colors = set("BWGRUX")
    for cost in costs_split:
        if set(cost).issubset(colors) and cost not in cost_dict:
           cost_dict[cost] = 1
        elif set(cost).issubset(colors) and cost in cost_dict:
            cost_dict[cost] += 1
        elif cost.isnumeric():
            cost_dict['colorless'] = int(cost)
        else:
            raise ValueError
    return cost_dict

