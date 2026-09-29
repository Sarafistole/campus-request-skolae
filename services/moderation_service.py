"""
Moteur de recommandation pour la modération des tickets.

Cette première version utilise volontairement des règles déterministes.
Les résultats constituent des recommandations destinées au modérateur,
et non des décisions administratives automatiques.
"""

import re
import unicodedata


VIGILANCE_LEVELS = ("NONE", "LOW", "MEDIUM", "HIGH")
PRIORITY_LEVELS = ("P0", "P1", "P2", "P3")


# Termes pouvant signaler une situation sensible.
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


# Mots très fréquents qui apportent peu d'information
# lors de la comparaison de deux tickets.
SIMILARITY_STOP_WORDS = {
    "a", "au", "aux", "avec", "ce", "ces", "dans", "de", "des",
    "du", "elle", "en", "et", "est", "il", "je", "la", "le",
    "les", "ma", "mais", "me", "mes", "mon", "ne", "nous", "on",
    "ou", "par", "pas", "pour", "que", "qui", "sa", "se", "ses",
    "son", "sur", "un", "une", "vous",
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

    vigilance_level = "NONE"
    priority = "P2"

    # Impact collectif déclaré.
    if scope == "GROUP":
        priority = "P1"
        reasons.append("Impact collectif déclaré")

    # Détection d'un sujet sensible.
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


def _normalize_text(text):
    """
    Normalise un texte pour la comparaison :
    minuscules et suppression des accents.
    """

    text = text or ""

    text = unicodedata.normalize("NFD", text)

    text = "".join(
        character
        for character in text
        if unicodedata.category(character) != "Mn"
    )

    return text.lower()


def _extract_significant_words(text):
    """
    Extrait les mots significatifs d'un texte.
    """

    normalized = _normalize_text(text)

    words = set(
        re.findall(r"[a-z0-9]+", normalized)
    )

    return {
        word
        for word in words
        if len(word) >= 3
        and word not in SIMILARITY_STOP_WORDS
    }


def calculate_similarity(
    title_a,
    description_a,
    tags_a,
    title_b,
    description_b,
    tags_b,
):
    """
    Calcule un indicateur de similarité entre deux tickets.

    Le résultat est compris entre 0 et 1.

    Pondération :
    - contenu textuel : 70 %
    - tags : 30 %

    Ce score est uniquement une aide au modérateur.
    Il ne classe jamais automatiquement un ticket comme doublon.
    """

    words_a = _extract_significant_words(
        f"{title_a or ''} {description_a or ''}"
    )

    words_b = _extract_significant_words(
        f"{title_b or ''} {description_b or ''}"
    )

    text_union = words_a | words_b
    text_intersection = words_a & words_b

    if text_union:
        text_score = len(text_intersection) / len(text_union)
    else:
        text_score = 0.0

    tag_names_a = {
        _normalize_text(
            getattr(tag, "name", str(tag))
        ).strip()
        for tag in (tags_a or [])
    }

    tag_names_b = {
        _normalize_text(
            getattr(tag, "name", str(tag))
        ).strip()
        for tag in (tags_b or [])
    }

    tag_union = tag_names_a | tag_names_b
    tag_intersection = tag_names_a & tag_names_b

    if tag_union:
        tag_score = len(tag_intersection) / len(tag_union)
    else:
        tag_score = 0.0

    score = (
        text_score * 0.70
        + tag_score * 0.30
    )

    return round(score, 2)
