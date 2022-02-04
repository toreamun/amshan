"""OBject Identification System (OBIS)."""
from __future__ import annotations

from enum import Enum, auto
from re import compile as compile_regex
from re import Pattern
from typing import Optional, Tuple

from dataclasses import dataclass

REDUCED_OBIS_PATTERN = r"((?P<AR>\d{0,3}){1}-)?((?P<BR>\d{0,3}){1}:)?((?P<CR>\d{0,3})\.)(?P<DR>\d{0,3})?(\.(?P<ER>\d{0,3}))?(\*(?P<FR>\d{0,3}))?"
STANDARD_OBIS_PATTERN = r"(?P<AS>\d{0,3})\.(?P<BS>\d{0,3})\.(?P<CS>\d{0,3})\.(?P<DS>\d{0,3})\.(?P<ES>\d{0,3})\.(?P<FS>\d{0,3})?"
OBIS_PATTERN_BOTH = (
    f"(?P<STANDARD>{STANDARD_OBIS_PATTERN})|(?P<REDUCED>{REDUCED_OBIS_PATTERN})"
)

# Compiled obis regex
_obis_pattern: Pattern = compile_regex(OBIS_PATTERN_BOTH)

ObisTupple = Tuple[Optional[int], Optional[int], int, int, Optional[int], Optional[int]]
"""6 part tupple value of all elements in oder A, B, C, D, E, and F."""


def to_obis_tupple(
    obis_code: str,
) -> ObisTupple:
    """Create a 6 part tupple from obis-code string."""
    match = _obis_pattern.match(obis_code)
    if match:
        if match.group("REDUCED"):
            obis = match.group("AR", "BR", "CR", "DR", "ER", "FR")
            return (
                int(obis[0]) if obis[0] else None,
                int(obis[1]) if obis[1] else None,
                int(obis[2]),
                int(obis[3]),
                int(obis[4]) if obis[4] else None,
                int(obis[5]) if obis[5] else None,
            )

        if match.group("STANDARD"):
            obis = match.group("AS", "BS", "CS", "DS", "ES", "FS")
            return (
                int(obis[0]),
                int(obis[1]),
                int(obis[2]),
                int(obis[3]),
                int(obis[4]),
                int(obis[5]) if obis[5] else None,
            )

    raise ValueError(f"Not a valid obis code: '{obis_code}'")


class Obis:
    """
    Object Identification System (OBIS) code.

    OBIS codes identify data items used in energy metering equipment, in a hierarchical
    structure using six value groups A to F.

    OBIS Reduced ID is supported: <A-><B:>[C.][D]<.E><*F>
    """

    def __init__(
        self,
        obis_tupple: ObisTupple,
    ) -> None:
        """Init Obis."""
        self._groups: ObisTupple = obis_tupple

    @property
    def a(self) -> int | None:  # pylint: disable=invalid-name
        """
        Get group A.

        The value group A defines the media (energy type) to which the metering is related.
        """
        return self._groups[0]

    @property
    def b(self) -> int | None:  # pylint: disable=invalid-name
        """
        Get group B.

        The value group B defines the channel number, i.e. the number of the input of a metering
        equipment having several inputs for the measurement of energy of the same or different types
        (for example in data concentrators, registration units). Data from different sources can thus be
        identified. The definitions for this value group are independent from the value group A.
        """
        return self._groups[1]

    @property
    def c(self) -> int:  # pylint: disable=invalid-name
        """
        Get group C.

        The value group C defines the abstract or physical data items related to the information source
        concerned, for example current, voltage, power, volume, temperature. The definitions depend
        on the value of the value group A .

        Further processing, classification and storage methods are defined by value groups D, E and
        F.

        For abstract data, value groups D to F provide further classification of data identified by value
        groups A to C.
        """
        return self._groups[2]

    @property
    def d(self) -> int:  # pylint: disable=invalid-name
        """
        Get group D.

        The value group D defines types, or the result of the processing of physical quantities
        identified with the value groups A and C, according to various specific algorithms.
        The algorithms can deliver energy and demand quantities as well as other physical quantities.
        """
        return self._groups[3]

    @property
    def e(self) -> int | None:  # pylint: disable=invalid-name
        """
        Get group E.

        The value group E defines further processing or classification of quantities identified
        by value groups A to D.
        """
        return self._groups[4]

    @property
    def f(self) -> int | None:  # pylint: disable=invalid-name
        """
        Get group F.

        The value group F defines the storage of data, identified by value groups A to E,
        according to different billing periods. Where this is not relevant, this value group
        can be used for further classification.
        """
        return self._groups[5]

    def as_tupple(self) -> ObisTupple:
        """Obis as ObisTupple."""
        return self._groups

    def to_reduced_str(self) -> str:
        """To redused obis code format."""
        obis_code = ""
        if self._groups[0]:
            obis_code += f"{self._groups[0]}-"
        if self._groups[1]:
            obis_code += obis_code + f"{self._groups[1]}:"
        obis_code += f"{self._groups[2]}.{self._groups[3]}"
        if self._groups[4]:
            obis_code += f".{self._groups[4]}"
        if self._groups[5]:
            obis_code += f"*{self._groups[5]}"

        return obis_code

    def __eq__(self, other) -> bool:
        """Return True if both instances represents the same obis code."""
        if isinstance(other, Obis):
            return self._groups == other._groups
        try:
            other_obis = Obis.from_string(other)
            return self._groups == other_obis._groups
        except ValueError:
            return False

    def __hash__(self) -> int:
        """Return instance hash code."""
        return hash(self._groups)

    def __str__(self) -> str:
        """Return OBIS code as 6 part string."""
        if all(self._groups):
            return f"{self._groups[0]}.{self._groups[1]}.{self._groups[2]}.{self._groups[3]}.{self._groups[4]}.{self._groups[5]}"

        return self.to_reduced_str()

    def __repr__(self) -> str:
        """Return the “official” string representation."""
        return str(self)

    @classmethod
    def from_string(cls, obis_code: str) -> Obis:
        """Create from obis-code string."""
        return Obis(to_obis_tupple(obis_code))

    def filter_group_cde(self):
        """Filter out group C, D and E."""
        return Obis(
            (None, None, self._groups[2], self._groups[3], self._groups[4], None)
        )

    def to_group_cdr_str(self):
        """To OBIS C.D.E string."""
        return f"{self._groups[2]}.{self._groups[3]}.{self._groups[4]}"


