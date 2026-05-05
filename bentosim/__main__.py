"""
``python -m bentosim <modül> [args]`` giriş noktası.

Şu anki modüller:
    aquarium  — Terminal Akvaryumu
"""

import sys


def _help():
    print("Kullanım: python -m bentosim <modül> [args...]")
    print()
    print("Mevcut modüller:")
    print("  aquarium    Terminal Akvaryumu")
    print()
    print("Örnek:")
    print("  python -m bentosim aquarium --theme abyss --fish 18")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        _help()
        sys.exit(0)

    mod_name = sys.argv[1]
    sub_argv = sys.argv[2:]

    if mod_name == "aquarium":
        from .aquarium.cli import run
        run(sub_argv)
    else:
        print(f"Bilinmeyen modül: {mod_name!r}")
        _help()
        sys.exit(2)


if __name__ == "__main__":
    main()
