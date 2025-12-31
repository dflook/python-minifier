def rename_locals_example(module,another_argument=False,third_argument=None):
	B=module;A=third_argument
	if A is None:A=[]
	A.extend(B)
	for C in B.things:
		if another_argument is False or C.name in A:C.my_method()