def main():
    total = 0
    index = 1000
    while index:
        index -= 1
        if not (index % 3) or not (index % 5):
            total += index

    print(total)


if __name__ == "__main__":
    main()
