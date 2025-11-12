"""
Unit tests for SafeSerializer module

Tests the secure JSON-based serialization that replaces pickle
to prevent RCE vulnerabilities.
"""

import pytest
import tempfile
import datetime
import gzip
from pathlib import Path
from decimal import Decimal
from dataclasses import dataclass

from src.utils.safe_serializer import SafeSerializer, SerializationError


@dataclass
class TestDataClass:
    """Test dataclass for serialization"""
    name: str
    value: int
    timestamp: datetime.datetime


class TestSafeSerializerBasic:
    """Test basic serialization functionality"""

    def test_serialize_deserialize_primitives(self):
        """Test serialization of primitive types"""
        serializer = SafeSerializer()

        test_data = {
            'string': 'Hello, World!',
            'integer': 42,
            'float': 3.14,
            'boolean': True,
            'none': None,
        }

        # Serialize
        serialized = serializer.dumps(test_data)
        assert isinstance(serialized, bytes)

        # Deserialize
        deserialized = serializer.loads(serialized)
        assert deserialized == test_data

    def test_serialize_deserialize_collections(self):
        """Test serialization of collections"""
        serializer = SafeSerializer()

        test_data = {
            'list': [1, 2, 3, 4, 5],
            'tuple': (1, 2, 3),  # Will become list
            'dict': {'nested': 'value'},
            'set': {1, 2, 3},  # Will become list
        }

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Lists and dicts should match exactly
        assert deserialized['list'] == test_data['list']
        assert deserialized['dict'] == test_data['dict']

        # Tuples become lists
        assert deserialized['tuple'] == list(test_data['tuple'])

        # Sets become lists (order may differ)
        assert set(deserialized['set']) == test_data['set']

    def test_serialize_datetime(self):
        """Test serialization of datetime objects"""
        serializer = SafeSerializer()

        now = datetime.datetime.now()
        test_data = {'timestamp': now}

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Should deserialize to datetime object
        assert isinstance(deserialized['timestamp'], datetime.datetime)
        # Microseconds might differ slightly, check within 1 second
        assert abs((deserialized['timestamp'] - now).total_seconds()) < 1

    def test_serialize_path(self):
        """Test serialization of Path objects"""
        serializer = SafeSerializer()

        test_path = Path('/tmp/test/file.txt')
        test_data = {'path': test_path}

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Should deserialize to Path object
        assert isinstance(deserialized['path'], Path)
        assert deserialized['path'] == test_path

    def test_serialize_nested_structures(self):
        """Test deeply nested data structures"""
        serializer = SafeSerializer()

        test_data = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': [1, 2, {'level5': 'deep'}]
                    }
                }
            }
        }

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        assert deserialized == test_data


class TestSafeSerializerCompression:
    """Test compression functionality"""

    def test_compression_enabled(self):
        """Test that compression reduces size"""
        serializer_no_comp = SafeSerializer(use_compression=False)
        serializer_comp = SafeSerializer(use_compression=True)

        # Large repetitive data compresses well
        test_data = {'data': 'A' * 10000}

        uncompressed = serializer_no_comp.dumps(test_data)
        compressed = serializer_comp.dumps(test_data)

        # Compressed should be smaller
        assert len(compressed) < len(uncompressed)

        # Both should deserialize correctly
        assert serializer_no_comp.loads(uncompressed) == test_data
        assert serializer_comp.loads(compressed) == test_data

    def test_decompress_uncompressed_data_fails(self):
        """Test that decompressing uncompressed data fails gracefully"""
        serializer_comp = SafeSerializer(use_compression=True)
        serializer_no_comp = SafeSerializer(use_compression=False)

        test_data = {'test': 'value'}
        uncompressed = serializer_no_comp.dumps(test_data)

        # Trying to decompress uncompressed data should raise error
        with pytest.raises(SerializationError):
            serializer_comp.loads(uncompressed)


