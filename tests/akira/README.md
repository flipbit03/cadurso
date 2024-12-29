## Akira (1988), ABAC-style

This folder contains a full Cadurso ABAC[^1] implementation set in the [Akira](https://en.wikipedia.org/wiki/Akira_(1988_film))
universe, with several actors (e.g., Kaneda, Tetsuo) attempting to execute actions on resources (e.g., Neo-Tokyo, Bikes).
These actions are modulated based on their attributes (e.g., `psychic_level`) and the system's rules.

### Diving in

The `conftest.py` file contains the whole system's definition. Start [here](./conftest.py#L261).

Then, just read the tests to see the authorization system in action.


[^1]: Attribute-based Access Control (ABAC) is an authorization model that defines access control based on attributes of the actors, resources, and the environment.
      [[NIST ABAC]](https://csrc.nist.gov/publications/detail/sp/800-162/final)
      [[Wikipedia]](https://en.wikipedia.org/wiki/Attribute-based_access_control)
