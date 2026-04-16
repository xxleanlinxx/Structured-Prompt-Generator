import unittest

from utils import (
    generate_prompt,
    get_default_form_data,
    get_prompt_health_report,
    normalize_actions,
    normalize_form_data,
)


class PromptUtilsTest(unittest.TestCase):
    def test_default_form_contains_single_empty_action(self):
        default_form = get_default_form_data()
        self.assertEqual(default_form["action"], [{"type": "Search", "value": ""}])

    def test_normalize_actions_from_multiline_string(self):
        actions = normalize_actions("first step\n\nsecond step")
        self.assertEqual(
            actions,
            [
                {"type": "Search", "value": "first step"},
                {"type": "Search", "value": "second step"},
            ],
        )

    def test_generate_prompt_en_uses_placeholders_when_empty(self):
        prompt = generate_prompt(get_default_form_data(), lang="en")
        self.assertIn('{domain}', prompt)
        self.assertIn('[Search("{action}")]', prompt)
        self.assertIn('{unwanted result}', prompt)

    def test_generate_prompt_zh_translates_action_type(self):
        data = get_default_form_data()
        data["action"] = [{"type": "Browse", "value": "https://example.com"}]
        prompt = generate_prompt(data, lang="zh")
        self.assertIn('[瀏覽("https://example.com")]', prompt)

    def test_health_report_warns_on_invalid_browse_url(self):
        data = get_default_form_data()
        data["domain"] = "marketing"
        data["specificGoal"] = "build a plan"
        data["format"] = "markdown"
        data["action"] = [{"type": "Browse", "value": "not-a-url"}]
        report = get_prompt_health_report(data, lang="en")
        self.assertTrue(report["warnings"])

    def test_normalize_form_data_handles_missing_action(self):
        normalized = normalize_form_data({"domain": "ml", "action": None})
        self.assertEqual(normalized["domain"], "ml")
        self.assertEqual(normalized["action"], [{"type": "Search", "value": ""}])


if __name__ == "__main__":
    unittest.main()
