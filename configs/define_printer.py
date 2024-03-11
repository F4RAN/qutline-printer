from threading import Thread
from time import sleep
from escpos.printer import Network
from helpers.check_printer import check_printer_status, check_printer_online
import queue


class Printer:
    Printers = []

    def __init__(self, mac):
        self.tout = 20
        self.mac = mac
        self.printer_thread = ""
        self.print_queue = ""
        self.set_printer()

    def set_printer(self):
        for printer in Printer.Printers:
            if printer.mac == self.mac:
                print("No need to initiate new thread and queue")
                self.print_queue = printer.print_queue
                self.printer_thread = printer.printer_thread
                break
        else:
            print("Initiate new thread and queue")
            # Initiate new thread and queue
            self.print_queue = queue.Queue()
            self.printer_thread = Thread(target=self.print_handler)
            self.printer_thread.daemon = True
            self.printer_thread.start()
            self.Printers.append(self)

    def print(self, image_path, ip, tp="image", code="", name=""):
        print(self.print_queue)
        try:  # Connect to the printer
            # if not check_printer_online(ip, 9100):
            #     return False
            self.print_queue.put({
                'image': image_path,
                'ip': ip,
                'type':tp,
                'code':code,
                'name':name
            })
            return True
        except Exception as e:
            print(e)
            return False

    def print_handler(self):
        while True:
            item = self.print_queue.get()
            print("new item received on", self.mac, "queue")
            try:
                c = 0
                skip = False
                while not check_printer_status(item['ip'], 9100):
                    c += 1
                    if c > self.tout:
                        skip = True
                        break
                    if check_printer_status(item['ip'], 9100):
                        print("Printer not busy")
                        break
                    else:  # Printer is busy
                        print("Printer", self.mac, "is busy")
                        print(f"Try for {self.tout - c} other seconds", self.print_queue.qsize() + 1, "items in queue", end='\r')
                    sleep(1)
                if skip:
                    self.print_queue.task_done()
                    continue
                printer = Network(item['ip'], port=9100)
                # Print image
                printer.open()
                if item['type'] == 'image':
                    printer.set(align='center', width=2, height=2)
                    printer.image(item['image'])
                    printer.cut()
                elif item['type'] == 'code':
                    printer.set(align='center', width=2, height=2)
                    print(item['code'], "Code is printing")
                    printer.text(item['name'] + " Code is:\n")
                    code = item['code']
                    for char in code:
                        printer.set(align='center', width=7, height=7, custom_size=True)
                        printer.text(char + ' ' + ' ')
                    printer.text('\n')
                printer.close()


            except Exception as e:
                print("Printer", self.mac, "queue error", e)
            # Handle errors

            self.print_queue.task_done()
