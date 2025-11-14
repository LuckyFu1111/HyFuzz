"""
Advanced Mutation Engine for HyFuzz

Implements 20+ mutation strategies including:
- Bit/byte level mutations
- Block-level mutations
- Dictionary-based mutations
- Protocol-aware mutations
- Arithmetic mutations
- Interesting values

Author: HyFuzz Team
Version: 2.0.0
Date: 2025-01-13
"""

import random
import struct
from typing import List, Set, Dict, Any, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ==============================================================================
# INTERESTING VALUES (AFL-style)
# ==============================================================================

# Interesting 8-bit values
INTERESTING_8 = [
    -128, -1, 0, 1, 16, 32, 64, 100, 127
]

# Interesting 16-bit values
INTERESTING_16 = [
    -32768, -129, 128, 255, 256, 512, 1000, 1024, 4096, 32767
]

# Interesting 32-bit values
INTERESTING_32 = [
    -2147483648, -100663046, -32769, 32768, 65535, 65536,
    100663045, 2147483647
]

# Protocol-specific dictionaries
SQL_KEYWORDS = [
    b"SELECT", b"UNION", b"DROP", b"INSERT", b"UPDATE", b"DELETE",
    b"' OR '1'='1", b"'; --", b"admin'--", b"1' AND '1'='1",
]

XSS_PAYLOADS = [
    b"<script>alert(1)</script>",
    b"<img src=x onerror=alert(1)>",
    b"javascript:alert(1)",
    b"<svg onload=alert(1)>",
]

PATH_TRAVERSAL = [
    b"../", b"..\\", b"....//", b"..../",
    b"..%2F", b"%2e%2e%2f", b"..%252f",
]

BUFFER_OVERFLOW = [
    b"A" * 100, b"A" * 256, b"A" * 1000, b"A" * 4096,
    b"%n" * 100, b"%s" * 100, b"%x" * 100,
]

FORMAT_STRING = [
    b"%s%s%s%s%s", b"%x%x%x%x%x", b"%n%n%n%n%n",
    b"%08x.%08x.%08x.%08x", b"AAAA%08x.%08x",
]


# ==============================================================================
# MUTATION ENGINE
# ==============================================================================

