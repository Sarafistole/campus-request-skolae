from services.moderation_service import analyse_ticket, calculate_similarity


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
print("\n--- Tests de similarité ---")


class FakeTag:
    def __init__(self, name):
        self.name = name


harcelement = FakeTag("Harcèlement")
planning = FakeTag("Planning")
restauration = FakeTag("Restauration")


similarity_cases = [
    (
        "Même incident reformulé",
        calculate_similarity(
            "Harcèlement dans ma classe",
            "Un étudiant me menace régulièrement pendant les cours.",
            [harcelement],
            "Problème de harcèlement en cours",
            "Je subis régulièrement des menaces de la part d'un étudiant.",
            [harcelement],
        ),
    ),
    (
        "Même tag, sujets différents",
        calculate_similarity(
            "Changement de salle",
            "Je voudrais connaître la nouvelle salle du cours.",
            [planning],
            "Emploi du temps incorrect",
            "Mon cours du vendredi n'apparaît pas dans mon planning.",
            [planning],
        ),
    ),
    (
        "Tickets différents",
        calculate_similarity(
            "Problème de planning",
            "Mon cours du lundi a disparu.",
            [planning],
            "Repas au restaurant",
            "Je souhaite signaler un problème avec mon repas.",
            [restauration],
        ),
    ),
    (
        "Texte identique",
        calculate_similarity(
            "Cours annulé",
            "Le cours de réseau est annulé aujourd'hui.",
            [planning],
            "Cours annulé",
            "Le cours de réseau est annulé aujourd'hui.",
            [planning],
        ),
    ),
    (
        "Accents différents",
        calculate_similarity(
            "Problème de réseau",
            "Le réseau du campus est déconnecté.",
            [],
            "Probleme de reseau",
            "Le reseau du campus est deconnecte.",
            [],
        ),
    ),
]


for name, score in similarity_cases:
    print(
        f"{name:<28} | "
        f"score={score:.2f} "
        f"({score * 100:.0f} %)"
    )

# Validation des comportements attendus.
scores = {
    name: score
    for name, score in similarity_cases
}

assert scores["Même incident reformulé"] >= 0.50
assert scores["Même tag, sujets différents"] < 0.50
assert scores["Tickets différents"] < 0.50
assert scores["Texte identique"] == 1.00
assert scores["Accents différents"] >= 0.50

print("\nTous les tests de similarité passent.")
