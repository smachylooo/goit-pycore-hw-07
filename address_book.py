from collections import UserDict
import datetime as dt

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name is required")
        super().__init__(value)


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = dt.datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(birthday_date)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
    def add_phone(self,phone):
        self.phones.append(Phone(phone))
    
    def edit_phone(self, old_phone, new_phone):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone:
                self.phones[i] = Phone(new_phone)
    
    def find_phone(self, phone):
       for el in self.phones:
           if el.value == phone:
               return el
        
    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = "; ".join(phone.value for phone in self.phones)
        birthday_str = str(self.birthday) if self.birthday else "not set"
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {birthday_str}"


class AddressBook(UserDict):       

    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data[name]
    
    def delete(self, name):
        del self.data[name]
    
    def get_upcoming_birthdays(self):
        upcoming_birthdays = []
        today = dt.date.today()

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            days_diff = (birthday_this_year - today).days

            if 0 <= days_diff <= 7:
                congratulation_date = birthday_this_year

                if congratulation_date.weekday() == 5:  # Saturday
                    congratulation_date += dt.timedelta(days=2)
                elif congratulation_date.weekday() == 6:  # Sunday
                    congratulation_date += dt.timedelta(days=1)

                upcoming_birthdays.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y")
                })

        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return str(e)
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Enter the required arguments for the command."
    return inner


def parse_input(user_input):
    cmd, *args = user_input.strip().split()
    return cmd.lower(), *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args

    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    record.add_phone(phone)
    return message


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."

    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    if record.birthday is None:
        return "Birthday not set."

    return str(record.birthday)


@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next 7 days."

    lines = []
    for item in upcoming:
        lines.append(f"{item['name']}: {item['congratulation_date']}")
    return "\n".join(lines)



def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

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