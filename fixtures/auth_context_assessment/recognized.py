# ruff: noqa: F821


def case(actor, resource):
    authorize(actor, "export", resource)
    export(resource)
