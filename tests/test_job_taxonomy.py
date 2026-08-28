"""Hierarchical job category matching."""

from sentinel_suisse.services.job_taxonomy import (
    canonical_job_category,
    classify_job_category,
    job_category_matches,
    title_needles_for_filter,
)


def test_same_leaf() -> None:
    assert job_category_matches("nursing", "nursing") is True


def test_descendant_matches_parent_field() -> None:
    assert job_category_matches("nursing", "healthcare") is True
    assert job_category_matches("bus", "transport") is True
    assert job_category_matches("bus", "logistics") is True


def test_parent_does_not_match_more_specific_filter() -> None:
    assert job_category_matches("healthcare", "nursing") is False
    assert job_category_matches("transport", "bus") is False


def test_siblings_do_not_match() -> None:
    assert job_category_matches("nursing", "doctor") is False
    assert job_category_matches("soc", "software") is False
    assert job_category_matches("warehouse", "transport") is False
    assert job_category_matches("truck", "bus") is False


def test_different_fields() -> None:
    assert job_category_matches("nursing", "architecture") is False
    assert job_category_matches("it", "healthcare") is False


def test_null_safe() -> None:
    assert job_category_matches(None, "nursing") is False
    assert job_category_matches("nursing", None) is True
    assert job_category_matches(None, "other") is True


def test_adzuna_labels_map_to_fields() -> None:
    assert canonical_job_category("IT Jobs") == "it"
    assert canonical_job_category("it-jobs") == "it"
    assert job_category_matches("IT Jobs", "it") is True
    assert job_category_matches("Admin Jobs", "it") is False
    assert job_category_matches("Legal Jobs", "other") is True
    assert canonical_job_category("Développement informatique") == "it"


def test_unknown_adzuna_tag_uses_job_title() -> None:
    assert canonical_job_category("Unknown") is None
    assert classify_job_category("Unknown", "Développeur Full Stack") == "software"
    assert (
        classify_job_category("engineering-jobs", "Analyste Test / Recette fonctionnelle")
        == "software"
    )
    assert classify_job_category("Unknown", "Carrossier / Mécanicien") == "trades"
    assert classify_job_category("Unknown", "Collaborateur comptable autonome") == "accounting"
    assert classify_job_category(None, "Paysagiste (H/F)") == "construction"
    assert classify_job_category("Unknown", "Horloger rhabilleur") == "restoration"
    assert classify_job_category("manufacturing-jobs", "Watchmaker / polisseur") == "polishing"
    assert classify_job_category("logistics", "Chauffeur de bus") == "bus"
    assert classify_job_category("logistics", "Magasinier") == "warehouse"
    assert classify_job_category("healthcare", "Infirmier Spitex") == "homecare"
    assert classify_job_category("Unknown", "Kleinbusfahrer:in 20-50 %") == "bus"
    assert classify_job_category("Unknown", "Conducteur-trice TPG") == "bus"
    assert classify_job_category("Unknown", "Chauffeur de taxi Genève") == "taxi"
    assert classify_job_category("Unknown", "Livreur Uber Eats Lausanne") == "delivery"
    assert classify_job_category("Unknown", "Florist/-in EFZ, BP oder HFP") == "florist"
    assert classify_job_category("Unknown", "Fleuriste 80%") == "florist"
    assert classify_job_category("sales", "Caissière-vendeuse / caissier-vendeur") == "cashier"


def test_logistics_and_purchasing_titles() -> None:
    assert classify_job_category("Unknown", "Acheteur industriel H/F") == "purchasing"
    assert classify_job_category("Unknown", "Responsable approvisionnement") == "purchasing"
    assert classify_job_category("logistics", "Magasinier / cariste") == "warehouse"
    assert classify_job_category("Unknown", "Préparateur de commandes") == "warehouse"
    assert classify_job_category("Unknown", "Logisticien supply chain") == "purchasing"
    assert job_category_matches("other", "warehouse", "Magasinier entrepôt") is True
    assert job_category_matches("logistics", "purchasing", "Acheteur junior") is True
    assert job_category_matches("logistics", "warehouse", "Acheteur junior") is False


def test_purchasing_title_needles() -> None:
    needles = title_needles_for_filter("purchasing")
    assert "%acheteur%" in needles
    assert "%approvisionnement%" in needles
    warehouse_needles = title_needles_for_filter("warehouse")
    assert "%magasinier%" in warehouse_needles
    assert "%stockiste%" in warehouse_needles


def test_title_refines_transport_alerts() -> None:
    assert job_category_matches("logistics", "transport", "Chauffeur poids lourd") is True
    assert job_category_matches("logistics", "bus", "Chauffeur poids lourd") is False
    assert job_category_matches("logistics", "transport", "Magasinier") is False
    assert job_category_matches("logistics", "warehouse", "Magasinier") is True
    assert job_category_matches("other", "bus", "Conducteur TPG lignes urbaines") is True
    assert job_category_matches("other", "taxi", "Chauffeur VTC") is True
    assert job_category_matches("other", "bus", "Chauffeur VTC") is False
