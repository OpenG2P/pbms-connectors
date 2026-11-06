"""Guard: every register is configurable end to end, and connection strings decode.

A register is a G2PRegistryType value. Each one needs:
  * the same value in the Odoo copy of the enum (g2p_registry_type_addon)
  * an entry in the adapters' registers.py
  * global.registers.<register>.connector / .connectionString in values.yaml
  * REGISTRY_ADAPTERS_<REGISTER>_CONNECTOR / _CONNECTION_STRING in the
    registryAdapterEnv anchor, used by the Celery worker and the staff API
  * a connector and connectionString question in questions.own.yaml

Python sources are read with ast, not imported, so CI needs only pytest and
pyyaml. connection.py is standard library only and is imported by path.
"""

import ast
import importlib.util
import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parent.parent
ADAPTERS = (
    REPO
    / "extensions"
    / "registry-adapters"
    / "src"
    / "openg2p_bg_task_registry_adapters"
)
ODOO_ENUM = REPO / "odoo" / "g2p_registry_type_addon" / "models" / "registry_type.py"
CHART = REPO / "helm" / "openg2p-pbms"
ENV_CONSUMERS = ("celeryWorkers", "staffPortalApi")


def _enum(path: pathlib.Path) -> dict[str, str]:
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.ClassDef) and node.name == "G2PRegistryType":
            return {
                stmt.targets[0].id: stmt.value.value
                for stmt in node.body
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant)
            }
    raise AssertionError(f"no G2PRegistryType in {path}")


def _registers_entries(members: dict[str, str]) -> set[str]:
    tree = ast.parse((ADAPTERS / "registers.py").read_text())
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "REGISTERS"
        ):
            # Keys look like G2PRegistryType.FARMER.value
            return {members[key.value.attr] for key in node.value.keys}
    raise AssertionError("no REGISTERS in registers.py")


def _registers() -> list[str]:
    return sorted(_enum(ADAPTERS / "models" / "enum.py").values())


@pytest.fixture(scope="module")
def values():
    return yaml.safe_load((CHART / "values.yaml").read_text())


@pytest.fixture(scope="module")
def questions():
    return {
        q["variable"]
        for q in yaml.safe_load((CHART / "questions.own.yaml").read_text())
    }


def test_enum_copies_match():
    assert _registers() == sorted(_enum(ODOO_ENUM).values())


def test_registers_py_covers_every_register():
    members = _enum(ADAPTERS / "models" / "enum.py")
    assert _registers_entries(members) == set(_registers())


@pytest.mark.parametrize("register", _registers())
def test_values_block(values, register):
    block = values["global"]["registers"].get(register)
    assert block is not None, f"values.yaml: global.registers.{register} missing"
    assert {"connector", "connectionString"} <= set(block)


@pytest.mark.parametrize("register", _registers())
def test_env(values, register):
    names = {
        f"REGISTRY_ADAPTERS_{register.upper()}_CONNECTOR",
        f"REGISTRY_ADAPTERS_{register.upper()}_CONNECTION_STRING",
    }
    for consumer in ENV_CONSUMERS:
        env = values["pbms"][consumer]["envVars"]
        assert names <= set(env), f"pbms.{consumer}.envVars misses {names - set(env)}"


@pytest.mark.parametrize("register", _registers())
def test_questions_block(questions, register):
    wanted = {
        f"global.registers.{register}.connector",
        f"global.registers.{register}.connectionString",
    }
    assert wanted <= questions, f"questions.own.yaml misses {wanted - questions}"


# Decoder


def _connection_module():
    spec = importlib.util.spec_from_file_location(
        "registry_connection", ADAPTERS / "connection.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


connection = _connection_module()
parse = connection.RegistryConnection.parse


def test_db_with_encoded_password():
    conn = parse(
        "farmer", "db", "postgresql://registry_user:p%40ss%3Aw0rd@pg.svc:5433/registry"
    )
    assert conn.connector == "db"
    assert conn.db_username == "registry_user"
    assert conn.db_password == "p@ss:w0rd"
    assert (conn.db_hostname, conn.db_port, conn.db_dbname) == (
        "pg.svc",
        5433,
        "registry",
    )
    assert (
        conn.sync_url()
        == "postgresql://registry_user:p%40ss%3Aw0rd@pg.svc:5433/registry"
    )
    assert conn.async_url().startswith("postgresql+asyncpg://")
    assert "p@ss" not in repr(conn)


def test_db_default_port():
    assert parse("farmer", "db", "postgresql://u:p@pg/registry").db_port == 5432


def test_dci_url_without_params_uses_register_defaults():
    conn = parse(
        "disability",
        "DCI",
        "http://disability-registry-partner-api/dci/registry/sync/search/",
        "PersonWithDisability",
        "spdci-extensions-dci:PersonwithDisability",
    )
    assert conn.connector == "dci"
    assert conn.search_url == "http://disability-registry-partner-api/dci/registry/sync/search"
    assert conn.partner_api_timeout == 30
    assert conn.partner_api_ssl_verify is True
    assert conn.reg_type == "PersonWithDisability"
    assert conn.reg_record_type == "spdci-extensions-dci:PersonwithDisability"


def test_dci_query_params_override():
    conn = parse(
        "farmer",
        "dci",
        "https://gw.example.org/farmer/dci/registry/sync/search"
        "?reg_type=Farm&reg_record_type=FarmRec&timeout=5&ssl_verify=false",
        "Farmer",
        "Farmer",
    )
    assert conn.search_url == "https://gw.example.org/farmer/dci/registry/sync/search"
    assert (conn.reg_type, conn.reg_record_type) == ("Farm", "FarmRec")
    assert conn.partner_api_timeout == 5
    assert conn.partner_api_ssl_verify is False


@pytest.mark.parametrize(
    "connector, value",
    [
        ("odbc", "postgresql://u:p@pg/registry"),
        ("db", ""),
        ("db", "postgresql://u:p@pg/"),
        ("db", "not a url"),
        ("dci", "ftp://api/dci/registry/sync/search"),
        ("dci", "http://api"),
        ("dci", "http://api/?timeout=5"),
        ("dci", "http://api/dci/registry/sync/search?regtype=Farmer"),
        ("dci", "http://api/dci/registry/sync/search?timeout=zero"),
        ("dci", "http://api/dci/registry/sync/search?ssl_verify=maybe"),
    ],
)
def test_invalid(connector, value):
    with pytest.raises(connection.RegistryConnectionError):
        parse("farmer", connector, value)
