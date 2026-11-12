from picop import UnicodeWriter

writer = UnicodeWriter(32)
writer.write("value: ")
writer.write_char(ord("✓"))
writer.write(" ")
writer.write_repr(123)
print(writer.finish())

with UnicodeWriter() as contextual:
    contextual.write("context manager")
    print(contextual.finish())
