from picop import BytesWriter

writer = BytesWriter(64)
writer.write(b"value: ")
writer.write_char(0x2713 & 0xFF)  # single byte
writer.write(b" ")
writer.write(bytearray(b"payload"))
print(writer.finish())

with BytesWriter() as contextual:
    contextual.write(b"context manager")
    print(contextual.finish())
