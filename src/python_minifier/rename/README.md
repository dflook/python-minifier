# Renaming

We can save bytes by shortening the names used in a python program.

One simple way to do this is to replace each unique name in a module with a shorter one. 
This will probably exhaust the available single character names, so is not as efficient as it could be.
Also, not all names can be safely changed this way.

By determining the scope of each name, we can assign the same short name to multiple non-overlapping scopes.
This means sibling namespaces may have the same names, and names will be shadowed in inner namespaces where possible.

This file is a guide for how the python_minifier package shortens names.
There are multiple steps to the renaming process.

## Binding Names

Names are bound to the local namespace it is defined in.

### Create namespace nodes

Namespaces in python are introduced by Modules, Functions, Comprehensions, Generators and Classes.
The AST node that introduces a new namespace is called a 'namespace node'.

These attributes are added to namespace nodes:
- Bindings - A list of Bindings local to this namespace, populated by the Bind names step
- Globals - A list of global names in this namespace
- Nonlocals - A list of nonlocal names in this namespace

### Determine parent node

Add a parent attribute to each node with the value of the node of which this is a child.

### Determine namespace

Add a namespace attribute to each node with the value of the namespace node that will be used for name binding and resolution.
This is usually the closest parent namespace node. The exceptions are:

- Function argument default values are in the same namespace as their function.
- Function decorators are in the same namespace as their function.
- Function annotations are in the same namespace as their function.
- Class decorator are in the same namespace as their class.
- Class bases, keywords, starargs and kwargs are in the same namespace as their class.
- The first iteration expression of a comprehension is in the same namespace as it's parent ListComp/SetComp/DictComp or GeneratorExp.

### Bind names

Every node that binds a name creates a NameBinding for that name in its namespace.
The node is added to the NameBinding as a reference.

If the name is nonlocal in its namespace it does not create a binding.

Nodes that create a binding:
- FunctionDef nodes bind their name
- ClassDef nodes bind their name
- arg nodes bind their arg
- Name nodes in Store or Del context bind their id
- MatchAs nodes bind their name
- MatchStar nodes bind their name
- MatchMapping nodes bind their rest

### Resolve names

For the remaining unbound name nodes and nodes that normally create a binding but are for a nonlocal name, we find their binding.

Bindings for name references are found by searching their namespace, then parent namespaces.
If a name is global in a searched namespace, skip straight to the module node.
If a name is nonlocal in a searched namespace, skip to the next parent namespace.
When traversing parent namespaces, Class namespaces are skipped.

If a NameBinding is found, add the node as a reference.
If no NameBinding is found, check if the name would resolve to a builtin. 
If so, create a BuiltinBinding in the module namespace and add this node as a reference.

Otherwise we failed to find a binding for this name - Create a NameBinding in the module namespace and add this node 
as a reference.

## Hoist Literals

At this point we do the HoistLiterals transform, which adds new HoistedLiteral bindings to the namespaces where it wants
to introduce new names.

## Name Assignment

Collect all bindings in the module and sort by estimated byte savings

For each binding:
 - Determine it's 'reservation scope', which is the set of namespaces that name is referenced in (and all namespaces between them)
 - Get the next available name that is unassigned and unreserved in all namespaces in the reservation scope.
 - Check if we should proceed with the rename - is it space efficient to do this rename, or has the original name been assigned somewhere else?
 - Rename the binding, rename all referenced nodes to the new name, and record this name as assigned in every namespace of the reservation scope.
