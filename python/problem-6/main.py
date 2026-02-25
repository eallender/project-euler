NUM = 100


def main():
    sum = 0
    squares = 0

    for i in range(1, NUM + 1):
        sum += i
        squares += i**2

    ans = sum**2 - squares

    print(ans)


if __name__ == "__main__":
    main()
