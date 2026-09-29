import re

# ============================================================
# Configuration des seuils de qualité du texte
# ============================================================

TITLE_MIN_LENGTH = 5
TITLE_MAX_LENGTH = 255

DESCRIPTION_MIN_LENGTH = 30
DESCRIPTION_MAX_LENGTH = 5000

# Nombre minimal de caractères alphanumériques
# requis dans la description.
DESCRIPTION_MIN_SIGNIFICANT_CHARS = 20

# Longueur minimale à partir de laquelle un texte
# peut être considéré comme répétitif.
REPETITION_MIN_LENGTH = 6

# Nombre maximal de caractères distincts dans un texte
# considéré comme une répétition simple.
REPETITION_MAX_PATTERN_LENGTH = 2


# ============================================================
# Fonctions de validation
# ============================================================

def has_significant_content(text):
    """
    Vérifie que le texte contient au moins une lettre
    ou un chiffre.
    """
    return bool(re.search(r"[^\W_]", text, re.UNICODE))


def count_significant_chars(text):
    """
    Compte les lettres et les chiffres du texte.
    Les espaces et la ponctuation ne sont pas comptés.
    """
    return len(re.findall(r"[^\W_]", text, re.UNICODE))


def is_repetitive(text):
    """
    Détecte les textes manifestement répétitifs :
    - un seul caractère répété ;
    - un motif de 2 caractères maximum répété
      au moins 3 fois.

    Les espaces sont ignorés pour cette vérification.
    """
    compact = re.sub(r"\s+", "", text).lower()

    if len(compact) < REPETITION_MIN_LENGTH:
        return False

    # Exemple : aaaaaaaa
    if len(set(compact)) == 1:
        return True

    # Exemple : ababababab
    for pattern_length in range(
        1, REPETITION_MAX_PATTERN_LENGTH + 1
    ):
        pattern = compact[:pattern_length]

        if len(compact) >= pattern_length * 3:
            if pattern * (len(compact) // pattern_length) == compact:
                return True

    return False


def validate_title(title):
    """
    Retourne un message d'erreur si le titre est invalide,
    sinon None.
    """

    if len(title) < TITLE_MIN_LENGTH:
        return (
            f"Le titre doit contenir au moins "
            f"{TITLE_MIN_LENGTH} caractères."
        )

    if len(title) > TITLE_MAX_LENGTH:
        return (
            f"Le titre ne doit pas dépasser "
            f"{TITLE_MAX_LENGTH} caractères."
        )

    if not has_significant_content(title):
        return "Le titre doit contenir au moins une lettre ou un chiffre."

    if is_repetitive(title):
        return "Le titre semble répétitif. Veuillez le reformuler."

    return None


def validate_description(description):
    """
    Retourne un message d'erreur si la description est invalide,
    sinon None.
    """

    if len(description) < DESCRIPTION_MIN_LENGTH:
        return (
            f"La description doit contenir au moins "
            f"{DESCRIPTION_MIN_LENGTH} caractères."
        )

    if len(description) > DESCRIPTION_MAX_LENGTH:
        return (
            f"La description ne doit pas dépasser "
            f"{DESCRIPTION_MAX_LENGTH} caractères."
        )

    if not has_significant_content(description):
        return (
            "La description doit contenir au moins "
            "une lettre ou un chiffre."
        )

    if count_significant_chars(description) < DESCRIPTION_MIN_SIGNIFICANT_CHARS:
        return (
            "La description ne contient pas assez de texte significatif. "
            f"Ajoutez au moins "
            f"{DESCRIPTION_MIN_SIGNIFICANT_CHARS} lettres ou chiffres."
        )

    if is_repetitive(description):
        return (
            "La description semble répétitive. "
            "Veuillez fournir des informations plus détaillées."
        )

    return None
