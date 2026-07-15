"""Stable complete-suite entry point; responsibility tests live beside it."""
from importlib import import_module

MODULES = (
    "test_static",
    "test_drive",
    "test_inspect",
    "test_task_switch",
    "test_lifecycle",
    "test_closeout",
)


def discovered_tests():
    tests = []
    for module_name in MODULES:
        module = import_module(module_name)
        tests.extend(
            value for name, value in vars(module).items()
            if name.startswith("test_") and callable(value)
        )
    return tests


def run_all():
    tests = discovered_tests()
    names = [test.__name__ for test in tests]
    if len(names) != len(set(names)):
        raise AssertionError("duplicate test names in split suite")
    for test in tests:
        test()
        print("ok", test.__name__)
    print(f"{len(tests)} tests passed")


if __name__ == "__main__":
    run_all()
