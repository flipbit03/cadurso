## Inception (2010), Veto & AuthorizationDecision

This folder contains a Cadurso implementation set in the [Inception](https://en.wikipedia.org/wiki/Inception)
universe, with several actors (e.g., Cobb, Arthur, Ariadne) attempting to execute actions on resources (e.g., Dream Levels, Totems).
These actions are modulated based on their roles (e.g., `EXTRACTOR`, `POINT_MAN`), resource state (e.g., `collapsed`), and the `Veto` mechanism.

This test universe specifically exercises:
- **`Veto`**: Hard-denying requests with an optional reason, overriding any `True` from other rules.
- **`AuthorizationDecision`**: Inspecting `.allowed` and `.reason` on query results.
- **`can().do().on()`**: Fluent query syntax returning `AuthorizationDecision` with full Veto support.

### Diving in

The `conftest.py` file contains the whole system's definition. Start [here](./conftest.py#L223) to see the rules.

Then, just read the tests to see the authorization system in action.
