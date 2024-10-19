use std::{
    fs::File,
    io::{BufReader, Read},
};

fn find_in_file(path: &str) {
    let file = File::open(path).unwrap();

    let mut reader = BufReader::new(file);

    let mut contents = String::new();

    reader.read_to_string(&mut contents).unwrap();

    // remove non-numeric characters

    contents = contents
        .chars()
        .skip(2) // skip 2.
        .filter(|c| c.is_numeric())
        .collect::<String>();

    let mut found = false;
    let str_to_find = "20012001";

    println!("Searching for: {} in {}", str_to_find, path);

    println!("{}[:50]: {}", path, &contents[0..50]);

    for i in 0..contents.len() - str_to_find.len() {
        if &contents[i..i + str_to_find.len()] == str_to_find {
            println!("Found at index: {}", i);
            found = true;
            break;
        }
    }

    if !found {
        println!("Not found");
    }
}

fn main() {
    find_in_file("euler-digits.txt");
    find_in_file("sqrt(2)-digits.txt");
    find_in_file("pi-digits.txt"); // 189003704 so not found
}
