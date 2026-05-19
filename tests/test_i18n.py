from tts_tool.i18n import (
    SUPPORTED_LOCALES,
    get_locale,
    set_locale,
    t,
    _STRINGS_DB,
)


class TestI18nBasic:
    def test_default_locale_is_zh(self):
        assert get_locale() == "zh"

    def test_t_returns_chinese_by_default(self):
        result = t("app.title")
        assert "TTS" in result
        assert "工具" in result

    def test_t_returns_key_for_missing(self):
        assert t("nonexistent.key") == "nonexistent.key"

    def test_t_with_kwargs(self):
        result = t("status.error", error="boom")
        assert "boom" in result
        assert "错误" in result

    def test_set_locale_to_en(self):
        original = get_locale()
        set_locale("en")
        assert get_locale() == "en"
        assert "TTS Tool" in t("app.title")
        set_locale(original)

    def test_set_locale_to_zh(self):
        set_locale("zh")
        assert get_locale() == "zh"
        assert "TTS" in t("app.title")

    def test_set_locale_unknown_gives_empty(self):
        set_locale("xx")
        assert t("app.title") == "app.title"
        set_locale("zh")

    def test_set_locale_roundtrip(self):
        set_locale("en")
        assert "Play" in t("player.play")
        set_locale("zh")
        assert "播放" in t("player.play")


class TestI18nCompleteness:
    def test_zh_and_en_have_same_keys(self):
        zh_keys = set(_STRINGS_DB["zh"].keys())
        en_keys = set(_STRINGS_DB["en"].keys())
        assert zh_keys == en_keys, f"Missing in en: {zh_keys - en_keys}, Missing in zh: {en_keys - zh_keys}"

    def test_all_speed_preset_keys_exist(self):
        for preset in ("settings.slower", "settings.slow", "settings.normal", "settings.fast", "settings.faster"):
            assert preset in _STRINGS_DB["zh"], f"Missing zh key: {preset}"
            assert preset in _STRINGS_DB["en"], f"Missing en key: {preset}"
            assert len(_STRINGS_DB["zh"][preset]) > 0
            assert len(_STRINGS_DB["en"][preset]) > 0

    def test_no_empty_values(self):
        for locale_code, strings in _STRINGS_DB.items():
            for key, value in strings.items():
                assert len(value) > 0, f"Empty value for {key} in {locale_code}"

    def test_supported_locales_have_db_entries(self):
        for loc in SUPPORTED_LOCALES:
            assert loc.code in _STRINGS_DB, f"Missing DB for locale: {loc.code}"

    def test_all_keys_non_empty_strings(self):
        for locale_code, strings in _STRINGS_DB.items():
            for key, value in strings.items():
                assert isinstance(value, str), f"{key} in {locale_code} is not str"
                assert len(value.strip()) > 0, f"{key} in {locale_code} is empty"


class TestI18nPlaceholders:
    def test_status_generating_has_placeholders(self):
        set_locale("zh")
        result = t("status.generating", current=1, total=5)
        assert "1" in result
        assert "5" in result

    def test_status_complete_has_duration(self):
        set_locale("zh")
        result = t("status.complete", duration="01:30")
        assert "01:30" in result

    def test_status_error_has_error(self):
        set_locale("en")
        result = t("status.error", error="timeout")
        assert "timeout" in result
        set_locale("zh")
