def rename_locals_example(module, another_argument=False, third_argument=None):

    if third_argument is None:
        third_argument = []

    third_argument.extend(module)

    for thing in module.things:
        if another_argument is False or thing.name in third_argument:
            thing.my_method()