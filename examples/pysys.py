"""Read a required sys attribute through the CPython 3.15 C API."""
import sys


def main():
    if sys.version_info < (3, 15):
        print("PySys_GetAttr requires CPython 3.15 or newer; skipping")
        return
    from picop import sys_get_attr
    assert sys_get_attr("version") is sys.version
    print(sys_get_attr("version"))


if __name__ == "__main__":
    main()
