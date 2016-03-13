import time
import pylirc as lirc

def main():
    lirc.init("radio")

    while 1:
        ir_codes = lirc.nextcode()
        if ir_codes != None:
            print(ir_codes)
        time.sleep(0.1)

if __name__ == "__main__":
    main()
