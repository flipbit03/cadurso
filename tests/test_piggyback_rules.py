"""Tests for piggyback rules — rules that delegate to is_allowed() internally."""

from dataclasses import dataclass

import pytest

from cadurso import Cadurso


@dataclass
class User:
    name: str
    admin: bool = False


@dataclass
class Document:
    owner: User


@pytest.fixture
def authz(user_alice: User, user_bob: User) -> Cadurso:
    c = Cadurso()

    @c.add_rule("edit")
    def owner_can_edit(actor: User, resource: Document) -> bool:
        return actor == resource.owner

    @c.add_rule("edit")
    def admin_can_edit(actor: User, _resource: Document) -> bool:
        return actor.admin

    @c.add_rule("view")
    def anyone_who_can_edit_can_view(actor: User, resource: Document) -> bool:
        """Piggyback: delegate to the edit permission."""
        return bool(c.is_allowed(actor, "edit", resource))

    @c.add_rule("view")
    def anyone_who_can_edit_can_view_via_query(
        actor: User, resource: Document
    ) -> bool:
        """Piggyback via fluent API."""
        return bool(c.can(actor).do("edit").on(resource))

    c.freeze()
    return c


@pytest.fixture
def user_alice() -> User:
    return User(name="Alice")


@pytest.fixture
def user_bob() -> User:
    return User(name="Bob", admin=True)


def test_owner_can_view_own_document(
    authz: Cadurso, user_alice: User
) -> None:
    """Alice owns the doc, so edit is allowed, and view piggybacks on edit."""
    doc = Document(owner=user_alice)
    assert authz.is_allowed(user_alice, "view", doc)


def test_admin_can_view_any_document(
    authz: Cadurso, user_alice: User, user_bob: User
) -> None:
    """Bob is admin, so edit is allowed, and view piggybacks on edit."""
    doc = Document(owner=user_alice)
    assert authz.is_allowed(user_bob, "view", doc)


def test_non_owner_non_admin_cannot_view(
    authz: Cadurso, user_alice: User
) -> None:
    """Alice can't view Bob's doc (she's not admin, not owner)."""
    bob = User(name="Bob")
    doc = Document(owner=bob)
    can_alice_view = authz.is_allowed(user_alice, "view", doc)
    assert not can_alice_view
    assert can_alice_view.reason is None


def test_piggyback_with_veto() -> None:
    """A piggybacked rule correctly reflects a Veto from the delegated permission."""
    from cadurso import Veto

    c = Cadurso()

    @c.add_rule("write")
    def anyone_can_write(actor: User, _resource: Document) -> bool:
        return True

    @c.add_rule("write")
    def suspended_cannot_write(actor: User, _resource: Document) -> bool:
        if actor.name == "Suspended":
            raise Veto("account suspended")
        return False

    @c.add_rule("publish")
    def publish_requires_write(actor: User, resource: Document) -> bool:
        """Piggyback: can only publish if you can write."""
        return bool(c.is_allowed(actor, "write", resource))

    c.freeze()

    doc = Document(owner=User(name="Owner"))

    can_normal_publish = c.is_allowed(User(name="Normal"), "publish", doc)
    assert can_normal_publish

    can_suspended_publish = c.is_allowed(User(name="Suspended"), "publish", doc)
    assert not can_suspended_publish
