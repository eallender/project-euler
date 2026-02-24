import math

MAX_NUM = 20


def main():
    minimum = math.factorial(MAX_NUM)

    for x in range(MAX_NUM, minimum, MAX_NUM):
        if is_multiple(x):
            minimum = x
            break

    print(minimum)


def is_multiple(num):
    for x in range(MAX_NUM, 3, -1):
        if (num % x) != 0:
            return False

    return True


if __name__ == "__main__":
    main()
