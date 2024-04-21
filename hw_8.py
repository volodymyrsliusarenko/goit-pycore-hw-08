from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        self.validate()

    def validate(self):
        if not self.value.isdigit() or len(self.value) != 10:
            raise ValueError("Invalid phone number format. Phone number should contain 10 digits.")

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y").date()
            super().__init__(value)
        except ValueError:
            raise ValueError('Invalid date format. Should be ДД-ММ-РРРР')

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]

    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)

    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        try:
            self.birthday = Birthday(birthday)
        except ValueError as e:
            raise ValueError("Invalid date format. Use DD.MM.YYYY") from e

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(str(p) for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = datetime.today()
        upcoming_birthdays = []
    
        for record in self.data.values():
            if record.birthday:
                birthday_this_year = datetime(today.year, record.birthday.date.month, record.birthday.date.day)
    
                if birthday_this_year < today:
                    birthday_this_year = datetime(today.year + 1, record.birthday.date.month, record.birthday.date.day)
    
                delta = birthday_this_year - today
    
                if 0 <= delta.days <= days:
                    if birthday_this_year.weekday() >= 5:
                        if birthday_this_year.weekday() == 5:
                            birthday_this_year += timedelta(days=2)
                        else:
                            birthday_this_year += timedelta(days=1)
    
                    upcoming_birthdays.append({"name": record.name.value, "birthday": birthday_this_year.strftime("%d.%m.%Y")})
    
        return upcoming_birthdays

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Contact already exists. Please try a different name or use the 'change' command to update."
        except ValueError as e:
            error_message = str(e)
            if "phone" in error_message:
                return "Invalid phone number format. Phone number should contain exactly 10 digits."
            elif "date" in error_message:
                return "Invalid date format. Please use the format DD.MM.YYYY."
            else:
                return "An error occurred. Please try again."
        except IndexError:
            return "Please enter a name to show the phone number."
        except AttributeError:
            return "Contact not found. Please enter a valid name."
    return wrapper

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    name, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(record.phones[0].value, new_phone)
        return "Contact phone number updated successfully."
    else:
        raise KeyError("Contact not found.")

@input_error
def show_phones(args, book: AddressBook):
    name = args[0]
    record = book.find(name)
    if record:
        return "; ".join(str(phone) for phone in record.phones)
    else:
        raise AttributeError("Contact not found.")

@input_error
def show_all(book: AddressBook):
    if book:
        return str(book)
    else:
        return "Address book is empty."

@input_error
def add_birthday(args, book):
    name = args[0]
    birthday = args[1]
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return "Birthday was added."
    else:
        raise KeyError

@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return str(record.birthday)

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join(f"{entry['name']}'s birthday on {entry['birthday']}" for entry in upcoming_birthdays)
    else:
        return "No upcoming birthdays in the next week."

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

def main():
    book = load_data()

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()
