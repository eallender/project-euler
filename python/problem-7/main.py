def main():
    NUM_PRIMES = 10_001
    primes = []
    curr = 2

    while len(primes) < NUM_PRIMES:
        invalid = False
        for prime in primes:
            if not curr % prime:
                invalid = True
                break

        if not invalid:
            if curr ** (1 / 2) <= 3:
                primes.append(curr)
                curr += 1
                continue
            else:
                for i in range(3, int(curr ** (1 / 2) + 1), 2):
                    if not curr % i:
                        invalid = True

        if not invalid:
            primes.append(curr)

        curr += 1

    print(primes[NUM_PRIMES - 1])


if __name__ == "__main__":
    main()
