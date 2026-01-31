def main():
    factors = {600851475143}

    factor_found = True
    while factor_found:
        factor_found = False
        updated_factors = set()
        for factor in factors:
            for n in range(2, int(factor/2)):
                if (factor % n) == 0:
                    updated_factors.add(n)
                    updated_factors.add(int(factor/n))
                    factor_found = True
                    break
        
        if updated_factors:
            factors = updated_factors

    s = sorted(factors, reverse=True)
    print(s[0])

if __name__ == "__main__":
    main()