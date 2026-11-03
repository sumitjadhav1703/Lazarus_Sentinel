def transfer():
    if configured_consent:
        check_consent("partner")
    handoff("partner")
