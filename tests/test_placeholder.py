def test_package_smoke_import_and_version():
    import amanogawa

    assert isinstance(amanogawa.__version__, str)
    assert len(amanogawa.__version__.split(".")) >= 2
