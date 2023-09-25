import sqlite3
import nltk
import gensim

# Create database and tables
conn = sqlite3.connect('library.db')
c = conn.cursor()

c.execute('''CREATE TABLE Books 
             (BookID text, Title text, Author text, ISBN text, Status text)''')

c.execute('''CREATE TABLE Users  
             (UserID text, Name text, Email text)''')

c.execute('''CREATE TABLE Reservations
             (ReservationID text, BookID text, UserID text, ReservationDate text)''')

# User interface
print('Library Management System')
while True:
    print('\nChoose an option:')
    print('1. Add a new book')
    print('2. Find book details')
    print('3. Find reservation status')
    print('4. Find all books')
    print('5. Update book details')
    print('6. Delete a book')
    print('7. Exit')

    choice = input('Enter your choice: ')

    if choice == '1':
        # Add new book
        book_id = input('Enter Book ID: ')
        title = input('Enter Title: ')
        author = input('Enter Author: ')
        isbn = input('Enter ISBN: ')
        status = 'Available'

        c.execute('INSERT INTO Books VALUES (?,?,?,?,?)',
                  (book_id, title, author, isbn, status))
        conn.commit()
        print('New book added successfully.')

    elif choice == '2':
        book_id = input('Enter Book ID to find details: ')

        # Join all 3 tables
        c.execute('''SELECT b.BookID, b.Title, b.Author, b.ISBN, b.Status,
                          u.Name, r.ReservationDate 
                     FROM Books b
                     LEFT JOIN Reservations r ON b.BookID = r.BookID
                     LEFT JOIN Users u ON r.UserID = u.UserID
                     WHERE b.BookID = ?''', (book_id,))

        book = c.fetchone()

        if book:
            print('\nBook Details:')
            print('Title:', book[1])
            print('Author:', book[2])
            print('ISBN:', book[3])
            print('Status:', book[4])
            if book[5]:
                print('Reserved by:', book[5])
                print('Reservation date:', book[6])
            else:
                print('Not reserved')
        else:
            print('Book not found.')

    elif choice == '3':
        # Find reservation status
        id_type = input('Enter ID type (BK for Book, LU for User, LR for Reservation): ')
        id_val = input('Enter ID value: ')

        if id_type == 'BK':
            # Search by Book ID
            c.execute('''SELECT b.Title, b.Status, u.Name, r.ReservationDate
                         FROM Books b
                         LEFT JOIN Reservations r ON b.BookID = r.BookID
                         LEFT JOIN Users u ON r.UserID = u.UserID 
                         WHERE b.BookID = ?''', (id_val,))

        elif id_type == 'LU':
            # Search by User ID
            c.execute('''SELECT b.Title, b.Status, u.Name, r.ReservationDate
                         FROM Books b
                         LEFT JOIN Reservations r ON b.BookID = r.BookID 
                         LEFT JOIN Users u ON r.UserID = u.UserID
                         WHERE u.UserID = ?''', (id_val,))

        elif id_type == 'LR':
            # Search by Reservation ID
            c.execute('''SELECT b.Title, b.Status, u.Name, r.ReservationDate
                         FROM Books b
                         LEFT JOIN Reservations r ON b.BookID = r.BookID
                         LEFT JOIN Users u ON r.UserID = u.UserID
                         WHERE r.ReservationID = ?''', (id_val,))
        else:
            # Search by Title
            c.execute('''SELECT b.BookID, b.Status, u.Name, r.ReservationDate
                         FROM Books b
                         LEFT JOIN Reservations r ON b.BookID = r.BookID
                         LEFT JOIN Users u ON r.UserID = u.UserID
                         WHERE b.Title = ?''', (id_val,))

        book = c.fetchone()

        if book:
            print('\nReservation Details:')
            print('Title:', book[0])
            print('Status:', book[1])
            if book[2]:
                print('Reserved by:', book[2])
                print('Reservation date:', book[3])
            else:
                print('Not reserved')
        else:
            print('Book not found.')

    elif choice == '4':
        # Find all books
        c.execute('''SELECT b.BookID, b.Title, b.Author, b.ISBN, b.Status,
                      u.Name, r.ReservationDate
                   FROM Books b
                   LEFT JOIN Reservations r ON b.BookID = r.BookID
                   LEFT JOIN Users u ON r.UserID = u.UserID''')

        books = c.fetchall()

        if books:
            print('\nAll Books:')
            for book in books:
                print(book[0], book[1], book[2], book[3], book[4])
                if book[5]:
                    print('Reserved by:', book[5])
                    print('Reservation date:', book[6])
                else:
                    print('Not reserved')
        else:
            print('No books found.')

    elif choice == '5':
        book_id = input('Enter Book ID to update details: ')

        print('1. Update Title')
        print('2. Update Author')
        print('3. Update ISBN')
        print('4. Update Status')
        print('5. Update Reservation Status')

        update_choice = input('What would you like to update? ')

        if update_choice == '1':
            new_title = input('Enter new title: ')
            c.execute('UPDATE Books SET Title = ? WHERE BookID = ?',
                      (new_title, book_id))

        elif update_choice == '2':
            new_author = input('Enter new author: ')
            c.execute('UPDATE Books SET Author = ? WHERE BookID = ?',
                      (new_author, book_id))

        elif update_choice == '3':
            new_isbn = input('Enter new ISBN: ')
            c.execute('UPDATE Books SET ISBN = ? WHERE BookID = ?',
                      (new_isbn, book_id))

        elif update_choice == '4':
            new_status = input('Enter new status: ')
            c.execute('UPDATE Books SET Status = ? WHERE BookID = ?',
                      (new_status, book_id))

        elif update_choice == '5':
            if input('Mark book as reserved? (y/n) ') == 'y':
                user_id = input('Enter user ID: ')
                date = input('Enter reservation date: ')
                c.execute('UPDATE Books SET Status = "Reserved" WHERE BookID = ?',
                          (book_id,))
                c.execute('INSERT INTO Reservations VALUES (?,?,?,?)',
                          (f'LR{user_id}', book_id, user_id, date))
            else:
                c.execute('DELETE FROM Reservations WHERE BookID = ?', (book_id,))
                c.execute('UPDATE Books SET Status = "Available" WHERE BookID = ?',
                          (book_id,))

        conn.commit()
        print('Book updated successfully.')

    elif choice == '6':
        book_id = input('Enter Book ID to delete: ')

        c.execute('DELETE FROM Books WHERE BookID = ?', (book_id,))
        c.execute('DELETE FROM Reservations WHERE BookID = ?', (book_id,))

        conn.commit()

        if c.rowcount > 0:
            print('Book deleted successfully.')
        else:
            print('Book not found.')

    elif choice == '7':
        print('Exiting program...')
        break

    else:
        print('Invalid choice. Please try again.')

conn.close()

# Topic modeling
from nltk.corpus import gutenberg

alice = gutenberg.raw('carroll-alice.txt')

import gensim
from gensim import corpora

# Create dictionary and corpus
alice_dict = corpora.Dictionary([alice])
alice_corpus = [alice_dict.doc2bow(alice)]

# Build LDA model
lda_model = gensim.models.LdaModel(alice_corpus,
                                   id2word=alice_dict,
                                   num_topics=5,
                                   passes=10)

# ps
# pyLadivs needs high-level numpy,but high-level numpy cannot fit rasa.
# pyLadivs needs above 1.42 numpy, but rasa needs below 1.4 numpy. So I failed.
