# ruff: noqa: F821


def case(actor, resource):
    authorize(actor, "preview", resource)
    export(resource)
