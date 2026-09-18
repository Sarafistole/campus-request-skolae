"""
Moteur de recommandation pour la modération des tickets.

Cette première version utilise volontairement des règles déterministes.
Les résultats constituent des recommandations destinées au modérateur,
et non des décisions administratives automatiques.
"""


VIGILANCE_LEVELS = ("NONE", "LOW", "MEDIUM", "HIGH")
PRIORITY_LEVELS = ("P0", "P1", "P2", "P3")


# Termes pouvant signaler une situation sensible.
# La présence d'un terme déclenche une vigilance renforcée,
# mais ne constitue jamais à elle seule une décision de modération.
SENSITIVE_KEYWORDS = {
    "harcèlement",
    "harcelement",
    "menace",
    "menaces",
    "violence",
    "agression",
    "agressé",
    "agresse",
    "discrimination",
    "racisme",
    "danger",
    "dangereux",
    "urgence",
}


def analyse_ticket(title, description, scope, tags=None):
    """
    Produit les recommandations initiales de modération d'un ticket.

    Retour :
        {
            "vigilance_level": "NONE|LOW|MEDIUM|HIGH",
            "priority": "P0|P1|P2|P3",
            "moderation_reasons": [...]
        }
    """

    tags = tags or []

    title = title or ""
    description = description or ""

    tag_names = [
        getattr(tag, "name", str(tag)).lower()
        for tag in tags
    ]

    searchable_text = " ".join(
        [
            title.lower(),
            description.lower(),
            *tag_names,
        ]
    )

    reasons = []

    # Valeurs normales par défaut.
    vigilance_level = "NONE"
    priority = "P2"

    # Une situation concernant un groupe mérite une remontée
    # dans la file de modération.
    if scope == "GROUP":
        priority = "P1"
        reasons.append("Impact collectif déclaré")

    detected_keywords = sorted(
        keyword
        for keyword in SENSITIVE_KEYWORDS
        if keyword in searchable_text
    )

    if detected_keywords:
        vigilance_level = "HIGH"

        if scope == "GROUP":
            priority = "P0"
        else:
            priority = "P1"

        reasons.append("Sujet sensible détecté")

    return {
        "vigilance_level": vigilance_level,
        "priority": priority,
        "moderation_reasons": reasons,
    }