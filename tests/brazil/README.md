## Brazil (1985), RBAC-style

This folder contains a full cadurso RBAC[^1] implementation set in the [Brazil](https://en.wikipedia.org/wiki/Brazil_(1985_film))
universe, with several actors (e.g., Sam Lowry, Tuttle) attempting to execute actions on resources (e.g., Paperwork, Ducts).
These actions are modulated based on their roles (e.g., `CITIZEN`, `BUREAUCRAT`) and the system's rules.

### Diving in

The `conftest.py` file contains the whole system's definition. Start [here](./conftest.py#L239) to see the system's definition.

We also present a single mixed RBAC+ABAC rule example [here](./conftest.py#L279), where a Character can only perform city plumbing repairs if they are an Engineer **and** also carrying Form "27B/6" in their pocket.

Then, just read the tests to see the authorization system in action.


[^1]: Role-based Access Control (RBAC) is an authorization model that defines access control based on roles assigned to actors.
      [[NIST RBAC]](https://csrc.nist.gov/pubs/conference/1992/10/13/rolebased-access-controls/final)
      [[Wikipedia]](https://en.wikipedia.org/wiki/Role-based_access_control)