class TestSafeSerializerFiles:
    """Test file-based serialization"""

    def test_dump_load_file(self):
        """Test dumping and loading from file"""
        serializer = SafeSerializer()
        test_data = {'file_test': 'data', 'number': 123}

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json') as f:
            temp_path = f.name
            serializer.dump(test_data, f)

        try:
            with open(temp_path, 'rb') as f:
                loaded_data = serializer.load(f)

            assert loaded_data == test_data
        finally:
            Path(temp_path).unlink()

    def test_dump_load_file_with_compression(self):
        """Test file serialization with compression"""
        serializer = SafeSerializer(use_compression=True)
        test_data = {'compressed': 'file', 'data': 'A' * 1000}

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.json.gz') as f:
            temp_path = f.name
            serializer.dump(test_data, f)

        try:
            with open(temp_path, 'rb') as f:
                loaded_data = serializer.load(f)

            assert loaded_data == test_data
        finally:
            Path(temp_path).unlink()


class TestSafeSerializerDataClass:
    """Test dataclass serialization"""

    def test_serialize_dataclass(self):
        """Test serialization of dataclass objects"""
        serializer = SafeSerializer()

        test_obj = TestDataClass(
            name='test',
            value=42,
            timestamp=datetime.datetime.now()
        )

        test_data = {'object': test_obj}

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Dataclass becomes dict
        assert isinstance(deserialized['object'], dict)
        assert deserialized['object']['name'] == 'test'
        assert deserialized['object']['value'] == 42


class TestSafeSerializerEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_data(self):
        """Test serialization of empty structures"""
        serializer = SafeSerializer()

        test_cases = [
            {},
            [],
            '',
        ]

        for test_data in test_cases:
            serialized = serializer.dumps(test_data)
            deserialized = serializer.loads(serialized)
            assert deserialized == test_data

    def test_unicode_data(self):
        """Test serialization of unicode strings"""
        serializer = SafeSerializer()

        test_data = {
            'chinese': '你好世界',
            'emoji': '🎉🔒✅',
            'mixed': 'Hello 世界 🌍',
        }

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        assert deserialized == test_data

    def test_large_data(self):
        """Test serialization of large data structures"""
        serializer = SafeSerializer()

        # Create large list
        large_list = list(range(100000))
        test_data = {'large': large_list}

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        assert deserialized == test_data

    def test_invalid_json_raises_error(self):
        """Test that invalid data raises SerializationError"""
        serializer = SafeSerializer()

        invalid_data = b'this is not json'

        with pytest.raises(SerializationError):
            serializer.loads(invalid_data)

    def test_circular_reference_handling(self):
        """Test handling of circular references"""
        serializer = SafeSerializer()

        # Create circular reference
        data = {'list': []}
        data['list'].append(data)  # Circular reference

        # Should raise error or handle gracefully
        with pytest.raises((SerializationError, ValueError, TypeError)):
            serializer.dumps(data)


class TestSafeSerializerDecimal:
    """Test Decimal serialization"""

    def test_serialize_decimal(self):
        """Test serialization of Decimal objects"""
        serializer = SafeSerializer()

        test_data = {
            'price': Decimal('19.99'),
            'tax': Decimal('0.15'),
        }

        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Decimals should be preserved or converted to float
        assert 'price' in deserialized
        assert 'tax' in deserialized


class TestSafeSerializerSecurity:
    """Test security features"""

    def test_no_code_execution(self):
        """Test that malicious data doesn't execute code"""
        serializer = SafeSerializer()

        # Try to inject code (should be treated as strings)
        malicious_data = {
            'code': '__import__("os").system("echo hacked")',
            'eval': 'eval("1+1")',
        }

        serialized = serializer.dumps(malicious_data)
        deserialized = serializer.loads(serialized)

        # Should deserialize as strings, not execute
        assert deserialized['code'] == malicious_data['code']
        assert deserialized['eval'] == malicious_data['eval']

    def test_cannot_deserialize_arbitrary_objects(self):
        """Test that arbitrary objects cannot be deserialized"""
        serializer = SafeSerializer()

        # JSON cannot represent arbitrary Python objects
        # This ensures safety compared to pickle
        class CustomClass:
            def __init__(self):
                self.value = "unsafe"

        test_data = {'obj': CustomClass()}

        # Should serialize (converts to dict)
        serialized = serializer.dumps(test_data)
        deserialized = serializer.loads(serialized)

        # Should not be CustomClass instance
        assert not isinstance(deserialized['obj'], CustomClass)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
