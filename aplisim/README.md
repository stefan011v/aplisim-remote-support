# Aplisim desktop build

Ovaj projekat priprema nepotpisane testne pakete za Windows x64, macOS Intel i
macOS Apple Silicon. Prvi macOS build i Windows recovery pakovanje su uspešni. Sistemske ikone i tray ikone i dalje
su upstream RustDesk ikone; logo u aplikaciji, boje i naziv su Aplisim.

## Priprema izvora lokalno

```sh
git -C upstream/rustdesk submodule update --init --recursive
python3 scripts/export-build-project.py
```

Dobija se samostalan izvorni projekat u `dist/aplisim-build-source`, sa vendorizovanim
podmodulom, licencom i tri workflow datoteke. Nema privatnih ključeva, VPS podataka
ili automatskog objavljivanja. Izvoz odbija prepisivanje postojećeg direktorijuma;
za sledeći izvoz navesti novu `--output` putanju.

## Build na GitHub Actions

Izvezeni direktorijum treba da bude koren zasebnog GitHub repozitorijuma.
Privatni repozitorijum: https://github.com/stefan011v/aplisim-remote-support. Posle postavljanja izvora,
ručno pokrenuti workflow **Aplisim desktop builds** iz kartice Actions.

- `preview`: koristi rezervisani domen `aplisim-preview.invalid`; nema veze sa
  javnim RustDesk serverima. Služi za proveru izgleda i pokretanja aplikacije.
- `configured`: zahteva repository variables `APLISIM_SERVER` (domen ili IPv4)
  i `APLISIM_PUBLIC_KEY` (sadržaj `id_ed25519.pub`). Provera prekida build ako
  podaci nisu ispravnog formata. Dostupnost i vlasništvo servera se ne proveravaju.

Skripta `aplisim/configure-build.py` postavlja server i javni ključ u vendorizovanom
`libs/hbb_common/src/config.rs` pre kompajliranja. Samo postavljanje promenljivih
`RENDEZVOUS_SERVER`/`RS_PUB_KEY` nije dovoljno u ovoj upstream reviziji.

Workflow zadržava upstream pripremu Flutter/Rust mosta, biblioteka i build alata.
Windows izlaz je samoraspakujući EXE; macOS izlazi su odvojeni DMG paketi.
Rezultati se čuvaju kao Actions artifacts zajedno sa SHA256SUMS i javnim build
metapodacima. Nema kreiranja GitHub Release-a ni slanja paketa servisu za potpisivanje.
Paketi su izgrađeni na Windows/macOS runnerima; budući build-ovi zavise od
dostupnosti upstream dependency servisa. Pokretanje može potrošiti Actions minute.

## Pre distribucije

Završiti ICO/ICNS i tray ikone. Proveriti instalaciju, naziv procesa i servisa,
macOS dozvole za snimanje ekrana i Accessibility, pokretanje posle restarta,
direktnu i relay vezu. Dodati Windows potpis i macOS potpis/notarizaciju.
MSI još nije uključen. Zadržati RustDesk licencu i odgovarajući izvorni kod.

## Površina promene

Osim logotipa, Flutter boja, desktop naziva i Windows metapodataka, macOS menja
AppInfo.xcconfig (naziv i bundle ID), project.pbxproj (bundle ID i proizvod),
Runner.xcscheme (naziv proizvoda), MainMenu.xib (Swift modul), i jednu putanju u
build.py koja kopira pomoćni servis u Aplisim.app. Sve su potrebne da proizvod
ostane dosledan nakon preimenovanja. Legacy Sciter build putanja nije menjana.
Izvezeni hbb_common menja samo podrazumevani server i javni ključ za izabrani build.
