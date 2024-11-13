# See: http://isthe.com/chongo/tech/comp/fnv/

import functools
from typing import Callable


PRIMES = {
    32: 16777619,
    64: 1099511628211,
    128: 309485009821345068724781371,
    256: 374144419156711147060143317175368453031918731002211,
    512: 35835915874844867368919076489095108449946327955754392558399825615420669938882575126094039892345713852759,
    1024: 5016456510113118655434598811035278955030765345404790744303017523831112055108147451509157692220295382716162651878526895249385292291816524375083746691371804094271873160484737966720260389217684476157468082573,
}

OFFSET_BASIS = {
    32: 2166136261,
    64: 14695981039346656037,
    128: 144066263297769815596495629667062367629,
    256: 100029257958052580907070968620625704837092796014241193945225284501741471925557,
    512: 9659303129496669498009435400716310466090418745672637896108374329434462657994582932197716438449813051892206539805784495328239340083876191928701583869517785,
    1024: 14197795064947621068722070641403218320880622795441933960878474914617582723252296732303717722150864096521202355549365628174669108571814760471015076148029755969804077320157692458563003215304957150157403644460363550505412711285966361610267868082893823963790439336411086884584107735010676915,
}


def fnv_1a(hash_value: int, byte: int, bits: int) -> int:
    """Calculate FNV-1A hash for the specified byte."""
    return ensure_bits_count((hash_value ^ byte) * PRIMES[bits], bits)


def fnv(hash_value: int, byte: int, bits: int) -> int:
    """Calculate FNV hash for the specified byte."""
    return ensure_bits_count(hash_value * PRIMES[bits], bits) ^ byte


def hash(data: bytes, algorithm: Callable[[int, int, int], int] = fnv_1a, bits: int = 128) -> int:
    """Calculates the FNV hash for the specified data.

    Currently calculates only 128 bit hashes.
    FNV and FNV-1A variantions are supported.

    Args:
        data (iterable): bytes to calculate hash for.
        algorithm (callable): algorithm to calculate hash for every byte in
            iterable data.
        bits (int): resulting hash size in bits.
    """
    return functools.reduce(functools.partial(algorithm, bits=bits), data, OFFSET_BASIS[bits])


def ensure_bits_count(number: int, bits: int) -> int:
    """
    Args:
        number (int)
        bits (int): maximum desirable bit count.

    Returns:
        int: number with the specified maximum number of bits.
    """
    return number & ((1 << bits) - 1)
