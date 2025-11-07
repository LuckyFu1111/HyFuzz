#!/usr/bin/env python3
"""
Protocol validation tool for HyFuzz.

This tool validates protocol implementations to ensure they meet
the required interface and follow best practices.
"""

import argparse
import importlib.util
import inspect
import sys
from pathlib import Path
from typing import List, Tuple


def load_protocol_module(file_path: Path):
    """Load a protocol module from a file path."""
    spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    return None


def validate_server_protocol(handler_cls) -> Tuple[bool, List[str]]:
    """
    Validate a server-side protocol handler.

    Args:
        handler_cls: Protocol handler class to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check class attributes
    if not hasattr(handler_cls, "name"):
        issues.append("Missing 'name' class attribute")
    elif not isinstance(handler_cls.name, str):
        issues.append("'name' attribute must be a string")

    if not hasattr(handler_cls, "SPEC"):
        issues.append("Missing 'SPEC' class attribute (ProtocolMetadata)")

    # Check required methods
    required_methods = {
        "prepare_request": ["context", "payload"],
        "parse_response": ["context", "response"],
        "validate": ["payload"],
        "get_spec": [],
    }

    for method_name, params in required_methods.items():
        if not hasattr(handler_cls, method_name):
            issues.append(f"Missing required method: {method_name}()")
        else:
            method = getattr(handler_cls, method_name)
            if not callable(method):
                issues.append(f"'{method_name}' is not callable")
            else:
                # Check method signature
                sig = inspect.signature(method)
                method_params = list(sig.parameters.keys())
                # Remove 'self' from instance methods
                if "self" in method_params:
                    method_params.remove("self")

                for param in params:
                    if param not in method_params:
                        issues.append(
                            f"Method '{method_name}' missing parameter: {param}"
                        )

    # Try to instantiate
    try:
        instance = handler_cls()

        # Test get_spec
        try:
            spec = instance.get_spec()
            if not hasattr(spec, "name"):
                issues.append("get_spec() must return an object with 'name' attribute")
            if not hasattr(spec, "version"):
                issues.append("get_spec() must return an object with 'version' attribute")
        except Exception as e:
            issues.append(f"get_spec() failed: {e}")

    except Exception as e:
        issues.append(f"Failed to instantiate handler: {e}")

    return len(issues) == 0, issues


def validate_client_handler(handler_cls) -> Tuple[bool, List[str]]:
    """
    Validate a client-side protocol handler.

    Args:
        handler_cls: Protocol handler class to validate

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check class attributes
    if not hasattr(handler_cls, "name"):
        issues.append("Missing 'name' class attribute")
    elif not isinstance(handler_cls.name, str):
        issues.append("'name' attribute must be a string")

    if not hasattr(handler_cls, "capabilities"):
        issues.append("Missing 'capabilities' class attribute (ProtocolMetadata)")

    # Check required methods
    if not hasattr(handler_cls, "execute"):
        issues.append("Missing required method: execute()")
    else:
        method = getattr(handler_cls, "execute")
        if not callable(method):
            issues.append("'execute' is not callable")
        else:
            sig = inspect.signature(method)
            params = list(sig.parameters.keys())
            if "self" in params:
                params.remove("self")
            if "request" not in params:
                issues.append("execute() must have 'request' parameter")

    if not hasattr(handler_cls, "get_capabilities"):
        issues.append("Missing method: get_capabilities()")

    # Try to instantiate
    try:
        instance = handler_cls()

        # Test get_capabilities
        try:
            caps = instance.get_capabilities()
            if not hasattr(caps, "name"):
                issues.append(
                    "get_capabilities() must return an object with 'name' attribute"
                )
            if not hasattr(caps, "version"):
                issues.append(
                    "get_capabilities() must return an object with 'version' attribute"
                )
        except Exception as e:
            issues.append(f"get_capabilities() failed: {e}")

    except Exception as e:
        issues.append(f"Failed to instantiate handler: {e}")

    return len(issues) == 0, issues


def validate_protocol_file(file_path: Path, protocol_type: str) -> bool:
    """
    Validate a protocol file.

    Args:
        file_path: Path to the protocol file
        protocol_type: Type of protocol (server or client)

    Returns:
        True if validation passed
    """
    print(f"\n{'=' * 70}")
    print(f"Validating {protocol_type} protocol: {file_path.name}")
    print(f"{'=' * 70}\n")

    # Load the module
    try:
        module = load_protocol_module(file_path)
        if module is None:
            print("❌ Failed to load module")
            return False
    except Exception as e:
        print(f"❌ Failed to load module: {e}")
        return False

    # Find handler classes
    handlers_found = []
    for name, obj in inspect.getmembers(module):
        if inspect.isclass(obj) and obj.__module__ == module.__name__:
            # Check if it's a protocol handler
            if hasattr(obj, "name") and hasattr(obj, "execute" if protocol_type == "client" else "prepare_request"):
                handlers_found.append((name, obj))

    if not handlers_found:
        print("❌ No protocol handler classes found in module")
        return False

    print(f"Found {len(handlers_found)} handler class(es):\n")

    all_valid = True
    for class_name, handler_cls in handlers_found:
        print(f"Validating class: {class_name}")
        print(f"  Protocol name: {getattr(handler_cls, 'name', 'N/A')}")

        # Validate based on type
        if protocol_type == "server":
            is_valid, issues = validate_server_protocol(handler_cls)
        else:
            is_valid, issues = validate_client_handler(handler_cls)

        if is_valid:
            print("  ✅ Valid protocol handler")

            # Get metadata
            try:
                instance = handler_cls()
                if protocol_type == "server":
                    metadata = instance.get_spec()
                else:
                    metadata = instance.get_capabilities()

                print(f"  Version: {metadata.version}")
                print(f"  Description: {metadata.description}")
                print(f"  Stateful: {metadata.stateful}")

            except Exception as e:
                print(f"  ⚠️  Could not extract metadata: {e}")

        else:
            print("  ❌ Invalid protocol handler")
            for issue in issues:
                print(f"     - {issue}")
            all_valid = False

        print()

    return all_valid


