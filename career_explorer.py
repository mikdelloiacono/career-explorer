import streamlit as st
import itertools
from collections import defaultdict

# ==============================
# LEVEL 0 — DATA MODEL
# ==============================
# You can extend this freely.
JOBS_DB = [
    {
        "name": "Sports Journalist",
        "tags": {"sport", "scrittura", "media"},
        "description": "Raccontare eventi sportivi con articoli, video o podcast.",
    },
    {
        "name": "UX Designer",
        "tags": {"design", "psicologia", "tecnologia", "creativita"},
        "description": "Progettazione di prodotti digitali centrati sulle persone.",
    },
    {
        "name": "Data Analyst",
        "tags": {"tecnologia", "numeri", "business", "analisi"},
        "description": "Analisi dati per prendere decisioni migliori.",
    },
    {
        "name": "Product Manager (Sport-Tech)",
        "tags": {"sport", "tecnologia", "business", "leadership"},
        "description": "Guida lo sviluppo di prodotti digitali nel mondo sportivo.",
    },
    {
        "name": "Content Creator",
        "tags": {"scrittura", "creativita", "media"},
        "description": "Creazione di contenuti online su temi specifici.",
    },
    {
        "name": "Mental Coach Sportivo",
        "tags": {"sport", "psicologia", "coaching"},
        "description": "Supporto mentale ad atleti e team.",
    },
    {
        "name": "Game Designer",
        "tags": {"tecnologia", "design", "creativita", "psicologia"},
        "description": "Progettazione di videogiochi e dinamiche di gioco.",
    },
    {
        "name": "Educatore Online",
        "tags": {"insegnamento", "scrittura", "media", "tecnologia"},
        "description": "Creazione di corsi e percorsi formativi digitali.",
    },
]

DEFAULT_INTERESTS = [
    "sport", "tecnologia", "psicologia", "scrittura", "musica", "design",
    "business", "analisi", "creativita", "media", "coaching", "insegnamento",
    "viaggi", "numeri", "leadership",
]

# ==============================
# HELPERS
# ==============================

def normalize_items(text: str):
    raw = [x.strip().lower() for x in text.split(",")]
    return [x for x in raw if x]


def generate_combinations(items):
    combos = []
    for r in range(1, len(items) + 1):
        combos.extend(itertools.combinations(items, r))
    return combos


def score_job(user_interests, job_tags, obsession_weights=None):
    """
    Level 2 scoring:
    - coverage: how many job tags match user interests
    - precision: overlap vs total job tags
    - optional anti-obsession penalty
    """
    user_set = set(user_interests)
    overlap = user_set.intersection(job_tags)

    if not overlap:
        return 0.0

    coverage = len(overlap) / max(1, len(user_set))
    precision = len(overlap) / max(1, len(job_tags))
    base_score = 0.6 * precision + 0.4 * coverage

    # LEVEL 4 — anti-obsession balancing
    penalty = 0.0
    if obsession_weights:
        for i in overlap:
            w = obsession_weights.get(i, 1.0)
            if w > 1.0:
                penalty += (w - 1.0) * 0.05

    return max(0.0, base_score - penalty)


def infer_hybrid_jobs(best_jobs):
    """
    LEVEL 3 — simple AI-like generation of new job ideas
    based on tag clusters.
    """
    suggestions = []
    names = [j["name"] for j in best_jobs[:5]]

    if "Sports Journalist" in names and "UX Designer" in names:
        suggestions.append(
            "UX Researcher per app sportive (unisce sport + psicologia + design)"
        )

    if "Data Analyst" in names and "Content Creator" in names:
        suggestions.append(
            "Data Storyteller (analisi dati + comunicazione)"
        )

    if any("Product Manager" in n for n in names):
        suggestions.append(
            "Founder di micro-prodotto digitale basato sulle tue passioni"
        )

    if not suggestions:
        suggestions.append(
            "Portfolio career: combina 2-3 attività part-time invece di un solo lavoro"
        )

    return suggestions


# ==============================
# STREAMLIT UI (LEVEL 1)
# ==============================

st.set_page_config(page_title="Career Combination Explorer", layout="wide")

st.title("🧭 Career Combination Explorer")
st.caption("Inserisci passioni → genera combinazioni → scopri lavori possibili")

with st.sidebar:
    st.header("⚙️ Configurazione")

    use_default = st.checkbox("Mostra interessi suggeriti", value=True)

    if use_default:
        selected_defaults = st.multiselect(
            "Seleziona interessi",
            options=DEFAULT_INTERESTS,
            default=["sport", "tecnologia", "scrittura"],
        )
    else:
        selected_defaults = []

    custom_text = st.text_input(
        "Aggiungi interessi (separati da virgola)",
        value="",
        placeholder="es. fotografia, neuroscienze, cucina",
    )

    st.subheader("🎚️ Modalità anti-ossessione (Level 4)")
    st.caption("Alza un interesse se senti che domina troppo: il ranking lo bilancerà.")

# Merge interests
custom_items = normalize_items(custom_text) if custom_text else []
interests = list(dict.fromkeys(selected_defaults + custom_items))

if not interests:
    st.info("Inserisci almeno un interesse per iniziare.")
    st.stop()

# Anti-obsession weights
obsession_weights = {}
with st.sidebar:
    for i in interests:
        obsession_weights[i] = st.slider(
            f"Peso {i}", min_value=1.0, max_value=3.0, value=1.0, step=0.1
        )

# ==============================
# LEVEL 1 — combinations engine
# ==============================

combos = generate_combinations(interests)

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("🔢 Combinazioni generate")
    st.metric("Totale combinazioni", len(combos))

    with st.expander("Mostra prime 50"):
        for c in combos[:50]:
            st.write("• " + " + ".join(c))

# ==============================
# LEVEL 2 — ranking jobs
# ==============================

scored = []
for job in JOBS_DB:
    s = score_job(interests, job["tags"], obsession_weights)
    if s > 0:
        scored.append((s, job))

scored.sort(key=lambda x: x[0], reverse=True)

with col2:
    st.subheader("⭐ Lavori consigliati (ranking intelligente)")

    if not scored:
        st.warning("Nessuna corrispondenza trovata. Prova ad aggiungere altri interessi.")
    else:
        for score, job in scored[:10]:
            pct = int(score * 100)
            st.markdown(f"### {job['name']} — {pct}% fit")
            st.write(job["description"])
            st.caption("Tag: " + ", ".join(sorted(job["tags"])))
            st.progress(min(score, 1.0))

# ==============================
# LEVEL 3 — AI-like suggestions
# ==============================

st.subheader("🧠 Idee di carriera generate (Level 3)")
if scored:
    hybrid = infer_hybrid_jobs([j for _, j in scored])
    for idea in hybrid:
        st.write("• " + idea)

# ==============================
# EXTRA: Explain levels
# ==============================

with st.expander("📚 Come sono implementati i 4 livelli"):
    st.markdown(
        """
**Level 1 — Interfaccia grafica**
- Form interattivo con Streamlit
- Selezione interessi e input libero

**Level 2 — Ranking intelligente**
- Scoring basato su overlap interessi/tag
- Ordinamento per compatibilità

**Level 3 — Suggerimenti AI-like**
- Generazione di ruoli ibridi da pattern di interessi

**Level 4 — Anti-ossessione**
- Slider per bilanciare interessi dominanti
- Penalità nel ranking per suggerire percorsi più equilibrati

Puoi estendere facilmente:
- database lavori più ampio
- esportazione PDF
- grafi delle carriere
- integrazione LLM/API
"""
    )