class RegisterCategory(Enum):
    """Register categories."""

    ACTIVE_ENERGY = auto()
    """Active energy registers"""

    REACTIVE_ENERGY = auto()
    """Reactive energy registers"""

    APPARENT_ENERGY = auto()
    """Apparent energy registers"""

    ACTIVE_ENERGY_PHASES = auto()
    """Registers of active energy per phases"""

    MAX_DEMAND = auto()
    """Maximum demand registers"""

    CUM_MAX_DEMAND = auto()
    """Cumulative maximum demand registers"""

    CURRENT_PERIOD_DEMAND = auto()
    """Demands in a current demand period"""

    PREVIOUS_PERIOD_DEMAND = auto()
    """Demands in the last completed demand period"""

    INSTANTANEOUS_POWER = auto()
    """Instantaneous power registers"""

    EL_NET_QUALITY = auto()
    """Electricity network quality registers"""

    MISC = auto()
    """Miscellaneous registers used in sequences"""


class ObisUnit(Enum):
    """Unit used by OBIS codes."""

    KW = "kW"
    KWH = "kWh"
    KVAR = "kvar"
    KVARH = "kvarh"
    AMPERE = "A"
    VOLT = "V"


@dataclass(frozen=True)
class ObisInfo:
    """OBIS code information."""

    code: Obis
    category: RegisterCategory
    name: str
    unit: ObisUnit | None
    phase: int | None = None


