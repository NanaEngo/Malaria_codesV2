from protein_prep_utils import chain_id_from_missing_key


class DummyChain:
    def __init__(self, chain_id):
        self.id = chain_id


def test_chain_id_from_missing_key_reads_chain_index_from_tuple():
    chains = [DummyChain("A"), DummyChain("B")]

    assert chain_id_from_missing_key((1, 221), chains) == "B"


def test_chain_id_from_missing_key_accepts_plain_chain_index():
    chains = [DummyChain("A"), DummyChain("B")]

    assert chain_id_from_missing_key(0, chains) == "A"