def check_compatibility(server_file: Path, client_file: Path) -> bool:
    """
    Check compatibility between server and client protocol implementations.

    Args:
        server_file: Path to server protocol file
        client_file: Path to client handler file

    Returns:
        True if compatible
    """
    print(f"\n{'=' * 70}")
    print("Checking compatibility")
    print(f"{'=' * 70}\n")

    try:
        # Load both modules
        server_module = load_protocol_module(server_file)
        client_module = load_protocol_module(client_file)

        if not server_module or not client_module:
            print("❌ Failed to load modules")
            return False

        # Find handlers
        server_handler = None
        client_handler = None

        for name, obj in inspect.getmembers(server_module):
            if inspect.isclass(obj) and hasattr(obj, "prepare_request"):
                server_handler = obj
                break

        for name, obj in inspect.getmembers(client_module):
            if inspect.isclass(obj) and hasattr(obj, "execute"):
                client_handler = obj
                break

        if not server_handler or not client_handler:
            print("❌ Could not find handler classes")
            return False

        # Check protocol names match
        server_name = getattr(server_handler, "name", None)
        client_name = getattr(client_handler, "name", None)

        if server_name != client_name:
            print("❌ Protocol name mismatch:")
            print(f"   Server: {server_name}")
            print(f"   Client: {client_name}")
            return False

        print(f"✅ Protocol names match: {server_name}")

        # Get metadata
        server_instance = server_handler()
        client_instance = client_handler()

        server_metadata = server_instance.get_spec()
        client_metadata = client_instance.get_capabilities()

        # Check version compatibility
        print("\nVersion information:")
        print(f"  Server handler: {server_metadata.version}")
        print(f"  Client handler: {client_metadata.version}")

        # Check stateful flag matches
        if server_metadata.stateful != client_metadata.stateful:
            print("⚠️  Stateful flag mismatch:")
            print(f"   Server: {server_metadata.stateful}")
            print(f"   Client: {client_metadata.stateful}")
            return False

        print(f"✅ Stateful flag matches: {server_metadata.stateful}")

        # Check default parameters
        server_params = set(server_metadata.default_parameters.keys())
        client_params = set(client_metadata.default_parameters.keys())

        if server_params != client_params:
            print("⚠️  Default parameters differ:")
            print(f"   Server only: {server_params - client_params}")
            print(f"   Client only: {client_params - server_params}")
        else:
            print("✅ Default parameters match")

        print("\n✅ Protocols are compatible")
        return True

    except Exception as e:
        print(f"❌ Compatibility check failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Validate HyFuzz protocol implementations"
    )
    parser.add_argument(
        "files", nargs="+", type=Path, help="Protocol files to validate"
    )
    parser.add_argument(
        "--type",
        choices=["server", "client", "auto"],
        default="auto",
        help="Type of protocol to validate",
    )
    parser.add_argument(
        "--check-compatibility",
        action="store_true",
        help="Check compatibility between server and client (requires 2 files)",
    )

    args = parser.parse_args()

    if args.check_compatibility:
        if len(args.files) != 2:
            print("❌ Compatibility check requires exactly 2 files (server and client)")
            return 1

        server_file, client_file = args.files
        success = check_compatibility(server_file, client_file)
        return 0 if success else 1

    # Validate each file
    all_valid = True
    for file_path in args.files:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            all_valid = False
            continue

        # Auto-detect type
        protocol_type = args.type
        if protocol_type == "auto":
            if "_protocol.py" in file_path.name:
                protocol_type = "server"
            elif "_handler.py" in file_path.name:
                protocol_type = "client"
            else:
                print(
                    f"❌ Cannot auto-detect protocol type for {file_path.name}. "
                    f"Use --type to specify."
                )
                all_valid = False
                continue

        if not validate_protocol_file(file_path, protocol_type):
            all_valid = False

    if all_valid:
        print(f"\n{'=' * 70}")
        print("✅ All protocols validated successfully")
        print(f"{'=' * 70}\n")
        return 0
    else:
        print(f"\n{'=' * 70}")
        print("❌ Some protocols failed validation")
        print(f"{'=' * 70}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
