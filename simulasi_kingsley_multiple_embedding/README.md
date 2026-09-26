# Simulasi Kingsley & Barmawi (2020): Multiple Embedding

Implementasi Python dari paper *Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding* (JIHMSP 11(1), 2020). Penjelasan metode dan rumus ada di [`../riset/paper-kingsley-2020-multiple-embedding.md`](../riset/paper-kingsley-2020-multiple-embedding.md).

## Menjalankan

```bash
# Dengan Docker
./run.sh

# Atau langsung (Python 3.9+)
pip install -r requirements.txt
python test_kingsley.py      # 13 unit test, termasuk contoh angka dari paper
python run_simulation.py     # eksperimen lengkap, ~30 detik, output di ./hasil
```

## Isi

| File | Isi |
|---|---|
| `kingsley_stego.py` | Seluruh metode: RM(1,4) + majority decoding, modulus function, Blum Blum Shub, Key Trace (Algoritma 1 & 2), embedding ke Agreed Image, (2,2) VCS, Share 2, `embed()` / `extract()` |
| `attacks.py` | Serangan Tabel 2–5: Gaussian, salt & pepper, speckle, cropping, scratching, JPEG |
| `run_simulation.py` | Eksperimen kapasitas/PSNR (Tabel 1) dan robustness, dengan dua skenario |
| `test_kingsley.py` | Verifikasi terhadap contoh di paper dan uji *round-trip* |

## Contoh pemakaian

```python
import numpy as np
import kingsley_stego as ks

stego, agreed_stego, share1, info = ks.embed(cover, secret, agreed, seed=262139, R=0)
recovered, key = ks.extract(stego, agreed_stego, share1, R=0)
print(info["EC_paper"], info["Nc"], ks.psnr(cover, stego))
```

Semua citra grayscale `uint8`. Cover dan agreed image yang dipakai eksperimen adalah 512×512.

## Keputusan implementasi (bagian yang ambigu di paper)

| Bagian paper | Implementasi |
|---|---|
| Algoritma 1 tidak konsisten (indeks & loop tidak berhenti) | Rantai XOR dari belakang: `CK_j = R ⊕ db_{j+1} ⊕ … ⊕ db_s`, `E = R ⊕ db_1 ⊕ … ⊕ db_s`; cocok dengan Algoritma 2 |
| Pers. (29) padding `Y mod k` | `n·k − Y`, sesuai contoh angka di paper |
| BBS: blok 18 bit → posisi | Lebar blok = `ceil(log2(pool))` (=18 untuk 512×512); nilai di luar rentang atau sudah terpakai dilewati agar tidak ada piksel ganda |
| Kunci dirender sebagai glyph 16×14 untuk dibaca mata | Tiap karakter disimpan sebagai byte ASCII (8 bit per baris) agar bisa diparse otomatis; VCS tetap (2,2) dengan pixel expansion 2 |
| Share 2 disisipkan mulai "marker q" | Share 2 (di-encode RM) di piksel paling akhir; posisi BBS diambil hanya dari piksel sebelum `q` agar tidak bertabrakan |
| Reference key R | Dianggap sudah disepakati (tidak ada di kunci) |
| "Cropping area" | Area yang disebut diisi hitam (0) |
| Kualitas JPEG tidak disebut | Q = 90 dan 75 |
| Modulus function Pers. (18) memakai ≤0 / ≥255 | Memakai < 0 / > 255 (versi Thien & Lin), supaya piksel 0 dan 255 yang valid tidak digeser |

## Skenario robustness

- **A**: asumsi paper, hanya stego I'' yang diserang dan Agreed stego A' utuh.
- **B**: serangan yang sama juga mengenai A'.

Kunci dianggap sudah diketahui penerima saat mengukur kanal rahasia. Kolom **Kunci** melaporkan secara terpisah apakah Share 2 di stego masih bisa didekode.
