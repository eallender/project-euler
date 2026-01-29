def main():
    count = 218000
    total = 0
    while count:
        if count % 2:
            total += count * count
        count -= 1

    print(total)
    assert total == 1726705333297000


if __name__ == "__main__":
    main()
