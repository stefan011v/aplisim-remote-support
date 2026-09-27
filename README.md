# Aplisim Remote Support

Brendirani RustDesk klijent za Windows x64 i macOS (Intel i Apple Silicon).

**Status:** priprema i prvi CI build; gotovi paketi još nisu potvrđeni.
Logo i boje aplikacije su Aplisim. Sistemske i tray ikone još su RustDesk.
Ovaj repozitorijum sadrži native Flutter/Rust aplikaciju. HTML vizuelni prototip
iz radnog projekta nije prenet u native UI.

## Pokretanje build-a

Actions → **Aplisim desktop builds** → **Run workflow**:

- `preview`: testiranje izgleda bez povezivanja sa javnim RustDesk serverima.
- `configured`: koristi repository variables `APLISIM_SERVER` i `APLISIM_PUBLIC_KEY`.
  Uneti samo javni ključ iz `id_ed25519.pub`.

Uspešan build prilaže nepotpisani Windows EXE i macOS DMG pakete kao Actions
artifacts, uz SHA256SUMS. Ne pravi javni Release i ne šalje pakete spoljnim
servisima za potpisivanje. Pre distribucije završiti sistemske ikone, potpisivanje,
notarizaciju i testove instalacije/udaljenih sesija.

Detalji: [build uputstvo](aplisim/README.md).

## Poreklo i licenca

Zasnovano na RustDesk 1.5.0. Tačne revizije su u [source.json](aplisim/source.json).
Originalna licenca ostaje u [LICENCE](LICENCE); upstream uputstva u
[UPSTREAM-README.md](aplisim/UPSTREAM-README.md).
