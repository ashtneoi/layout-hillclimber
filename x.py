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


def ncsfu_score(ngrams, char_to_key):
    score = 0
    for i, igrams in enumerate(ngrams[2:], 2):
        # print(f"Scoring {i}-grams")
        for igram, count in igrams.items():
            fingers = []
            rows = []
            for c in igram:
                key = char_to_key.get(c)
                if key is None:
                    raise Exception(f"can't type {igram}")
                row, finger = key
                if row == 0:
                    break
                if finger in fingers:
                    break
                fingers.append(finger)
                rows.append(row)
            else:
                if not(1 in rows and 3 in rows):
                    score += count * i**2
    return score


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
                    break
                rows.append(row)
            else:
                if not(1 in rows and 3 in rows):
                    score += count * i
    return score


def hand_alternation_score(ngrams, char_to_key):
    score = 0
    for i, igrams in enumerate(ngrams[4:], 4):
        for igram, count in igrams.items():
            cols = []
            for c in igram:
                key = char_to_key.get(c)
                if key is None:
                    raise Exception(f"can't type {igram}")
                _, col = key
                cols.append(col)
            if not (all(c <= 3 for c in cols) or all(c >= 4 for c in cols)):
                score += count
    return score


def layout_score(ngrams, layout):
    char_to_key = {}
    for r, row in enumerate(layout):
        for c, char in enumerate(row):
            char_to_key[char] = (r, c)

    strength = [
        (0, 1, 2, 2, 2, 2, 1, 0),
        (2, 5, 8, 6, 6, 8, 5, 2),
        (4, 7, 8, 8, 8, 8, 7, 4),
        (2, 2, 4, 7, 7, 4, 2, 2),
    ]
    char_to_strength = {}
    for layout_row, strength_row in zip(layout, strength):
        for char, strength_num in zip(layout_row, strength_row):
            char_to_strength[char] = int(strength_num)
    return 10 * inward_roll_score(ngrams, char_to_key) \
        + strength_score(ngrams, char_to_strength)


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
    attempts = [0] * len(max_attempts)
    best = [(0, None)] * len(max_attempts)  # (score, layout)
    best[0] = (layout_score(ngrams, start_layout), start_layout)
    level = 0

    invalid_layout = ["'-------"] * 4
    failed = 0
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
            print(score)
            best[level] = (score, layout)
        else:
            failed += 1
        # print("\n".join(best[level][1]))
        attempts[level] += 1

        while attempts[level] >= max_attempts[level]:
            print()
            print("\n".join(best[level][1]))
            print(best[level][0])
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

    return best[0]



def main():
    ngrams = get_ngrams(3)

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

    best = search(ngrams, starting_layout, [4, 30, 60])
    print()
    print("\n".join(best[1]))
    print(best[0])


if __name__ == "__main__":
    main()
