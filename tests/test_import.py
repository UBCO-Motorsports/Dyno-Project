def test_package_imports():
    import dyno

    assert "dynamometer" in dyno.__doc__
