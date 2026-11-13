"""Shared fixtures.

Code-switch routing has two classifiers — the char-Markov detector in
:mod:`tugaphone.langdetect` and the orthographic fallback in
:mod:`tugaphone.codeswitch` — and which one runs depends on whether the optional
``markovonnx`` dependency is installed. A routing invariant has to hold under
both, so tests asserting one take the ``classifier`` fixture and run twice.
"""
import pytest


@pytest.fixture(params=["detector", "fallback"])
def classifier(request, monkeypatch):
    """Run the test once per code-switch classifier.

    ``get_detector`` is ``lru_cache``d, so the cache is cleared around the
    monkeypatch; otherwise a detector loaded by an earlier test survives it.
    """
    import tugaphone.langdetect as langdetect

    get_detector = langdetect.get_detector
    get_detector.cache_clear()
    if request.param == "fallback":
        monkeypatch.setattr(langdetect, "get_detector", lambda: None)
    elif get_detector() is None:
        pytest.skip("markovonnx or bundled langdetect models unavailable")
    yield request.param
    get_detector.cache_clear()
