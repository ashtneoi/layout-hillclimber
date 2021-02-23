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
        for i, col in enumerate(row):
            char_to_finger[col] = i
    return ncsfu_score(ngrams, char_to_finger)


def random_swap(layout):
    keys = []
    chars = []
    for _ in range(randrange(2, 6)):
        for _ in range(100):
            row = randrange(len(layout))
            col = randrange(len(layout[0]))
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


def search(ngrams, layout, best_best_score, best_best_layout):
    failed = 0
    best_score = 0
    while failed < 400:
        new_layout = [""]
        while new_layout[0].count("-") != 5:
            new_layout = random_swap(layout)
        score = layout_score(ngrams, new_layout)
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

    print(layout_score(ngrams, [
        "---TY---",
        "---GH---",
        "---BN---",
        "QWERUIOP",
        "ASDFJKL-",
        "ZXCVM---",
    ]))
    print()

    starting_layout = [
        "--QXZ---",
        "YDRWFUPV",
        "ASHTNEOI",
        "KGMCLB-J",
    ]

    best_best_score = [0]
    best_best_layout = [starting_layout]

    try:
        while True:
            print()
            print("\n".join(best_best_layout[0]))
            print(best_best_score[0])
            layout = best_best_layout[0]
            for _ in range(3):
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
