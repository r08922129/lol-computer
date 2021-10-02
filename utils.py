from nltk import edit_distance

def match_champion_name(name, champion_names):
    name = name.lower()
    champion_names = [champion_name.lower() for champion_name in champion_names]

    candidates = []
    # find the same name
    for champion_name in champion_names:
        if name == champion_name:
            return champion_name
        if name in champion_name:
            candidates.append(champion_name)
    # failed to find exact name, test whether name if name
    # eg. nunu <-> nunu & willump
    if len(candidates) > 0:
        return get_most_similar_name(name, candidates)

    # find most similar name
    return get_most_similar_name(name, champion_names)

def get_most_similar_name(name, champion_names):
    distance = 1000
    for champion_name in champion_names:
        d = edit_distance(name, champion_name)
        if d < distance:
            distance = d
            most_similar_name = champion_name
    return most_similar_name
