# ruff: noqa: F821


def case(actor, resource):
    authorize(resource, "export", resource)
    export(resource)
