import curses

stdscr = curses.initscr()



while True:
    c = stdscr.getch()
    if c == ord('w'):
        print("Vooruit")
    if c == ord('a'):
        print("Links")
    if c == ord('s'):
        print("Beneden")
    if c == ord('d'):
        print("Rechts")
    elif c == ord('q'):
        break  # Exit the while loop
    elif c == curses.KEY_HOME:
        x = y = 0
