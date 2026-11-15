import unittest

from calculator.history import History


class HistoryTest(unittest.TestCase):
    def test_newest_first(self):
        h = History()
        h.add("1+1", "2")
        h.add("2×3", "6")
        self.assertEqual([str(e) for e in h.entries], ["2×3 = 6", "1+1 = 2"])

    def test_max_size(self):
        h = History(max_size=3)
        for i in range(5):
            h.add(f"{i}+0", str(i))
        self.assertEqual(len(h), 3)
        self.assertEqual(h.entries[0].result, "4")
        self.assertEqual(h.entries[-1].result, "2")

    def test_clear(self):
        h = History()
        h.add("1+1", "2")
        h.clear()
        self.assertEqual(len(h), 0)

    def test_entries_is_copy(self):
        h = History()
        h.add("1+1", "2")
        h.entries.clear()
        self.assertEqual(len(h), 1)


if __name__ == "__main__":
    unittest.main()
