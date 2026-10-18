"""Python usage for picop cymarshal.

Run: python examples/pymarshal.py
"""
from picop import marshal_dumps, marshal_loads

def main() -> None:
    blob = marshal_dumps({"k": 1})
    assert marshal_loads(blob) == {"k": 1}
    print("ok", blob[:8])

if __name__ == "__main__":
    main()
