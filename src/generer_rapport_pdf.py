# -*- coding: utf-8 -*-

"""Génération du rapport PDF du projet NutriHFr."""

from pathlib import Path
import re

import markdown
from weasyprint import HTML, CSS

RACINE = Path(__file__).resolve().parents[1]
RAPPORT = RACINE / "reports" / "rapport_nutrihfr.md"
SORTIE = RACINE / "reports" / "rapport_nutrihfr.pdf"

texte = RAPPORT.read_text(encoding="utf-8")

# Conversion des formules LaTeX simples en notation lisible.
texte = re.sub(
    r"\\\[\s*CV\s*=.*?\\\]",
    "CV = (écart-type / moyenne) × 100",
    texte,
    flags=re.DOTALL,
)

texte = re.sub(
    r"\\\[\s*D_p\s*=.*?\\\]",
    "Densité protéique = (protéines / énergie) × 1 000",
    texte,
    flags=re.DOTALL,
)

texte = re.sub(
    r"\\\[\s*A_\{ij\}\s*=.*?\\\]",
    "Apport estimé = (quantité pondérée × teneur pour 100 g) / 100",
    texte,
    flags=re.DOTALL,
)

# Conversion de la formule de moyenne pondérée.
texte = re.sub(
    r"\\\[\s*\\overline\{x\}_w\s*=.*?\\\]",
    "Moyenne pondérée = Σ(wᵢ × xᵢ) / Σ(wᵢ)",
    texte,
    flags=re.DOTALL,
)

# Conversion des symboles grecs dans les explications.
texte = texte.replace(r"\(\sigma\)", "σ")
texte = texte.replace(r"\(\mu\)", "μ")

# Autres formules LaTeX : conserver une représentation textuelle.
texte = re.sub(
    r"\\\[(.*?)\\\]",
    lambda m: (
        '<div class="formule">'
        + m.group(1).replace("\\", "")
        + "</div>"
    ),
    texte,
    flags=re.DOTALL,
)

corps = markdown.markdown(
    texte,
    extensions=["tables", "fenced_code"],
)

html = f"""
<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
</head>
<body>
{corps}
</body>
</html>
"""

style = CSS(string="""
@page {
    size: A4;
    margin: 15mm 17mm;
}

body {
    font-family: "DejaVu Sans", sans-serif;
    font-size: 8.5pt;
    line-height: 1.28;
    color: #222;
}

h1 {
    font-size: 17pt;
    color: #183650;
    margin-bottom: 9px;
}

h2 {
    font-size: 12pt;
    color: #183650;
    margin-top: 14px;
    margin-bottom: 6px;
}

h3 {
    font-size: 10pt;
    color: #245475;
    margin-top: 10px;
    margin-bottom: 5px;
}

p {
    margin: 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 7.6pt;
    margin: 7px 0;
}

th, td {
    border: 1px solid #bbb;
    padding: 4px 5px;
}

th {
    background: #eaf0f4;
}

img {
    display: block;
    max-width: 100%;
    max-height: 72mm;
    width: auto;
    height: auto;
    margin: 5px auto;
}

pre {
    font-size: 7pt;
    white-space: pre-wrap;
}

.formule {
    text-align: center;
    margin: 8px;
    font-style: italic;
}

h2, h3, img, table {
    break-inside: avoid;
}
""")

documento = HTML(
    string=html,
    base_url=str(RAPPORT.parent),
).render(stylesheets=[style])

documento.write_pdf(SORTIE)

print(f"Rapport PDF : {SORTIE}")
print(f"Nombre de pages : {len(documento.pages)}")
