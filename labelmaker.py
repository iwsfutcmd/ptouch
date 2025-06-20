#!/usr/bin/env python3

# import binascii
# import packbits
import serial
import sys
# import time
import bluetooth

from labelmaker_encode import encode_raster_transfer, read_png, unsigned_char
from text_to_image import label

STATUS_OFFSET_BATTERY = 6
STATUS_OFFSET_EXTENDED_ERROR = 7
STATUS_OFFSET_ERROR_INFO_1 = 8
STATUS_OFFSET_ERROR_INFO_2 = 9
STATUS_OFFSET_STATUS_TYPE = 18
STATUS_OFFSET_PHASE_TYPE = 19
STATUS_OFFSET_NOTIFICATION = 22

STATUS_TYPE = [
    "Reply to status request",
    "Printing completed",
    "Error occured",
    "IF mode finished",
    "Power off",
    "Notification",
    "Phase change",
]

STATUS_BATTERY = [
    "Full",
    "Half",
    "Low",
    "Change batteries",
    "AC adapter in use"
]

def print_status(raw):
    if len(raw) != 32:
        print("Error: status must be 32 bytes. Got " + len(raw))
        return

    if raw[STATUS_OFFSET_STATUS_TYPE] < len(STATUS_TYPE):
        print("Status: " + STATUS_TYPE[raw[STATUS_OFFSET_STATUS_TYPE]])
    else:
        print("Status: " + hex(raw[STATUS_OFFSET_STATUS_TYPE]))

    if raw[STATUS_OFFSET_BATTERY] < len(STATUS_BATTERY):
        print("Battery: " + STATUS_BATTERY[raw[STATUS_OFFSET_BATTERY]])
    else:
        print("Battery: " + hex(raw[STATUS_OFFSET_BATTERY]))

    print("Error info 1: " + hex(raw[STATUS_OFFSET_ERROR_INFO_1]))
    print("Error info 2: " + hex(raw[STATUS_OFFSET_ERROR_INFO_2]))
    print("Extended error: " + hex(raw[STATUS_OFFSET_EXTENDED_ERROR]))
    print()


# Check for input image
# if len(sys.argv) < 2:
#     print("Usage: %s <path-to-image>" % sys.argv[0])
#     sys.exit(1)

# Get serial device

def write(data, dryrun=False):
    ser = serial.Serial(
        # '/dev/rfcomm0',
        '/dev/tty.PT-300BT8415',
        baudrate=9600,
        stopbits=serial.STOPBITS_ONE,
        parity=serial.PARITY_NONE,
        bytesize=8,
        dsrdtr=True
    )

    print(ser.name)

    # Read input image into memory
    # data = read_png(png_path)

    # Enter raster graphics (PTCBP) mode
    ser.write(b"\x1b\x69\x61\x01")

    # Initialize
    ser.write(b"\x1b\x40")

    # Dump status
    ser.write(b"\x1b\x69\x53")
    print_status( ser.read(size=32) )

    # Flush print buffer
    for i in range(64):
        ser.write(b"\x00")

    # Initialize
    ser.write(b"\x1b\x40")

    # Enter raster graphics (PTCBP) mode
    ser.write(b"\x1b\x69\x61\x01")

    # Found docs on http://www.undocprint.org/formats/page_description_languages/brother_p-touch
    ser.write(b"\x1B\x69\x7A") # Set media & quality
    ser.write(b"\xC4\x01") # print quality, continuous roll
    ser.write(b"\x0C") # Tape width in mm
    ser.write(b"\x00") # Label height in mm (0 for continuous roll)

    # Number of raster lines in image data
    raster_lines = len(data) // 16
    print(raster_lines, raster_lines % 256, int(raster_lines // 256))
    ser.write( unsigned_char.pack( raster_lines % 256 ) )
    ser.write( unsigned_char.pack( int(raster_lines // 256) ) )

    # Unused data bytes in the "set media and quality" command
    ser.write(b"\x00\x00\x00\x00")

    # Set print chaining off (0x8) or on (0x0)
    ser.write(b"\x1B\x69\x4B\x08")

    # Set mirror, no auto tape cut
    ser.write(b"\x1B\x69\x4D\x80")

    # Set margin amount (feed amount)
    ser.write(b"\x1B\x69\x64\x00\x00")

    # Set compression mode: TIFF
    ser.write(b"\x4D\x02")

    # Send image data
    print("Sending image data")
    ser.write( encode_raster_transfer(data) )
    print("Done")

    # Print and feed
    if not dryrun:
        ser.write(b"\x1A")
    print("Printing")

    # Dump status that the printer returns
    print_status( ser.read(size=32) )

    # Initialize
    ser.write(b"\x1b\x40")

    ser.close()

def write_bt(data, dryrun=False):
    addr = 'A8:B2:DA:7D:43:5E'
    port = 1
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((addr, port))
    # Enter raster graphics (PTCBP) mode
    sock.send(b"\x1b\x69\x61\x01")

    # Initialize
    sock.send(b"\x1b\x40")

    # Dump status
    sock.send(b"\x1b\x69\x53")
    print_status( sock.recv(32) )

    # Flush print buffer
    for i in range(64):
        sock.send(b"\x00")

    # Initialize
    sock.send(b"\x1b\x40")

    # Enter raster graphics (PTCBP) mode
    sock.send(b"\x1b\x69\x61\x01")

    # Found docs on http://www.undocprint.org/formats/page_description_languages/brother_p-touch
    sock.send(b"\x1B\x69\x7A") # Set media & quality
    sock.send(b"\xC4\x01") # print quality, continuous roll
    sock.send(b"\x0C") # Tape width in mm
    sock.send(b"\x00") # Label height in mm (0 for continuous roll)

    # Number of raster lines in image data
    raster_lines = len(data) // 16
    print(raster_lines, raster_lines % 256, raster_lines // 256)
    sock.send( unsigned_char.pack( raster_lines % 256 ) )
    sock.send( unsigned_char.pack( raster_lines // 256) )

    # Unused data bytes in the "set media and quality" command
    sock.send(b"\x00\x00\x00\x00")

    # Set print chaining off (0x8) or on (0x0)
    sock.send(b"\x1B\x69\x4B\x08")

    # Set mirror, no auto tape cut
    sock.send(b"\x1B\x69\x4D\x80")

    # Set margin amount (feed amount)
    sock.send(b"\x1B\x69\x64\x00\x00")

    # Set compression mode: TIFF
    sock.send(b"\x4D\x02")

    # Send image data
    print("Sending image data")
    sock.send( bytes(encode_raster_transfer(data)) )
    print("Done")

    # Print and feed
    if not dryrun:
        sock.send(b"\x1A")
    print("Printing")

    # Dump status that the printer returns
    print_status( sock.recv(32) )

    # Initialize
    sock.send(b"\x1b\x40")

    sock.close()


def print_label(text, font_path, index=0):
    data = label(text, font_path, index).tobytes()
    try:
        write_bt(data)
    except serial.SerialException:
        write_bt(data)

if __name__ == "__main__":
    try:
        print_label(sys.argv[1], sys.argv[2])
    except IndexError:
        pass
