def main():
    num1 = 1
    num2 = 2
    total = 0

    while num1 < 4000000:
        if not (num1 % 2):
            total += num1
        temp = num2
        num2 = num1 + num2
        num1 = temp

    print(total)

if __name__ == "__main__":
    main()