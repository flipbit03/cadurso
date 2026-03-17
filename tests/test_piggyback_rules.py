"""Tests for piggyback rules — rules that delegate to is_allowed() internally."""

from dataclasses import dataclass

from cadurso import AuthorizationDecision, Cadurso, Veto


@dataclass
class User:
    name: str
    admin: bool = False


@dataclass
class Document:
    owner: User


def test_piggyback_allows_through() -> None:
    """A piggyback rule grants access when the delegated permission allows."""
    c = Cadurso()

    @c.add_rule("edit")
    def owner_can_edit(actor: User, resource: Document) -> bool:
        return actor == resource.owner

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> AuthorizationDecision:
        return c.is_allowed(actor, "edit", resource, raise_veto=True)

    c.freeze()

    alice = User(name="Alice")
    doc = Document(owner=alice)
    assert c.is_allowed(alice, "view", doc)


def test_piggyback_denies_through() -> None:
    """A piggyback rule denies access when the delegated permission denies."""
    c = Cadurso()

    @c.add_rule("edit")
    def owner_can_edit(actor: User, resource: Document) -> bool:
        return actor == resource.owner

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> AuthorizationDecision:
        return c.is_allowed(actor, "edit", resource, raise_veto=True)

    c.freeze()

    alice = User(name="Alice")
    bob = User(name="Bob")
    doc = Document(owner=alice)
    can_bob_view = c.is_allowed(bob, "view", doc)
    assert not can_bob_view
    assert can_bob_view.reason is None


def test_piggyback_propagates_veto_reason() -> None:
    """raise_veto=True bubbles the Veto so the outer caller sees the reason."""
    c = Cadurso()

    @c.add_rule("edit")
    def anyone_can_edit(actor: User, _resource: Document) -> bool:
        return True

    @c.add_rule("edit")
    def suspended_cannot_edit(actor: User, _resource: Document) -> bool:
        if actor.name == "Suspended":
            raise Veto("account suspended")
        return False

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> AuthorizationDecision:
        return c.is_allowed(actor, "edit", resource, raise_veto=True)

    c.freeze()

    doc = Document(owner=User(name="Owner"))

    # Normal user: edit allowed, so view allowed
    can_normal_view = c.is_allowed(User(name="Normal"), "view", doc)
    assert can_normal_view

    # Suspended user: edit vetoed, veto bubbles through piggyback
    can_suspended_view = c.is_allowed(User(name="Suspended"), "view", doc)
    assert not can_suspended_view
    assert can_suspended_view.reason == "account suspended"


def test_piggyback_without_raise_veto_loses_reason() -> None:
    """Without raise_veto=True, the Veto reason is lost in the piggyback."""
    c = Cadurso()

    @c.add_rule("edit")
    def anyone_can_edit(actor: User, _resource: Document) -> bool:
        return True

    @c.add_rule("edit")
    def suspended_cannot_edit(actor: User, _resource: Document) -> bool:
        if actor.name == "Suspended":
            raise Veto("account suspended")
        return False

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> AuthorizationDecision:
        # No raise_veto — Veto is caught inside is_allowed, returns denied decision
        return c.is_allowed(actor, "edit", resource)

    c.freeze()

    doc = Document(owner=User(name="Owner"))
    can_suspended_view = c.is_allowed(User(name="Suspended"), "view", doc)
    assert not can_suspended_view
    assert can_suspended_view.reason is None  # reason lost


def test_piggyback_via_fluent_api_propagates_veto() -> None:
    """raise_veto=True works through the fluent can().do().on() API too."""
    c = Cadurso()

    @c.add_rule("edit")
    def anyone_can_edit(actor: User, _resource: Document) -> bool:
        return True

    @c.add_rule("edit")
    def suspended_cannot_edit(actor: User, _resource: Document) -> bool:
        if actor.name == "Suspended":
            raise Veto("account suspended")
        return False

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> AuthorizationDecision:
        return c.can(actor).do("edit").on(resource, raise_veto=True)

    c.freeze()

    doc = Document(owner=User(name="Owner"))
    can_suspended_view = c.is_allowed(User(name="Suspended"), "view", doc)
    assert not can_suspended_view
    assert can_suspended_view.reason == "account suspended"


def test_piggyback_with_bool_return_type_still_works() -> None:
    """Rules can still use -> bool with bool() wrapping if preferred."""
    c = Cadurso()

    @c.add_rule("edit")
    def owner_can_edit(actor: User, resource: Document) -> bool:
        return actor == resource.owner

    @c.add_rule("view")
    def can_view_if_can_edit(actor: User, resource: Document) -> bool:
        return bool(c.is_allowed(actor, "edit", resource, raise_veto=True))

    c.freeze()

    alice = User(name="Alice")
    doc = Document(owner=alice)
    assert c.is_allowed(alice, "view", doc)
    assert not c.is_allowed(User(name="Bob"), "view", doc)
