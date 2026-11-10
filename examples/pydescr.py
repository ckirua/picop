"""Python usage for picop cydescr.

Run: python examples/pydescr.py
"""
from picop import descr_is_data, descr_name, descr_objclass

def main() -> None:
    descriptor = str.upper
    assert descr_name(descriptor) == "upper"
    assert descr_objclass(descriptor) is str
    assert descr_is_data(property()) is True
    print("ok", descr_name(descriptor), descr_objclass(descriptor))

if __name__ == "__main__":
    main()
