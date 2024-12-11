import pkg_resources
import sys


def get_installed_libraries():
    installed_libs = pkg_resources.working_set
    installed_libs = sorted(installed_libs, key=lambda lib: lib.project_name)
    return [(lib.project_name, lib.version) for lib in installed_libs]


def get_imported_libraries():
    imported_libs = []
    for name, module in sys.modules.items():
        if hasattr(module, '__file__'):
            imported_libs.append((name, module.__version__))
    return imported_libs


def main():
    print("Installed Libraries:")
    for lib, version in get_installed_libraries():
        print(f"{lib}: {version}")

    print("\nImported Libraries:")
    for lib, version in get_imported_libraries():
        print(f"{lib}: {version}")


if __name__ == "__main__":
    main()