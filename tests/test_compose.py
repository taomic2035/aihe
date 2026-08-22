def test_compose_has_required_services():
    import yaml
    data = yaml.safe_load(open("docker-compose.yml"))
    for svc in ["postgres", "redis", "qdrant", "letta", "backend", "gateway"]:
        assert svc in data["services"], f"missing service {svc}"


def test_compose_backend_depends_on_infra():
    import yaml
    data = yaml.safe_load(open("docker-compose.yml"))
    backend = data["services"]["backend"]
    depends = backend.get("depends_on", {})
    # depends_on may be dict or list
    if isinstance(depends, dict):
        deps = set(depends.keys())
    else:
        deps = set(depends)
    for dep in ["postgres", "redis", "qdrant"]:
        assert dep in deps, f"backend should depend on {dep}"


def test_env_example_has_required_keys():
    content = open(".env.example").read()
    for key in ["OPENROUTER_API_KEY", "QDRANT_URL", "LETTA_URL", "REDIS_URL"]:
        assert key in content, f"missing env key {key}"
