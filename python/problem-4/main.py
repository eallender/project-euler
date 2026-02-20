def main():
    num1, num2 = 999, 999
    largest = 0

    for i in range(num1, 0, -1):
        for j in range(num2, 0, -1):
            prod = i * j
            if prod <= largest:
                break
            if check_palindrome(prod):
                largest = prod

    print(largest)


def check_palindrome(num: int) -> bool:
    num_str = str(num)

    if num_str == num_str[::-1]:
        return True

    return False


if __name__ == "__main__":
    main()
