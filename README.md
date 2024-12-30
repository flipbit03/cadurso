# 🐻Cadurso[^1]
Authorization framework for Python-based applications. Inspired by _[Oso](https://github.com/osohq/oso)_.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cadurso)](https://pypi.org/project/cadurso/)
[![PyPI - Version](https://img.shields.io/pypi/v/cadurso)](https://pypi.org/project/cadurso/)

## Overview

Cadurso is a lightweight and extensible authorization framework designed to handle access control scenarios by building and querying rules. It enables developers to define rules for actors performing actions on resources, with support for synchronous and asynchronous workflows. This library is inspired by the principles of the Oso framework, emphasizing flexibility and clarity in managing authorization.

## Features

- **Declarative Rule Definitions**: Define who can do what with ease. Rules are just Python functions[^2].
- **Support for Sync and Async**: Handle both blocking and non-blocking authorization queries seamlessly. Rules can also be async.
- **Immutable**: Prevent rule additions at runtime by freezing the authorization framework after defining rules.
- **Error Handling**: Comprehensive exceptions for incomplete queries, operational issues, and rule definition errors.

## Use Cases

- Multi-tenant applications requiring fine-grained access control.
- Implementing Role-Based Access Control, Attribute-Based Access Control or anything in between.

## Core Concepts

The core concepts of a Cadurso-powered authorization system are `Actors`, `Actions`, and `Resources`. They are combined into `Rules` which can be added to a `Cadurso` instance, represent capabilities within a system.

After defining rules, the framework can be marked as "frozen" to prevent further modifications, ensuring the integrity of the authorization system.

### Actors

an `Actor` can be any Python instance. e.g `User`, `ServiceAccount`.

### Actions

`Actions` are operations that `Actors` can attempt on `Resources`. They can be any hashable object.

Good candidates for `Actions` are `str`, `Enum`, etc.

_(But any object that implements `__hash__` and `__eq__` can be used)_

### Resources

`Resources` are entities that `Actors` interact with. They can be any object that needs to be protected. e.g `Document`, `Post`.

### Rules

`Rules` are combinations of `Actors`, `Actions`, and `Resources`. They are expressed as Python functions that return a boolean value.

Cadurso uses the type hints of the rule function to determine the types of the `Actor` and `Resource` arguments. The `Action` is passed as a parameter to the decorator that defines the rule.

Rule format:
```python
cadurso = Cadurso()

@cadurso.add_rule(<ACTION>)
def rule_definition(actor: [ACTOR TYPE], resource: [RESOURCE TYPE]) -> bool:
    # Return True or False based on the rule logic
    ...
```

### State Freezing

Once you are finished defining rules, the framework should be "frozen" to prevent further modifications. This ensures the integrity of the authorization system.

```python
cadurso.freeze()
```

## Quick Start

### Installation

```bash
pip install cadurso
```

### Complete Example

#### Defining Rules
```python
# Initialize the authorization framework
from cadurso import Cadurso
cadurso = Cadurso()

# Some Actors and Resources type definitions
class User:
    ...

class Document:
    ...

# Some Actions
class DocumentPermission(Enum):
    EDIT = auto()
    """Edit a document."""

    VIEW = auto()
    """Visualize a document."""


# Define your authorization rules
@cadurso.add_rule(DocumentPermission.EDIT)
def owner_can_edit_own_document(actor: User, resource: Document) -> bool:
    return actor == resource.owner

@cadurso.add_rule(DocumentPermission.EDIT)
def admin_can_edit_any_document(actor: User, _resource: Document) -> bool:
    return actor.role == Role.ADMIN

@cadurso.add_rule(DocumentPermission.VIEW)
def owner_can_edit_own_document(actor: User, resource: Document) -> bool:
    """Any person who can EDIT a document can also, obviously, VIEW it."""
    # Piggyback on the EDIT permission.
    # This way we don't need to write VIEW rules for both owners and admins.
    return cadurso.can(actor).do(DocumentPermission.EDIT).on(resource)

# Async rules are also okay, if you need them
@cadurso.add_rule(DocumentPermission.VIEW)
async def async_rule(actor: User, resource: Document) -> bool:
    return await some_other_async_check(actor, resource)


# Freeze the rules to prevent further modifications
cadurso.freeze()

# (You are ready to query now)
# Use your `cadurso` instance as a singleton throughout your application
```

#### Querying

(Instance definitions)
```python
# Some Actors
john = User(name="John", role=Role.USER)
gunnar = User(name="Gunnar", role=Role.ADMIN)

# Some Resources
johns_document = Document(owner=john)
gunnars_document = Document(owner=gunnar)
```

(Query: Synchronous APIs)
```python
# `.is_allowed()` method to query permissions
cadurso.is_allowed(john, DocumentPermission.EDIT, johns_document)   # Output: True
cadurso.is_allowed(john, DocumentPermission.EDIT, gunnars_document) # Output: False
cadurso.is_allowed(gunnar, DocumentPermission.EDIT, johns_document) # Output: True

# Alternate querying syntax with `.can()`.
# This is just syntactic sugar for the above.
cadurso.can(john).do(DocumentPermission.EDIT).on(johns_document)    # Output: True
cadurso.can(john).do(DocumentPermission.EDIT).on(gunnars_document)  # Output: False
cadurso.can(gunnar).do(DocumentPermission.EDIT).on(johns_document)  # Output: True
```

(Query: Asynchronous APIs)
```python
# `.is_allowed_async()` method to query permissions asynchronously
await cadurso.is_allowed_async(john, DocumentPermission.EDIT, johns_document)  # Output: True

# Querying permissions with `.can()` asynchronously
await cadurso.can(john).do(DocumentPermission.EDIT).on_async(johns_document)   # Output: True
```

#### More examples?

- **ABAC** (Attribute-based Access Control) in Cadurso:
  - Check [`/tests/akira/`](./tests/akira) for a full ABAC implementation set in the [Akira](https://en.wikipedia.org/wiki/Akira_(1988_film)) universe.


- **RBAC** (Role-based Access Control) in Cadurso:
  - The [`/tests/brazil/`](./tests/brazil) folder shows a full RBAC implementation set in the [Brazil](https://en.wikipedia.org/wiki/Brazil_(1985_film)) universe.


## Contributing
Contributions are welcome! Please ensure tests are included for any new features or bug fixes. Follow the standard pull request guidelines for this repository.

## License
Cadurso is licensed under the MIT License. See the LICENSE file for details.

[^1]: Oso means "bear" in Spanish. `Cadurso` is a portmanteau of "Cadu" (my nickname) and "Urso" ("bear", in Portuguese) 😉

[^2]: **Important:** Rules should be pure functions, and avoid mutating the actors or resources passed to them.
      As we cannot enforce this at runtime, it is the responsibility of the developer to ensure this.
