"""Job listing re-classification."""

from sentinel_suisse.services.job_reclassify import proposed_job_category


def test_proposed_refines_transport_to_bus() -> None:
    assert proposed_job_category("transport", "Conducteur TL région lausannoise") == "bus"
    assert proposed_job_category("logistics", "Chauffeur de bus TPG") == "bus"


def test_proposed_refines_other_sectors() -> None:
    assert proposed_job_category("other", "Plombier sanitaire 100%") == "trades"
    assert proposed_job_category("other", "Cuisinier de production") == "kitchen"
    assert proposed_job_category("other", "Réceptionniste d'hôtel") == "hotel"
    assert proposed_job_category("other", "Aide-soignant diplômé") == "care"


def test_proposed_keeps_specific_category() -> None:
    assert proposed_job_category("bus", "Conducteur TL") == "bus"
    assert proposed_job_category("warehouse", "Magasinier cariste") == "warehouse"
