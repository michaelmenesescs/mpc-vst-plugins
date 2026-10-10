"""Every plugin's panel, by id. Each machine is drawn as the hardware it models (hwpanel.Page: controls at the
machine's own positions, with its panel artwork); the functions live in the m_*.py modules, grouped by maker:

    m_roland.py   303, 808, 909, 606, SH-101 (hush1), CR-78 (cw78)
    m_fx.py       RE-201 (tapedelay), Juno-60 chorus (juno), SSL E/G EQ (4keq), Midiverb
    m_euro.py     Braids, Plaits, MicroFreak (mrhyde), Serge (denis), M185 sequencer (ml185)
    m_misc.py     PO-32 (libpo32), Game Boy (chiptune), PlayStation reverb (psxverb), Drum Buss (busdriver), ducker,
                  SEM-style filter, cassette deck (tapescam), DX-style 2-op FM (hank), WeirdDrums (weird)

Each function takes the plugin's parameters (panels.load_params) and returns its pages. The grid layout of
panels.py (page / band / sec) still works for a page that has no hardware drawing."""
import m_euro
import m_fx
import m_misc
import m_roland

PANELS = {
    "303": m_roland.p303, "8w8": m_roland.p808, "9w9": m_roland.p909, "6w6": m_roland.p606, "hush1": m_roland.p101,
    "cw78": m_roland.pcr78,
    "tapedelay": m_fx.ptape, "juno": m_fx.pjuno, "4keq": m_fx.p4k, "midiverb": m_fx.pmidiverb,
    "braids": m_euro.pbraids, "plaits": m_euro.pplaits, "mrhyde": m_euro.pmrhyde, "denis": m_euro.pdenis, "ml185": m_euro.pml185,
    "libpo32": m_misc.plibpo32, "chiptune": m_misc.pchip, "psxverb": m_misc.ppsx, "busdriver": m_misc.pbus,
    "ducker": m_misc.pduck, "filter": m_misc.pfilter, "tapescam": m_misc.ptapescam, "hank": m_misc.phank,
    "weird": m_misc.pweird, "breakslicer": m_misc.pbreak,
}
