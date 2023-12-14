import socket
from escpos.printer import Network
from helpers.check_printer import is_printer_ready
t = 'test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test'
h = 'hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hellohello hello hello '
for i in range(3):
    t+=t
    h+=h
def test_printer():
    if is_printer_ready("192.168.1.159",9100):
        p = Network("192.168.1.159", port=9100)
        p.text(t)
        p.cut()

def test_print_2():
    if is_printer_ready("192.168.1.159",9100):
        p = Network("192.168.1.159", port=9100)
        p.text(h)
        p.cut()


test_printer()
test_print_2()