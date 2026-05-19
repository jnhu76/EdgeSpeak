from hypothesis import given, settings
from hypothesis import strategies as st

from tts_tool.i18n import (
    SUPPORTED_LOCALES,
    get_locale,
    set_locale,
    t,
    _STRINGS_DB,
)


class TestI18nProperty:
    @given(
        locale_code=st.sampled_from([loc.code for loc in SUPPORTED_LOCALES]),
        key=st.sampled_from(list(_STRINGS_DB["zh"].keys())),
    )
    @settings(max_examples=100)
    def test_t_never_returns_raw_key_for_valid_inputs(self, locale_code: str, key: str) -> None:
        original = get_locale()
        set_locale(locale_code)
        result = t(key)
        assert result != key or key not in _STRINGS_DB[locale_code]
        set_locale(original)

    @given(key=st.text(min_size=1, max_size=50))
    @settings(max_examples=200)
    def test_t_always_returns_string(self, key: str) -> None:
        result = t(key)
        assert isinstance(result, str)

    @given(
        key=st.sampled_from(list(_STRINGS_DB["zh"].keys())),
        kwargs=st.dictionaries(
            st.text(min_size=1, max_size=10, alphabet=st.characters(whitelist_categories=("Ll",))),
            st.text(min_size=1, max_size=20),
            max_size=3,
        ),
    )
    @settings(max_examples=100)
    def test_t_with_kwargs_never_crashes(self, key: str, kwargs: dict) -> None:
        try:
            t(key, **kwargs)
        except (KeyError, IndexError):
            pass

    @given(text=st.text(min_size=0, max_size=200))
    @settings(max_examples=100)
    def test_locale_switch_never_crashes(self, text: str) -> None:
        original = get_locale()
        for loc in SUPPORTED_LOCALES:
            set_locale(loc.code)
            t("app.title")
        set_locale(original)

    @given(
        duration=st.text(min_size=1, max_size=10),
        current=st.integers(min_value=0, max_value=999),
        total=st.integers(min_value=1, max_value=999),
        error=st.text(min_size=1, max_size=50),
    )
    @settings(max_examples=100)
    def test_template_placeholders_accept_varied_input(
        self, duration: str, current: int, total: int, error: str
    ) -> None:
        original = get_locale()
        for loc in SUPPORTED_LOCALES:
            set_locale(loc.code)
            r1 = t("status.complete", duration=duration)
            assert duration in r1
            r2 = t("status.generating", current=current, total=total)
            assert str(current) in r2
            assert str(total) in r2
            r3 = t("status.error", error=error)
            assert error in r3
        set_locale(original)


class TestI18nStress:
    def test_rapid_locale_switching(self) -> None:
        original = get_locale()
        for _ in range(500):
            set_locale("en")
            assert "TTS" in t("app.title")
            set_locale("zh")
            assert "TTS" in t("app.title")
        set_locale(original)

    def test_all_keys_accessible_in_all_locales(self) -> None:
        original = get_locale()
        all_keys = set(_STRINGS_DB["zh"].keys()) | set(_STRINGS_DB["en"].keys())
        for loc in SUPPORTED_LOCALES:
            set_locale(loc.code)
            for key in all_keys:
                result = t(key)
                assert isinstance(result, str)
                assert len(result) > 0
        set_locale(original)
