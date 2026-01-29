fn main() {
    let mut index: u64 = 218000;
    let mut total: u64 = 0;

    loop {
        if index % 2 != 0 {
            total += index * index
        }
        if index == 1 {
            break;
        }
        index -= 1;
    }

    print!("{}\n", total)
}