class AdvancedMutationEngine:
    """
    Advanced mutation engine with 20+ strategies
    """

    def __init__(self,
                 dictionary: Optional[List[bytes]] = None,
                 protocol: Optional[str] = None):
        """
        Initialize mutation engine

        Args:
            dictionary: Custom dictionary for mutations
            protocol: Target protocol for protocol-aware mutations
        """
        self.dictionary = dictionary or []
        self.protocol = protocol
        self.logger = logging.getLogger(__name__)

        # Load protocol-specific dictionary
        self._load_protocol_dict()

        self.logger.info(f"AdvancedMutationEngine initialized (protocol={protocol})")

    def _load_protocol_dict(self):
        """Load protocol-specific dictionary"""
        if self.protocol:
            if self.protocol.lower() in ['http', 'https']:
                self.dictionary.extend(XSS_PAYLOADS)
                self.dictionary.extend(PATH_TRAVERSAL)
            elif self.protocol.lower() in ['sql', 'mysql', 'postgres']:
                self.dictionary.extend(SQL_KEYWORDS)
            # Add more protocol-specific dictionaries

    # ==========================================================================
    # BIT-LEVEL MUTATIONS
    # ==========================================================================

    def bit_flip_1(self, data: bytes) -> List[bytes]:
        """Flip single bit at random position"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data) * 8, 100)):  # Limit mutations
            pos = random.randint(0, len(data) - 1)
            bit = random.randint(0, 7)
            mutated = bytearray(data)
            mutated[pos] ^= (1 << bit)
            mutations.append(bytes(mutated))

        return mutations

    def bit_flip_2(self, data: bytes) -> List[bytes]:
        """Flip two consecutive bits"""
        if len(data) < 1:
            return [data]

        mutations = []
        for _ in range(min(len(data) * 8, 50)):
            pos = random.randint(0, len(data) - 1)
            bit = random.randint(0, 6)
            mutated = bytearray(data)
            mutated[pos] ^= (3 << bit)  # Flip 2 bits
            mutations.append(bytes(mutated))

        return mutations

    def bit_flip_4(self, data: bytes) -> List[bytes]:
        """Flip four consecutive bits"""
        if len(data) < 1:
            return [data]

        mutations = []
        for _ in range(min(len(data) * 8, 25)):
            pos = random.randint(0, len(data) - 1)
            bit = random.randint(0, 4)
            mutated = bytearray(data)
            mutated[pos] ^= (0xF << bit)  # Flip 4 bits
            mutations.append(bytes(mutated))

        return mutations

    # ==========================================================================
    # BYTE-LEVEL MUTATIONS
    # ==========================================================================

    def byte_flip(self, data: bytes) -> List[bytes]:
        """Flip entire byte"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data), 50)):
            pos = random.randint(0, len(data) - 1)
            mutated = bytearray(data)
            mutated[pos] ^= 0xFF
            mutations.append(bytes(mutated))

        return mutations

    def byte_random(self, data: bytes) -> List[bytes]:
        """Replace byte with random value"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data), 50)):
            pos = random.randint(0, len(data) - 1)
            mutated = bytearray(data)
            mutated[pos] = random.randint(0, 255)
            mutations.append(bytes(mutated))

        return mutations

    # ==========================================================================
    # ARITHMETIC MUTATIONS
    # ==========================================================================

    def arithmetic_inc(self, data: bytes, amount: int = 1) -> List[bytes]:
        """Increment byte values"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data), 20)):
            pos = random.randint(0, len(data) - 1)
            mutated = bytearray(data)
            mutated[pos] = (mutated[pos] + amount) % 256
            mutations.append(bytes(mutated))

        return mutations

    def arithmetic_dec(self, data: bytes, amount: int = 1) -> List[bytes]:
        """Decrement byte values"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data), 20)):
            pos = random.randint(0, len(data) - 1)
            mutated = bytearray(data)
            mutated[pos] = (mutated[pos] - amount) % 256
            mutations.append(bytes(mutated))

        return mutations

    # ==========================================================================
    # INTERESTING VALUES
    # ==========================================================================

    def interesting_8bit(self, data: bytes) -> List[bytes]:
        """Replace with interesting 8-bit values"""
        if not data:
            return [data]

        mutations = []
        for _ in range(min(len(data), 20)):
            pos = random.randint(0, len(data) - 1)
            value = random.choice(INTERESTING_8)
            mutated = bytearray(data)
            mutated[pos] = value & 0xFF
            mutations.append(bytes(mutated))

        return mutations

    def interesting_16bit(self, data: bytes) -> List[bytes]:
        """Replace with interesting 16-bit values"""
        if len(data) < 2:
            return [data]

        mutations = []
        for _ in range(min(len(data) // 2, 20)):
            pos = random.randint(0, len(data) - 2)
            value = random.choice(INTERESTING_16)
            mutated = bytearray(data)
            # Try both endianness
            for endian in ['<', '>']:
                m = bytearray(mutated)
                struct.pack_into(f'{endian}h', m, pos, value)
                mutations.append(bytes(m))

        return mutations

    def interesting_32bit(self, data: bytes) -> List[bytes]:
        """Replace with interesting 32-bit values"""
        if len(data) < 4:
            return [data]

        mutations = []
        for _ in range(min(len(data) // 4, 20)):
            pos = random.randint(0, len(data) - 4)
            value = random.choice(INTERESTING_32)
            mutated = bytearray(data)
            # Try both endianness
            for endian in ['<', '>']:
                m = bytearray(mutated)
                struct.pack_into(f'{endian}i', m, pos, value)
                mutations.append(bytes(m))

        return mutations

    # ==========================================================================
    # BLOCK-LEVEL MUTATIONS
    # ==========================================================================

    def block_delete(self, data: bytes) -> List[bytes]:
        """Delete random block"""
        if len(data) < 2:
            return [data]

        mutations = []
        for _ in range(5):
            start = random.randint(0, len(data) - 1)
            length = random.randint(1, min(len(data) - start, 64))
            mutated = data[:start] + data[start + length:]
            if mutated:  # Don't return empty
                mutations.append(mutated)

        return mutations

    def block_duplicate(self, data: bytes) -> List[bytes]:
        """Duplicate random block"""
        if len(data) < 2:
            return [data]

        mutations = []
        for _ in range(5):
            start = random.randint(0, len(data) - 1)
            length = random.randint(1, min(len(data) - start, 64))
            block = data[start:start + length]
            # Insert at random position
            insert_pos = random.randint(0, len(data))
            mutated = data[:insert_pos] + block + data[insert_pos:]
            mutations.append(mutated)

        return mutations

    def block_swap(self, data: bytes) -> List[bytes]:
        """Swap two random blocks"""
        if len(data) < 4:
            return [data]

        mutations = []
        for _ in range(5):
            # Select two blocks
            pos1 = random.randint(0, len(data) - 2)
            len1 = random.randint(1, min(len(data) - pos1, 32))
            pos2 = random.randint(0, len(data) - 2)
            len2 = random.randint(1, min(len(data) - pos2, 32))

            if pos1 + len1 <= pos2 or pos2 + len2 <= pos1:  # Non-overlapping
                mutated = bytearray(data)
                block1 = mutated[pos1:pos1 + len1]
                block2 = mutated[pos2:pos2 + len2]
                # Swap
                mutated[pos1:pos1 + len1] = block2
                mutated[pos2:pos2 + len2] = block1
                mutations.append(bytes(mutated))

        return mutations

    def block_insert(self, data: bytes) -> List[bytes]:
        """Insert random block"""
        mutations = []
        for _ in range(5):
            pos = random.randint(0, len(data))
            length = random.randint(1, 64)
            block = bytes([random.randint(0, 255) for _ in range(length)])
            mutated = data[:pos] + block + data[pos:]
            mutations.append(mutated)

        return mutations

    # ==========================================================================
    # DICTIONARY-BASED MUTATIONS
    # ==========================================================================

    def dictionary_replace(self, data: bytes) -> List[bytes]:
        """Replace part of data with dictionary entry"""
        if not self.dictionary or not data:
            return [data]

        mutations = []
        for _ in range(min(len(self.dictionary), 10)):
            dict_entry = random.choice(self.dictionary)
            pos = random.randint(0, max(0, len(data) - len(dict_entry)))
            mutated = data[:pos] + dict_entry + data[pos + len(dict_entry):]
            mutations.append(mutated)

        return mutations

    def dictionary_insert(self, data: bytes) -> List[bytes]:
        """Insert dictionary entry"""
        if not self.dictionary:
            return [data]

        mutations = []
        for _ in range(min(len(self.dictionary), 10)):
            dict_entry = random.choice(self.dictionary)
            pos = random.randint(0, len(data))
            mutated = data[:pos] + dict_entry + data[pos:]
            mutations.append(mutated)

        return mutations

    # ==========================================================================
    # PROTOCOL-AWARE MUTATIONS
    # ==========================================================================

    def sql_injection(self, data: bytes) -> List[bytes]:
        """SQL injection mutations"""
        mutations = []
        for payload in SQL_KEYWORDS[:10]:
            # Try different positions
            for pos in [0, len(data) // 2, len(data)]:
                mutated = data[:pos] + payload + data[pos:]
                mutations.append(mutated)
        return mutations

    def xss_injection(self, data: bytes) -> List[bytes]:
        """XSS injection mutations"""
        mutations = []
        for payload in XSS_PAYLOADS[:10]:
            for pos in [0, len(data) // 2, len(data)]:
                mutated = data[:pos] + payload + data[pos:]
                mutations.append(mutated)
        return mutations

    def path_traversal(self, data: bytes) -> List[bytes]:
        """Path traversal mutations"""
        mutations = []
        for payload in PATH_TRAVERSAL[:10]:
            for pos in [0, len(data) // 2, len(data)]:
                mutated = data[:pos] + payload + data[pos:]
                mutations.append(mutated)
        return mutations

    def buffer_overflow_patterns(self, data: bytes) -> List[bytes]:
        """Buffer overflow patterns"""
        return BUFFER_OVERFLOW[:10]

    def format_string_patterns(self, data: bytes) -> List[bytes]:
        """Format string patterns"""
        return FORMAT_STRING[:10]

    # ==========================================================================
    # HAVOC MUTATIONS (STACKED MUTATIONS)
    # ==========================================================================

    def havoc(self, data: bytes, num_stages: int = 3) -> List[bytes]:
        """
        Apply multiple random mutations in sequence (havoc mode)

        Args:
            data: Input data
            num_stages: Number of mutation stages

        Returns:
            List of heavily mutated data
        """
        mutations = [data]

        for _ in range(5):  # Generate 5 havoc mutations
            mutated = data
            for _ in range(num_stages):
                # Select random mutation
                mutation_func = random.choice([
                    self.bit_flip_1,
                    self.byte_flip,
                    self.arithmetic_inc,
                    self.block_duplicate,
                    self.dictionary_insert,
                ])
                results = mutation_func(mutated)
                if results:
                    mutated = random.choice(results)

            mutations.append(mutated)

        return mutations

    # ==========================================================================
    # MAIN MUTATION INTERFACE
    # ==========================================================================

    def mutate(self,
               data: bytes,
               strategy: Optional[str] = None,
               count: int = 10) -> List[bytes]:
        """
        Generate mutations using specified strategy or random

        Args:
            data: Input data to mutate
            strategy: Specific strategy name (or None for random)
            count: Maximum number of mutations to generate

        Returns:
            List of mutated data
        """
        if not data:
            return [data]

        # Select strategy
        if strategy:
            mutation_func = getattr(self, strategy, None)
            if not mutation_func:
                self.logger.warning(f"Unknown strategy: {strategy}")
                return [data]
        else:
            # Random strategy
            strategies = [
                'bit_flip_1', 'bit_flip_2', 'bit_flip_4',
                'byte_flip', 'byte_random',
                'arithmetic_inc', 'arithmetic_dec',
                'interesting_8bit', 'interesting_16bit', 'interesting_32bit',
                'block_delete', 'block_duplicate', 'block_swap', 'block_insert',
                'dictionary_replace', 'dictionary_insert',
                'havoc'
            ]

            # Add protocol-specific strategies
            if self.protocol:
                if self.protocol.lower() in ['http', 'https']:
                    strategies.extend(['xss_injection', 'path_traversal'])
                elif self.protocol.lower() in ['sql', 'mysql']:
                    strategies.append('sql_injection')

            strategy = random.choice(strategies)
            mutation_func = getattr(self, strategy)

        # Generate mutations
        try:
            mutations = mutation_func(data)
            return mutations[:count]
        except Exception as e:
            self.logger.error(f"Mutation failed: {e}")
            return [data]

    def get_available_strategies(self) -> List[str]:
        """Get list of available mutation strategies"""
        strategies = [
            'bit_flip_1', 'bit_flip_2', 'bit_flip_4',
            'byte_flip', 'byte_random',
            'arithmetic_inc', 'arithmetic_dec',
            'interesting_8bit', 'interesting_16bit', 'interesting_32bit',
            'block_delete', 'block_duplicate', 'block_swap', 'block_insert',
            'dictionary_replace', 'dictionary_insert',
            'sql_injection', 'xss_injection', 'path_traversal',
            'buffer_overflow_patterns', 'format_string_patterns',
            'havoc'
        ]
        return strategies


# ==============================================================================
# TESTING
# ==============================================================================

def test_mutations():
    """Test mutation engine"""
    logging.basicConfig(level=logging.INFO)

    engine = AdvancedMutationEngine(protocol="http")

    test_data = b"GET /api/users?id=123 HTTP/1.1\r\nHost: example.com\r\n\r\n"

    print(f"Original: {test_data[:50]}")
    print(f"\nAvailable strategies: {len(engine.get_available_strategies())}")

    # Test each strategy
    for strategy in ['bit_flip_1', 'byte_flip', 'xss_injection', 'havoc']:
        mutations = engine.mutate(test_data, strategy=strategy, count=3)
        print(f"\n{strategy}:")
        for i, mut in enumerate(mutations[:3], 1):
            print(f"  {i}. {mut[:50]}")


if __name__ == "__main__":
    test_mutations()
