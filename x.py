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


def ncsfu_score(ngrams, char_to_finger):
    score = 0
    for _i, igrams in enumerate(ngrams[2:], 2):
        # print(f"Scoring {i}-grams")
        for igram, count in igrams.items():
            fingers = []
            for c in igram:
                finger = char_to_finger.get(c)
                if finger is None:
                    raise Exception(f"can't type {igram}")
                if finger in fingers:
                    break
                fingers.append(finger)
            else:
                score += count
    return score


def layout_score(ngrams, layout):
    char_to_finger = {}
    for row in layout:
        char_to_finger[row[0]] = 0
        char_to_finger[row[1]] = 1
        char_to_finger[row[2]] = 2
        char_to_finger[row[3]] = 3
        char_to_finger[row[4]] = 3
        char_to_finger[row[5]] = 4
        char_to_finger[row[6]] = 4
        char_to_finger[row[7]] = 5
        char_to_finger[row[8]] = 6
        char_to_finger[row[9]] = 7
    return ncsfu_score(ngrams, char_to_finger)


def random_swap(layout):
    keys = []
    chars = []
    for _ in range(randrange(2, 6)):
        for _ in range(100):
            row = randrange(3)
            col = randrange(10)
            if (row, col) not in keys:
                break
        else:
            raise Exception("what?")
        keys.append((row, col))
        chars.append(layout[row][col])
    assert len(keys) == len(chars)
    shuffle(keys)
    new_layout = layout.copy()
    for char, key in zip(chars, keys):
        row, col = key
        new_layout[row] = new_layout[row][:col] + char + new_layout[row][col+1:]
    return new_layout


def main():
    ngrams = get_ngrams(3)

    print(layout_score(ngrams, [
        "QWERTYUIOP",
        "ASDFGHJKL-",
        "ZXCVBNM---",
    ]))
    print()

    layout = [
        "QDRWBJFUP-",
        "ASHTGYNEOI",
        "ZXMCVKL---",
    ]
    max_score = layout_score(ngrams, layout)
    print("\n".join(layout))
    print(max_score)

    failed = 0
    while True:
        new_layout = random_swap(layout)
        score = layout_score(ngrams, new_layout)
        if score <= max_score:
            failed += 1
        else:
            layout = new_layout
            max_score = score
            print()
            print(f"failed: {failed}")
            print()
            print("\n".join(layout))
            print(score)
            failed = 0


if __name__ == "__main__":
    main()
