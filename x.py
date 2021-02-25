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
    return ncsfu_score(ngrams, char_to_key)


def layout_score2(ngrams, layout):
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


def search(ngrams, layout, best_best_score, best_best_layout):
    failed = 0
    best_score = 0
    while failed < 100:
        new_layout = [""]
        while new_layout[0].count("-") != 5:
            new_layout = random_swap(layout)
        score = layout_score2(ngrams, new_layout)
        if score <= best_score:
            failed += 1
        else:
            layout = new_layout
            best_score = score
            if score > best_best_score[0]:
                best_best_layout[0] = layout
                best_best_score[0] = score
            print()
            print(f"failed: {failed}")
            print()
            print("\n".join(layout))
            print(f"{score} / {best_best_score[0]}")
            failed = 0


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

    best_best_score = [0]
    best_best_layout = [starting_layout]

    try:
        while True:
            print()
            print("\n".join(best_best_layout[0]))
            print(best_best_score[0])
            layout = best_best_layout[0]
            for _ in range(4):
                search(ngrams, layout, best_best_score, best_best_layout)
                print()
                print("<<<")
            print()
            print("<<<<<<<<<<<<<<<<")
    except KeyboardInterrupt:
        print()
        print()
        print("Best best layout:")
        print("\n".join(best_best_layout[0]))
        print(best_best_score[0])


if __name__ == "__main__":
    main()
