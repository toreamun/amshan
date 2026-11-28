"""Decode a corpus of real, public meter messages and compare with stored snapshots.

The corpus in tests/corpus is collected from public GitHub issues. Meter ids are
replaced with fake values and checksums recomputed. Any change in decoded output
shows up as a snapshot diff (update with `pytest --snapshot-update` when intended).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from syrupy.assertion import SnapshotAssertion

from han import dlde, hdlc
from han.autodecoder import AutoDecoder

CORPUS = sorted((Path(__file__).parent / "corpus").glob("*.hex"))


def read_corpus_file(path: Path) -> bytes:
    lines = path.read_text().splitlines()
    return bytes.fromhex("".join(x for x in lines if not x.startswith("#")))


def decode(path: Path) -> tuple[str | None, dict[str, Any] | None]:
    data = read_corpus_file(path)
    decoder = AutoDecoder()
    messages: list[hdlc.HdlcFrame] | list[dlde.DataReadout]
    if "_hdlc_" in path.name:
        messages = hdlc.HdlcFrameReader(use_octet_stuffing=False).read(data)
    elif "_p1_" in path.name:
        messages = dlde.ModeDReader().read(data)
    else:
        return None, decoder.decode_message_payload(data)

    assert len(messages) == 1
    assert messages[0].is_valid
    return messages[0].message_type.name, decoder.decode_message(messages[0])


def test_corpus_is_present() -> None:
    assert len(CORPUS) >= 10


@pytest.mark.parametrize("path", CORPUS, ids=[p.stem for p in CORPUS])
def test_decode_corpus(path: Path, snapshot: SnapshotAssertion) -> None:
    message_type, decoded = decode(path)

    assert decoded is not None
    assert {"message_type": message_type, "decoded": decoded} == snapshot
