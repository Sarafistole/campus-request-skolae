from services.moderation_service import analyse_ticket


def check(name, result, vigilance, priority):
    ok = (
        result["vigilance_level"] == vigilance
        and result["priority"] == priority
    )

    print(
        f"{'OK' if ok else 'ERREUR'} | "
        f"{name:<25} | "
        f"vigilance={result['vigilance_level']} "
        f"priority={result['priority']} "
        f"reasons={result['moderation_reasons']}"
    )

    if not ok:
        raise AssertionError(name)


# Ticket classique
check(
    "Ticket normal",
    analyse_ticket(
        "Question planning",
        "Je voudrais connaître ma salle de cours.",
        "SELF",
    ),
    "NONE",
    "P2",
)


# Impact collectif
check(
    "Impact collectif",
    analyse_ticket(
        "Problème de planning",
        "Notre classe rencontre un problème.",
        "GROUP",
    ),
    "NONE",
    "P1",
)


# Sujet sensible
check(
    "Harcèlement",
    analyse_ticket(
        "Situation préoccupante",
        "Je souhaite signaler un harcèlement.",
        "SELF",
    ),
    "HIGH",
    "P1",
)


# Impact collectif + sujet sensible
check(
    "Collectif sensible",
    analyse_ticket(
        "Situation dans ma classe",
        "Plusieurs étudiants subissent des menaces.",
        "GROUP",
    ),
    "HIGH",
    "P0",
)


# Variante sans accent
check(
    "Mot sans accent",
    analyse_ticket(
        "Signalement",
        "Je souhaite signaler un cas de harcelement.",
        "SELF",
    ),
    "HIGH",
    "P1",
)


print("\nTous les tests de modération passent.")