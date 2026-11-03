# ruff: noqa: F821


def case(actor, resource):
    authorize(actor, "export", actor)
    export(resource)
