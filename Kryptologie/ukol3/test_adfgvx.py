"""Automaticke testy ADFGX (CZ/EN) a ADFGVX.

Umisteni: do stejne slozky jako adfgvx.py.
Spusteni: python -m unittest -v test_adfgvx.py

Testy vyzaduji verzi adfgvx.py s volitelnym parametrem jazyk='CZ'
u funkci vytvoreni_matice, filtrace_textu, ziskta_klic a obnov_znaky.
"""

import random
import string
import unittest

from adfgvx import (
    vytvoreni_matice,
    filtrace_textu,
    ziskta_klic,
    substituce_difuze,
    transpozice_difuze,
    inverze_transpozice_difuze,
    inverze_substituce_difuze,
    obnov_znaky,
)


VARIANTY = [(0, "CZ"), (0, "EN"), (1, "CZ")]


class TestADFGVX(unittest.TestCase):
    def over_cestu(self, velikost, jazyk, seed, zprava, klic_raw):
        matice = vytvoreni_matice(seed, velikost, jazyk)
        klic = ziskta_klic(klic_raw, velikost, jazyk)
        filtrovany = filtrace_textu(zprava, velikost, jazyk)
        self.assertTrue(klic, "Test musi pouzit platny neprazdny klic")

        substituce = substituce_difuze(matice, filtrovany, velikost)
        self.assertEqual(
            len(substituce), 2 * len(filtrovany),
            "Substituce ztratila znak - pravdepodobne chybi v matici",
        )

        sifrovany = transpozice_difuze(substituce, klic)
        po_inverzi_transpozice = inverze_transpozice_difuze(sifrovany, klic)
        self.assertEqual(po_inverzi_transpozice, substituce)

        po_inverzi_substituce = inverze_substituce_difuze(
            po_inverzi_transpozice, matice, velikost
        )
        self.assertEqual(po_inverzi_substituce, filtrovany)
        self.assertEqual(
            obnov_znaky(po_inverzi_substituce, velikost, jazyk),
            obnov_znaky(filtrovany, velikost, jazyk),
        )

    def test_01_matice_rozmery_a_abecedy(self):
        for velikost, jazyk in VARIANTY:
            for seed in (0, 10, 98765):
                with self.subTest(velikost=velikost, jazyk=jazyk, seed=seed):
                    m = vytvoreni_matice(seed, velikost, jazyk)
                    n = 5 if velikost == 0 else 6
                    abeceda = (
                        string.ascii_lowercase.replace("w" if jazyk == "CZ" else "j", "")
                        if velikost == 0 else string.ascii_lowercase + string.digits
                    )
                    self.assertEqual(len(m), n)
                    self.assertTrue(all(len(r) == n for r in m))
                    self.assertEqual(set(x for r in m for x in r), set(abeceda))
                    self.assertEqual(len([x for r in m for x in r]), len(abeceda))

    def test_02_seed_je_reprodukovatelny(self):
        for velikost, jazyk in VARIANTY:
            with self.subTest(velikost=velikost, jazyk=jazyk):
                self.assertEqual(
                    vytvoreni_matice(42, velikost, jazyk),
                    vytvoreni_matice(42, velikost, jazyk),
                )

    def test_03_cz_en_mapovani(self):
        self.assertEqual(filtrace_textu("WJ", 0, "CZ"), "vj")
        self.assertEqual(filtrace_textu("WJ", 0, "EN"), "wi")
        self.assertEqual(ziskta_klic("WJ", 0, "CZ"), "vj")
        self.assertEqual(ziskta_klic("WJ", 0, "EN"), "wi")
        self.assertEqual(filtrace_textu("1", 0, "CZ"), "xjednax")
        self.assertEqual(filtrace_textu("1", 0, "EN"), "xiednax")
        self.assertEqual(obnov_znaky("xiednax", 0, "EN"), "1")

    def test_04_cyklus_sifrovani_a_desifrovani(self):
        zpravy = (
            "AHOJ SVETE 123", "WJ 1", "TEST", "A", "Ahoj, svete! 0123456789",
            "123 456", "X", "ABCDEF", "KRYPTOLOGIE",
        )
        klice = ("TAJNE", "A", "KLIC", "AB", "DLOUHESLOVO123", "XYZ")
        for velikost, jazyk in VARIANTY:
            for seed in (0, 10, 987):
                for zprava in zpravy:
                    for klic in klice:
                        with self.subTest(velikost=velikost, jazyk=jazyk,
                                          seed=seed, zprava=zprava, klic=klic):
                            self.over_cestu(velikost, jazyk, seed, zprava, klic)

    def test_05_nahodne_pripady(self):
        rng = random.Random(20261023)
        abeceda = string.ascii_uppercase + string.digits + "  .!?"
        for velikost, jazyk in VARIANTY:
            for pokus in range(1000):
                zprava = "".join(rng.choices(abeceda, k=rng.randint(1, 80)))
                klic = "".join(rng.choices(string.ascii_uppercase, k=rng.randint(1, 20)))
                seed = rng.randint(0, 1000000)
                with self.subTest(velikost=velikost, jazyk=jazyk, pokus=pokus):
                    self.over_cestu(velikost, jazyk, seed, zprava, klic)

    def test_06_prazdny_klic(self):
        with self.assertRaises(ValueError):
            transpozice_difuze("ADFG", "")
        with self.assertRaises(ValueError):
            inverze_transpozice_difuze("ADFG", "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
