from suitescript_auditor.core.parsing.line_map import LineMap


def test_line_map_offset_to_range():
    content = "first\nsecond\nthird"
    line_map = LineMap.from_text(content)
    line_range = line_map.to_range(0, 10)
    assert line_range.start == 1
    assert line_range.end == 2
    numbered = line_map.numbered_text(1, 2)
    assert numbered[0].startswith("0001|")
    assert line_map.loc == 3
