fn main() {
    let mut total: u64 = 0;
    let mut index: u64 = 1000;

    while index >= 3 {
        index -= 1;
        if index % 3 == 0 || index % 5 == 0 {
            total += index;
        }
    }

    print!("{}\n", total);
}
