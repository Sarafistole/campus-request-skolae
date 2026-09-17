/* =========================
   MENU
========================= */

const menuButton = document.querySelector(".menu-button");
const menu = document.querySelector(".menu");

menuButton.addEventListener("click", (event) => {
    event.stopPropagation();
    menu.classList.toggle("active");
});

/* =========================
   FERMER LE MENU EN CLIQUANT AILLEURS
========================= */

document.addEventListener("click", (event) => {

    if (
        !menu.contains(event.target) &&
        !menuButton.contains(event.target)
    ) {
        menu.classList.remove("active");
    }

});


/* =========================
   LIMITATION DES TAGS
   1 À 5 MAXIMUM
========================= */

const tagCheckboxes = document.querySelectorAll(
    'input[name="tag_ids"]'
);

tagCheckboxes.forEach(checkbox => {

    checkbox.addEventListener("change", () => {

        const selectedTags = document.querySelectorAll(
            'input[name="tag_ids"]:checked'
        );

        if (selectedTags.length > 5) {

            checkbox.checked = false;

            alert(
                "Vous pouvez sélectionner au maximum 5 sujets."
            );

        }

    });

});