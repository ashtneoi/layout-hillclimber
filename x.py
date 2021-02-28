#!/usr/bin/env python


from random import shuffle, randrange


def get_ngrams(maxlen):
    n = [{}]
    with open("ngrams-all.tsv") as f:
        unread = None
        for i in range(1, maxlen + 1):
            header = f.readline() if unread is None else unread
            unread = None
            kind, splats, _ = header.split("\t", 2)
            assert kind == f"{i}-gram"
            assert splats == "*/*"
            igrams = {}
            for line in f:
                igram, count, _ = line.split("\t", 2)
                if igram.endswith("-gram"):
                    unread = line
                    break
                igrams[igram] = int(count)
            n.append(igrams)
    return n


def strength_score(ngrams, char_to_strength):
    score = 0
    for igram, count in ngrams[1].items():
        for c in igram:
            score += count * char_to_strength[c]
    return score


def inward_roll_score(ngrams, char_to_key):
    score = 0
    for i, igrams in enumerate(ngrams[2:], 2):
        for igram, count in igrams.items():
            rows = []
            prev_col = -1
            for c in igram:
                key = char_to_key.get(c)
                if key is None:
                    raise Exception(f"can't type {igram}")
                row, col = key
                if row == 0:
                    break
                if (prev_col <= 3 and col <= prev_col) \
                        or (prev_col >= 4 and col >= prev_col):
                    if col == prev_col:
                        score -= count * i
                    break
                rows.append(row)
            else:
                if not(1 in rows and 3 in rows):
                    score += count * i
    return score


def layout_score(ngrams, layout, print_details=False):
    char_to_key = {}
    for r, row in enumerate(layout):
        for c, char in enumerate(row):
            char_to_key[char] = (r, c)

    strength = [
        (0, 1, 2, 2, 2, 2, 1, 0),
        (3, 5, 8, 6, 6, 8, 5, 3),
        (5, 7, 8, 8, 8, 8, 7, 5),
        (3, 1, 4, 7, 7, 4, 1, 3),
    ]
    char_to_strength = {}
    for layout_row, strength_row in zip(layout, strength):
        for char, strength_num in zip(layout_row, strength_row):
            char_to_strength[char] = int(strength_num)
    irs = inward_roll_score(ngrams, char_to_key)
    ss = strength_score(ngrams, char_to_strength)
    if print_details:
        print(f"irs = {irs:_}; ss = {ss:_}")
    return 20 * irs + ss


def random_swap(layout):
    keys = []
    chars = []
    for _ in range(randrange(2, 8)):
        while True:
            row = randrange(len(layout))
            col = randrange(len(layout[0]))
            if (row, col) not in keys:
                break
        keys.append((row, col))
        chars.append(layout[row][col])
    assert len(keys) == len(chars)
    shuffle(keys)
    new_layout = layout.copy()
    for char, key in zip(chars, keys):
        row, col = key
        new_layout[row] = new_layout[row][:col] + char + new_layout[row][col+1:]
    return new_layout


def search(ngrams, start_layout, max_attempts):
    total_attempts = 0
    attempts = [0] * len(max_attempts)
    best = [(0, None)] * len(max_attempts)  # (score, layout)
    best[0] = (layout_score(ngrams, start_layout), start_layout)
    level = 0

    invalid_layout = ["'-------"] * 4
    failed = 0

    try:
        while level >= 0:
            while level < len(max_attempts) - 1:
                level += 1
                _, lower_best_layout = best[level - 1]
                best[level] = 0, lower_best_layout

            layout = invalid_layout
            while layout[0].count("-") != 5 or "'" in layout[0]:
                layout = random_swap(best[level][1])
            score = layout_score(ngrams, layout)
            if score > best[level][0]:
                print()
                print(f"failed = {failed}")
                failed = 0
                print()
                print("\n".join(layout))
                print(f"{score:_}")
                best[level] = (score, layout)
            else:
                failed += 1
            # print("\n".join(best[level][1]))
            attempts[level] += 1
            total_attempts += 1

            while attempts[level] >= max_attempts[level]:
                print()
                print("\n".join(best[level][1]))
                print(f"{best[level][0]:_}")
                print()
                print("<" * (level+1))
                attempts[level] = 0
                if level == 0:
                    level = -1
                    break
                level -= 1
                attempts[level] += 1
                lower_best_score, _ = best[level]
                upper_best_score, upper_best_layout = best[level + 1]
                if upper_best_score > lower_best_score:
                    best[level] = (upper_best_score, upper_best_layout)
    except KeyboardInterrupt:
        print()
        return total_attempts, max(best, key=lambda x: x[0])

    return total_attempts, best[0]



def main():
    import sys

    ngrams = get_ngrams(4)

    not_qxz = "ABCDEFGHIJKLMNOPRSTUVWY'"
    assert len(not_qxz) == 26 + 1 - 3
    not_qxz_split = list(not_qxz)
    shuffle(not_qxz_split)
    not_qxz = "".join(not_qxz_split)
    qxz = "QXZ-----"
    qxz_split = list(qxz)
    shuffle(qxz_split)
    qxz = "".join(qxz_split)

    starting_layout = [
        qxz,
        not_qxz[0:8],
        not_qxz[8:16],
        not_qxz[16:24],
    ]

    max_attempts = list(map(int, sys.argv[1:]))

    total_attempts, best = search(ngrams, starting_layout, max_attempts)
    print()
    print("Best:")
    print()
    print("\n".join(best[1]))
    print(f"{best[0]:_}")
    layout_score(ngrams, best[1], print_details=True)
    print(f"attempts: {total_attempts:_} / {max_attempts}")


if __name__ == "__main__":
    main()
