from unittest import TestCase, main

from restcli import extract_body_part, parse_body_part


class ParseBodyTests(TestCase):

    def test_one(self):
        self.assertEqual(list(parse_body_part('a')), ['a'])

    def test_many(self):
        self.assertEqual(list(parse_body_part('a.b[2].c')), ['a', 'b', 2, 'c'])

    def test_arr_beg(self):
        self.assertEqual(list(parse_body_part('[2].c')), [2, 'c'])

    def test_arr_beg_end(self):
        self.assertEqual(list(parse_body_part('[2].c[3]')), [2, 'c', 3])

    def test_arr_twice(self):
        self.assertEqual(list(parse_body_part('[2].c[3][4]')), [2, 'c', 3, 4])


class ExtractBodyTests(TestCase):

    def setUp(self):
        self.d = {'a': {'b': [2, 3, {'c': 'c2'}]}}

    def test_1(self):
        body, part = extract_body_part(self.d, 'a')
        self.assertEqual(body, self.d)
        self.assertEqual(part, 'a')

    def test_2(self):
        body, part = extract_body_part(self.d, 'a.b')
        self.assertEqual(body, self.d['a'])
        self.assertEqual(part, 'b')

    def test_arr(self):
        body, part = extract_body_part(self.d, 'a.b[2]')
        self.assertEqual(body, self.d['a']['b'])
        self.assertEqual(part, 2)


if __name__ == '__main__':
    main()