OBIS_CODES = [
    ObisInfo(
        Obis.from_string("1.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive active instantaneous power (A+)",
        ObisUnit.KW,
    ),
    ObisInfo(
        Obis.from_string("2.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative active instantaneous power (A-)",
        ObisUnit.KW,
    ),
    ObisInfo(
        Obis.from_string("3.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive reactive instantaneous power (Q+)",
        ObisUnit.KVAR,
    ),
    ObisInfo(
        Obis.from_string("4.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative reactive instantaneous power (Q-)",
        ObisUnit.KVAR,
    ),
    ObisInfo(
        Obis.from_string("21.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive active instantaneous power (A+) in phase L1",
        ObisUnit.KW,
        1,
    ),
    ObisInfo(
        Obis.from_string("22.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative active instantaneous power (A-) in phase L1",
        ObisUnit.KW,
        1,
    ),
    ObisInfo(
        Obis.from_string("41.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive active instantaneous power (A+) in phase L2",
        ObisUnit.KW,
        2,
    ),
    ObisInfo(
        Obis.from_string("42.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative active instantaneous power (A-) in phase L2",
        ObisUnit.KW,
        2,
    ),
    ObisInfo(
        Obis.from_string("61.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive active instantaneous power (A+) in phase L3",
        ObisUnit.KW,
        3,
    ),
    ObisInfo(
        Obis.from_string("62.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative active instantaneous power (A-) in phase L3",
        ObisUnit.KW,
        3,
    ),
    ObisInfo(
        Obis.from_string("23.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive reactive instantaneous power (Q+) in phase L1",
        ObisUnit.KVAR,
        1,
    ),
    ObisInfo(
        Obis.from_string("24.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative reactive instantaneous power (Q-) in phase L2",
        ObisUnit.KVAR,
        1,
    ),
    ObisInfo(
        Obis.from_string("43.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive reactive instantaneous power (Q+) in phase L2",
        ObisUnit.KVAR,
        2,
    ),
    ObisInfo(
        Obis.from_string("44.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative reactive instantaneous power (Q-) in phase L2",
        ObisUnit.KVAR,
        2,
    ),
    ObisInfo(
        Obis.from_string("63.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Positive reactive instantaneous power (Q+) in phase L3",
        ObisUnit.KVAR,
        3,
    ),
    ObisInfo(
        Obis.from_string("64.7.0"),
        RegisterCategory.INSTANTANEOUS_POWER,
        "Negative reactive instantaneous power (Q-) in phase L3",
        ObisUnit.KVAR,
        3,
    ),
    ObisInfo(
        Obis.from_string("31.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous current (I) in phase L1",
        ObisUnit.AMPERE,
        1,
    ),
    ObisInfo(
        Obis.from_string("51.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous current (I) in phase L2",
        ObisUnit.AMPERE,
        2,
    ),
    ObisInfo(
        Obis.from_string("71.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous current (I) in phase L3",
        ObisUnit.AMPERE,
        3,
    ),
    ObisInfo(
        Obis.from_string("32.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous voltage (U) in phase L1",
        ObisUnit.VOLT,
        1,
    ),
    ObisInfo(
        Obis.from_string("52.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous voltage (U) in phase L2",
        ObisUnit.VOLT,
        2,
    ),
    ObisInfo(
        Obis.from_string("72.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous voltage (U) in phase L3",
        ObisUnit.VOLT,
        3,
    ),
    ObisInfo(
        Obis.from_string("33.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous power factor in phase L1",
        None,
        1,
    ),
    ObisInfo(
        Obis.from_string("53.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous power factor in phase L2",
        None,
        2,
    ),
    ObisInfo(
        Obis.from_string("73.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous power factor in phase L3",
        None,
        3,
    ),
    ObisInfo(
        Obis.from_string("13.7.0"),
        RegisterCategory.EL_NET_QUALITY,
        "Instantaneous power factor",
        None,
    ),
    ObisInfo(
        Obis.from_string("1.8.0"),
        RegisterCategory.ACTIVE_ENERGY,
        "Positive active energy (A+) total",
        ObisUnit.KWH,
    ),
    ObisInfo(
        Obis.from_string("2.8.0"),
        RegisterCategory.ACTIVE_ENERGY,
        "Negative active energy (A+) total",
        ObisUnit.KWH,
    ),
    ObisInfo(
        Obis.from_string("3.8.0"),
        RegisterCategory.REACTIVE_ENERGY,
        "Positive reactive energy (Q+) total",
        ObisUnit.KVARH,
    ),
    ObisInfo(
        Obis.from_string("4.8.0"),
        RegisterCategory.REACTIVE_ENERGY,
        "Negative reactive energy (Q-) total",
        ObisUnit.KVARH,
    ),
    ObisInfo(
        Obis.from_string("22.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Negative active energy (A-) in phase L1 total",
        ObisUnit.KWH,
        1,
    ),
    ObisInfo(
        Obis.from_string("42.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Negative active energy (A-) in phase L2 total",
        ObisUnit.KWH,
        2,
    ),
    ObisInfo(
        Obis.from_string("62.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Negative active energy (A-) in phase L3 total",
        ObisUnit.KWH,
        3,
    ),
    ObisInfo(
        Obis.from_string("21.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Positive active energy (A+) in phase L1 total",
        ObisUnit.KWH,
        1,
    ),
    ObisInfo(
        Obis.from_string("41.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Positive active energy (A+) in phase L2 total",
        ObisUnit.KWH,
        2,
    ),
    ObisInfo(
        Obis.from_string("61.8.0"),
        RegisterCategory.ACTIVE_ENERGY_PHASES,
        "Positive active energy (A+) in phase L3 total",
        ObisUnit.KWH,
        3,
    ),
]
