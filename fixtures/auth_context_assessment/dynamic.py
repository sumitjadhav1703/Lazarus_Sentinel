# ruff: noqa: F821


def case(actor, resource):
    authorize(actor, required_action(resource), resource)
    export(resource)
