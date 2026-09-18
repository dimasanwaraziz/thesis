# Riset Mingguan Thesis — 18 September 2026

**Topik:** Multiple Embedding Steganography (MES): Parallel Embedding Architecture in RGB Color Space for High-Capacity Image-in-Image Watermarking

Catatan: ini adalah run riset mingguan pertama yang tercatat di folder `riset/`, jadi cakupan literaturnya sengaja dibuat lebih luas (2023–2026) untuk membangun basis awal. Run berikutnya akan fokus ke publikasi baru saja.

---

## Ringkasan Progress Draft

Kondisi draft di `dokumen_thesis/` sebelum revisi minggu ini:

| Chapter | Status | Catatan |
|---|---|---|
| Chapter 1 — Introduction | Kerangka lengkap | Background, problem statement, objectives, scope, significance sudah ada. Hanya 1 sitasi (Liu & Su 2025). |
| Chapter 2 — Literature Review | **Paling tipis (28 baris)** | 4 subbab konseptual + 2 subbab related studies. Belum ada sintesis, belum ada research gap eksplisit, belum ada pembahasan steganalysis. |
| Chapter 3 — Methodology | Kerangka lengkap | Channel decomposition, edge detection, parallel embedding, metrik. Metrik SSIM belum ada padahal disebut di scope Chapter 1. |
| Chapter 4 — Results | Placeholder | Tabel kapasitas & PSNR/SSIM masih data ilustratif (sudah diberi catatan oleh Dimas). Ada satu kalimat terpotong dan satu bug kolom tabel. |
| Chapter 5 — Conclusion | Kerangka lengkap | 4 kesimpulan + 4 rekomendasi. Belum ada bagian limitations. |

Masalah paling menonjol: **`ref_database.bib` masih berisi 5 entri bawaan template tentang biometrik palmprint** (`01_journal`–`05_journal`) yang sama sekali tidak relevan dengan topik steganografi, dan hanya 1 entri yang benar-benar dipakai (`liu2025color`). Basis literatur inilah yang menjadi prioritas perbaikan minggu ini.

---

## Paper/Jurnal Baru yang Ditemukan

Sebelas paper di bawah ini sudah ditambahkan ke `ref_database.bib` (semua entri lama tidak disentuh). Diurutkan berdasarkan relevansi terhadap argumen thesis.

### A. Skema edge-adaptive high-capacity (pembanding kapasitas paling langsung)

1. **Patwari, B., Ghosal, S. K., Dhar, S., & Nandi, U. (2025).** *Variable payload-based image steganographic scheme using dilated Laplacian of Gaussians edge detection.* Multimedia Tools and Applications, 84(38), 47227–47259. DOI: [10.1007/s11042-025-21016-5](https://doi.org/10.1007/s11042-025-21016-5) — key: `patwari2025dilatedlog`
   Menggunakan LoG + dilasi morfologis sehingga piksel *tetangga* edge juga ikut jadi kandidat payload berat, dengan rasio alokasi X:Y yang bisa diatur. **Melaporkan hingga 3.44 bpp, PSNR > 35 dB, SSIM > 0.96.**
   → Ini angka paling penting minggu ini: target 3.0 bpp thesis sudah dilampaui oleh skema grayscale yang ada.

2. **Singh, A. K., & Singh, J. (2026).** *Parameter optimized edge guided image steganography using variable bit LSB embedding for high capacity and visual fidelity.* Discover Applied Sciences, 8(6), 620. DOI: [10.1007/s42452-026-08602-4](https://doi.org/10.1007/s42452-026-08602-4) — key: `singh2026edgeopt`
   Memperlakukan threshold hysteresis Canny sebagai **variabel optimasi**, bukan konstanta. Hasil: hingga 3.3 bpp, PSNR > 34 dB, SSIM > 0.82.
   → Langsung relevan untuk justifikasi pemilihan threshold Canny di Chapter 3.

3. **Ismail, S. M., AbuAladas, F. E., Abu Helou, M., & Abu-ulbeh, W. (2026).** *Edge-Adaptive High-Capacity Image Steganography Using Hybrid Edge Detection and MSB Embedding.* Computers, 15(3), 141. DOI: [10.3390/computers15030141](https://doi.org/10.3390/computers15030141) — key: `ismail2026edgeadaptive`
   Canny + Sobel digabung untuk peta kompleksitas yang lebih stabil. Kapasitas ~2.97 bpp, tapi **PSNR > 38 dB, SSIM > 0.97, plus uji chi-square dan RS steganalysis.**
   → Contoh posisi trade-off yang berlawanan dengan MES (kapasitas lebih rendah, imperceptibility & bukti keamanan lebih kuat).

### B. Skema colour-aware / multi-channel (ruang kompetisi langsung MES)

4. **Al-Jburi, M. A., & Broumandnia, A. (2026).** *Real-time, imperceptible, and high-capacity color image steganography using 3D Exploiting Modification Direction (3DEMD) and 3D Baker chaotic mapping.* Multimedia Tools and Applications, 85(6), 530. DOI: [10.1007/s11042-026-21685-w](https://doi.org/10.1007/s11042-026-21685-w) — key: `aljburi2026emd3d`
   Memperlakukan triple (R,G,B) satu piksel sebagai **satu koordinat 3D** — satu modification event untuk tiga channel sekaligus, dengan enkripsi 3D Baker chaotic map.
   → **Paper paling penting untuk membedakan kontribusi MES.** Ini *colour-aware* tapi *coupled*; MES *decoupled*. Perbedaan ini harus dinyatakan eksplisit, kalau tidak reviewer akan bertanya "apa bedanya dengan 3DEMD?".

5. **Li, Q., Ma, B., Fu, X., Wang, X., Wang, C., & Li, X. (2025).** *Robust Image Steganography via Color Conversion.* IEEE Transactions on Circuits and Systems for Video Technology, 35(2), 1399–1408. DOI: [10.1109/TCSVT.2024.3466961](https://doi.org/10.1109/TCSVT.2024.3466961) — key: `li2025colorconversion`
   Pendekatan colour space dari sisi robustness terhadap distorsi aktif.
   → Berguna sebagai pembatas ruang lingkup: arah ini eksplisit di luar scope thesis.

### C. Steganalysis & keamanan (celah terbesar draft saat ini)

6. **Amrutha, E., Arivazhagan, S., & Jebarani, W. S. L. (2023).** *Novel color image steganalysis method based on RGB channel empirical modes to expose stego images with diverse payloads.* Pattern Analysis and Applications, 26(1), 239–253. DOI: [10.1007/s10044-022-01102-2](https://doi.org/10.1007/s10044-022-01102-2) — key: `amrutha2023rgbsteganalysis`
   **Paper paling kritis minggu ini.** Premisnya: embedding independen di channel warna terpisah **merusak korelasi alami antar-channel**, dan kerusakan itu terdeteksi meskipun tiap channel secara terpisah tampak normal secara statistik.
   → Ini tantangan langsung terhadap arsitektur paralel MES. Independensi yang membuka kapasitas justru properti yang dicari detektor colour-aware. Harus dijawab, bukan dihindari.

7. **Kombrink, M. H., Geradts, Z. J. M. H., & Worring, M. (2025).** *Image Steganography Approaches and Their Detection Strategies: A Survey.* ACM Computing Surveys, 57(2), 1–40. DOI: [10.1145/3694965](https://doi.org/10.1145/3694965) — key: `kombrink2025survey`
   Survey sistematis yang memetakan tiap pendekatan embedding ke strategi deteksi yang mengalahkannya.
   → Referensi standar untuk argumen "PSNR tinggi ≠ aman".

8. **Alrusaini, O. A. (2025).** *Deep learning for steganalysis: evaluating model robustness against image transformations.* Frontiers in Artificial Intelligence, 8, 1532895. DOI: [10.3389/frai.2025.1532895](https://doi.org/10.3389/frai.2025.1532895) — key: `alrusaini2025robustness`
   Membandingkan EfficientNet, SRNet, ResNet, Xu-Net, Yedroudj-Net. Performa detektor **sendiri tidak stabil** terhadap transformasi biasa; Xu-Net dan Yedroudj-Net turun tajam dengan noise.
   → Implikasi praktis: jangan pakai satu detektor saja untuk klaim keamanan; pakai panel kecil.

9. **Andone, M.-D., Morteci, T.-S., Ștefănescu, Ș.-N., & Morogan, L. (2026).** *StegBench: A Dual-Branch Benchmark Dataset for Multi-Class Steganalysis in JPEG and PNG Formats Using Deep Learning.* Algorithms, 19(8), 655. DOI: [10.3390/a19080655](https://doi.org/10.3390/a19080655) — key: `andone2026stegbench`
   Dataset benchmark terstandar untuk steganalysis multi-kelas.
   → Kandidat dataset tambahan selain 4 citra klasik USC-SIPI.

### D. Konteks image-in-image berbasis deep learning

10. **Janok, M., Forgáč, R., & Hluchý, L. (2026).** *From Pixel Modification to Generative Synthesis: A Survey of Deep Learning for Image Data Hiding.* Journal of Imaging, 12(9), 417. DOI: [10.3390/jimaging12090417](https://doi.org/10.3390/jimaging12090417) — key: `janok2026survey`
   Taksonomi tiga paradigma (modification / synthesis / logic-based), menelusuri CNN → GAN → INN → Transformer → diffusion. Mengidentifikasi empat celah infrastruktur: **benchmarking fragmentation, narrow robustness evaluation, domain generalization failures, computational infeasibility.**
   → Sumber terbaik untuk memposisikan MES terhadap metode deep learning tanpa harus bersaing langsung.

11. **Alrawashdeh, R., Almuhammadi, S., Niazi, M., Mahmud, M., & Rahman, M. M. (2025).** *Secure edge-guided adaptive image steganography using HED-based attention maps and CNN.* Scientific Reports, 15, 42984. DOI: [10.1038/s41598-025-27150-2](https://doi.org/10.1038/s41598-025-27150-2) — key: `alrawashdeh2025hed`
   Mengganti detektor edge manual dengan Holistically-Nested Edge Detection; attention map mengatur jumlah bit per piksel. PSNR 60.72–61.20 dB, SSIM ~0.9995, **AUC XuNet/YeNet 0.47–0.53 (setara tebakan acak)** — tapi semua itu **pada 0.1 bpp**.
   → Penting untuk dicatat perbedaan operating point-nya (0.1 bpp vs >3.0 bpp). Angka PSNR 60 dB tidak sebanding dengan 34 dB pada 3.1 bpp; kalau tidak dijelaskan, tabel perbandingan akan menyesatkan.

---

## Saran Arah/Gap Penelitian

### 1. Kapasitas >3.0 bpp sudah bukan kontribusi yang berdiri sendiri (prioritas tinggi)

Ini temuan paling penting minggu ini dan berdampak langsung ke framing thesis. Patwari et al. (3.44 bpp) dan Singh & Singh (3.3 bpp) sudah melampaui target 3.0 bpp — **pada citra grayscale**. Kalau Chapter 1 dan Chapter 4 membingkai ">3.0 bpp" sebagai kontribusi utama, reviewer akan langsung menunjuk dua paper ini.

**Saran framing ulang:** posisikan 3.0 bpp sebagai *syarat kelayakan* (admissibility floor), bukan klaim. Kontribusinya adalah **dari mana kapasitas itu berasal** — tiga bidang warna yang di-budget independen, bukan alokasi bit yang lebih agresif dalam satu bidang. Ini membuat gain di Tabel 4.1 menjadi hasil *arsitektural*, bukan *parametrik*. Framing ini sudah diterapkan di revisi Chapter 2, 3, dan 4 minggu ini.

### 2. Korelasi antar-channel adalah ancaman spesifik terhadap arsitektur paralel (prioritas tinggi)

Amrutha et al. (2023) menunjukkan justru independensi antar-channel yang dicari detektor colour-aware. Ini bukan alasan membatalkan MES, tapi berarti:

- klaim keamanan MES **harus** diuji terhadap detektor colour-aware, bukan hanya detektor channel-agnostic;
- preservasi korelasi antar-channel sebaiknya jadi **design constraint eksplisit** di Chapter 3, bukan sesuatu yang dicek belakangan;
- alokasi `|S_R|, |S_G|, |S_B|` proporsional terhadap kapasitas lokal tiap channel adalah mitigasi paling sederhana (menjaga distorsi relatif antar bidang sebanding dengan statistik cover), dan sudah dituliskan di revisi Chapter 3.

Kalau nanti hasil steganalysis menunjukkan AUC menyimpang dari 0.5 **hanya** pada detektor colour-aware, itu sinyal untuk merevisi aturan alokasi — bukan arsitektur paralelnya.

### 3. Sinkronisasi edge map belum dijelaskan di draft (prioritas tinggi, risiko teknis)

Chapter 3 menyebut Canny diterapkan pada tiap channel, tapi belum menjelaskan bagaimana penerima merekonstruksi peta edge yang **sama persis** dari stego-image. Kalau embedding menggeser nilai piksel melewati threshold hysteresis, partisi yang dihitung ulang berbeda dan ekstraksi gagal. Ini bukan detail kecil — ini menentukan apakah skema bisa blind extraction atau butuh side information.

Tiga opsi standar di literatur: (a) hitung edge map dari bit-plane yang tidak diubah embedding, (b) kirim peta/seed sebagai side information, (c) turunkan peta dari statistik invarian. Revisi Chapter 3 minggu ini memilih opsi (a) — **mohon dicek apakah ini memang sesuai dengan implementasi yang sudah/akan Dimas buat.**

### 4. Pembeda terhadap 3DEMD harus eksplisit (prioritas menengah)

Al-Jburi & Broumandnia (2026) adalah metode colour image steganography high-capacity terbaru. Perbedaan MES: 3DEMD **coupled** (satu modification event atas triple), MES **decoupled** (tiga budget independen). Kalimat pembeda ini sudah ditambahkan di Chapter 2 dan Chapter 3.

### 5. Perbandingan dengan metode deep learning harus menyebut operating point (prioritas menengah)

Jangan menaruh PSNR 60 dB milik Alrawashdeh et al. sejajar dengan PSNR 34 dB MES tanpa keterangan — bedanya 0.1 bpp vs >3.0 bpp. Argumen yang lebih kuat: metode berbasis pembelajaran melakukan rekonstruksi **aproksimatif**, sedangkan aplikasi target thesis (medical imaging, komunikasi terenkripsi) menuntut recovery **bit-exact**. Ini pembeda kualitatif yang tidak bisa dikalahkan dengan angka PSNR.

### 6. Dataset evaluasi terlalu kecil untuk klaim keamanan (prioritas menengah)

Empat citra klasik cukup untuk karakterisasi trade-off kapasitas–kualitas, tapi tidak cukup untuk klaim statistik tentang detectability. Saran: pertahankan 4 citra klasik untuk komparabilitas dengan prior work, tambahkan korpus warna yang lebih besar (StegBench atau sejenisnya) khusus untuk evaluasi steganalysis.

---

## Update Perkembangan Terbaru (State-of-the-Art)

Empat tren yang terbaca dari literatur 2025–2026:

1. **Edge detector bergeser dari saklar biner ke estimator kapasitas bergradasi.** Dulu: piksel edge vs non-edge. Sekarang: multi-operator (Canny+Sobel), dilasi morfologis pada peta LoG, attention map HED yang memberi bobot kontinu. Implikasi untuk MES: klasifikasi "Edge"/"Smooth" dua kelas di Chapter 3 adalah pilihan yang sah tapi konservatif — bisa jadi arah pengembangan.

2. **Parameter detektor menjadi variabel optimasi, bukan konstanta.** Singh & Singh mengoptimasi threshold Canny secara sistematis. Threshold yang dipilih sebaiknya dilaporkan bersama hasil, supaya operating point tiap pengukuran jelas.

3. **Bukti resistensi steganalysis kini menjadi ekspektasi standar, bukan nilai tambah.** Dari paper-paper 2025–2026 yang ditemukan, yang melaporkan imperceptibility terkuat adalah juga yang melaporkan hasil steganalysis (chi-square, RS, XuNet, YeNet). Draft thesis saat ini hanya punya histogram analysis — itu statistik orde pertama, sementara detektor state-of-the-art bekerja pada fitur residual orde tinggi.

4. **Fragmentasi benchmark diakui sebagai kelemahan struktural bidang ini.** Janok et al. menyebutnya eksplisit; StegBench adalah respons langsung terhadap masalah ini. Menyebut isu ini di thesis justru memperkuat kredibilitas metodologi.

Tidak ditemukan publikasi baru minggu ini yang secara khusus mengusulkan *parallel independent multi-channel embedding* dalam pengertian yang sama dengan MES — celah penelitian yang diklaim thesis masih terbuka.

---

## Masukan Outline/Struktur

Struktur 5 chapter sudah standar dan logis (Introduction → Literature Review → Methodology → Results → Conclusion). Tidak perlu diubah. Yang kurang adalah kedalaman, bukan kerangka.

**Chapter 1** — Sudah baik. Problem statement kini punya 4 poin (ditambah poin keamanan colour-aware). Objectives dan scope tidak diubah karena itu keputusan desain Dimas.

**Chapter 2** — Sebelumnya bagian terlemah: 28 baris, tanpa sintesis, tanpa research gap eksplisit, tanpa pembahasan steganalysis. Untuk ukuran thesis S2, literature review yang hanya membahas satu paper pembanding sulit dipertahankan di sidang. Sudah direstrukturisasi minggu ini (lihat bagian berikutnya).

**Chapter 3** — Kerangkanya benar. Tiga kekurangan yang sudah ditambal: (a) tidak ada justifikasi kenapa Canny dan bukan Sobel/LoG, (b) tidak ada penjelasan sinkronisasi edge map, (c) SSIM disebut di scope Chapter 1 dan dilaporkan di Chapter 4 tapi tidak didefinisikan di Chapter 3.

**Chapter 4** — Masih placeholder, wajar. Dua bug kecil yang diperbaiki: deklarasi tabular 5 kolom padahal datanya 4 kolom (berpotensi error LaTeX), dan satu kalimat yang terpotong di bagian imperceptibility ("despite the high capacity..." tanpa awalan).

**Chapter 5** — Kesimpulan tidak diubah. Ditambah bagian **Limitations**, yang biasanya ditanyakan penguji dan lebih baik dinyatakan sendiri daripada ditemukan penguji.

**Saran struktural yang belum dikerjakan (untuk pertimbangan Dimas):**

- Chapter 2 sebaiknya diberi **tabel perbandingan metode** (metode | domain | carrier | kapasitas | PSNR | SSIM | uji steganalysis) — memudahkan penguji melihat posisi MES sekilas.
- Chapter 3 belum punya **diagram alur embedding dan extraction**. Untuk klaim arsitektural seperti "paralel vs sekuensial", satu gambar jauh lebih meyakinkan daripada paragraf.
- Chapter 3 belum punya **pseudocode algoritma** (paket `algorithm`/`algorithmic` sudah ter-load di preamble, tinggal dipakai).
- Belum ada pembahasan **kompleksitas komputasi / waktu eksekusi**, padahal "paralel" secara alami memunculkan pertanyaan soal throughput.

---

## Perubahan Isi Chapter Minggu Ini

Semua perubahan bisa dicek diff-nya di GitHub dan di-revert per file kalau tidak sesuai.

### `chapter_2.tex` — revisi menyeluruh (28 → ~60 baris, penulisan ulang)

Direstrukturisasi menjadi empat bagian bernomor: Foundations → Related Studies → Steganalysis & Security → Synthesis & Research Gap.

- **Digital Steganography** — ditulis ulang, menambahkan kerangka trade-off tiga sumbu (capacity / imperceptibility / security) dengan sitasi ke dua survey.
- **RGB Color Model** — ditambah dua paragraf soal korelasi antar-channel (liabilitas keamanan) dan sensitivitas HVS yang tidak seragam antar primer (peluang).
- **PVD** — ditambah penjelasan bahwa tabel kuantisasi diturunkan dari cover, sehingga kapasitas adalah properti cover, bukan konstanta yang dipilih perancang.
- **Edge Detection** — ditambah pembahasan masalah sinkronisasi peta edge dan tiga strategi penyelesaiannya, plus perkembangan multi-operator dan dilasi.
- **Sequential Embedding** — diperjelas dua konsekuensi: budget Blue channel adalah residual, dan error propagation antar-channel.
- **Subbab baru: Edge-Adaptive and High-Capacity Spatial Schemes** — tiga paper pembanding dengan angka bpp/PSNR/SSIM, plus tiga observasi yang menjustifikasi framing ulang target kapasitas.
- **Subbab baru: Colour-Aware and Multi-Channel Schemes** — 3DEMD dan color conversion, dengan pembeda eksplisit terhadap MES.
- **Subbab baru: Learning-Based Image-in-Image Hiding** — memposisikan MES terhadap deep learning lewat argumen operating point + exact recovery.
- **Recent Developments** → diganti menjadi **The Reference Baseline: Liu and Su (2025)**, diperluas: apa yang diwarisi dan di mana titik divergensinya.
- **Section baru: Steganalysis and Security Evaluation** — bagian yang sebelumnya tidak ada sama sekali.
- **Section baru: Synthesis and Research Gap** — empat kesimpulan bernomor lalu pernyataan gap eksplisit.

Klaim inti tidak berubah: MES = parallel embedding RGB, target >3.0 bpp, PSNR >30 dB.

### `chapter_1.tex` — revisi sedang

- Background: ditambah satu kalimat bahwa skema spatial mutakhir sudah melaporkan 3.0–3.5 bpp (3 sitasi), dan satu paragraf baru yang memposisikan MES terhadap skema colour-aware dan deep learning.
- Statement of the Problem: **ditambah poin ke-4** tentang kurangnya bukti keamanan colour-aware.
- `\cite{liu2025color}` → `\citet{liu2025color}` (perbaikan tata bahasa sitasi natbib).
- Objectives, Scope, Significance **tidak diubah**.

### `chapter_3.tex` — revisi sedang

- Ditambah `\label{cap:chapter3}`.
- Edge Detection: ditambah justifikasi pemilihan Canny, paragraf **Edge-map synchronisation**, dan paragraf **Threshold selection**.
- Parallel Embedding: ditambah kalimat pembeda terhadap 3DEMD.
- **Subbab baru: Inter-Channel Correlation as a Design Constraint.**
- Experiment Scenario: ditambah sumber dataset (USC-SIPI) dan dua catatan validitas.
- **Subbab baru: Structural Similarity Index (SSIM)** dengan rumusnya — sebelumnya SSIM dipakai di Chapter 4 tanpa pernah didefinisikan.
- Embedding Capacity: ditambah penjelasan bahwa 3.0 bpp adalah ambang kelayakan, bukan klaim.
- **Section baru: Supplementary Security Evaluation**, dengan penegasan bahwa ini berbeda dari robustness terhadap serangan aktif (yang tetap di luar scope).

⚠️ **Perlu konfirmasi Dimas:** penambahan Supplementary Security Evaluation memperluas metodologi. Ini dinilai perlu karena literatur 2025–2026 sudah memperlakukan bukti steganalysis sebagai standar, tapi kalau Dimas memang ingin scope tetap sesempit semula, cukup hapus section ini di Chapter 3 dan section Steganalysis Evaluation di Chapter 4.

### `chapter_4.tex` — revisi ringan–sedang (angka hasil tidak disentuh)

- Ditambah `\label{cap:chapter4}`.
- **Perbaikan bug:** `\begin{tabular}{|l|c|c|c|c|}` → `{|l|c|c|c|}` (5 kolom dideklarasikan, 4 kolom datanya).
- **Perbaikan kalimat terpotong:** paragraf setelah Tabel 4.2 sebelumnya diawali "despite the high capacity." tanpa induk kalimat. Direkonstruksi memakai angka yang sudah ada di tabel (30 dB, 0.88) — tidak ada angka baru.
- Capacity Analysis: ditambah paragraf interpretasi (pola Baboon vs Lenna) dan pembanding literatur.
- Imperceptibility Analysis: ditambah paragraf interpretasi urutan hasil dan penempatan SSIM 0.88–0.93 dalam rentang referensi literatur.
- Histogram Analysis: ditambah peringatan bahwa histogram adalah statistik orde pertama.
- **Section baru: Steganalysis Evaluation** (ditandai jelas sebagai *pending*, berisi panduan interpretasi hasil).
- Tabel, angka, dan Summary of Findings **tidak diubah**.

### `chapter_5.tex` — revisi ringan

- Rekomendasi Optimization ditambah rujukan konkret ke Singh & Singh.
- **3 rekomendasi baru:** Colour-Aware Steganalysis, Standardised Benchmarking, Correlation-Preserving Allocation.
- **Section baru: Limitations** (3 batasan: ukuran dataset, kondisi passive-warden, perbandingan tidak setara dengan deep learning).
- Empat butir Conclusions **tidak diubah**.

### `ref_database.bib`

11 entri baru ditambahkan di akhir file dengan penanda komentar. **Tidak ada entri lama yang diubah atau dihapus** — termasuk 5 entri biometrik bawaan template, yang sebaiknya Dimas hapus sendiri kalau memang tidak terpakai.

### Verifikasi

Seluruh dokumen dikompilasi ulang dengan `latexmk -pdf` untuk memastikan tidak ada error: **berhasil, 47 halaman, semua sitasi ter-resolve.** Satu-satunya warning tersisa adalah `\ref{fig:histogram}` yang memang sudah ditandai "to be added" sejak sebelumnya. File PDF hasil build sengaja **tidak** ikut di-commit agar diff tetap bersih.

---

## Status Push ke GitHub

⚠️ **Commit berhasil dibuat secara lokal, tetapi push ke `main` GAGAL.**

Penyebabnya bukan token dan bukan konflik dengan remote. Clone dan fetch berjalan normal (read-only), tetapi push ditolak oleh egress proxy lingkungan tempat task ini berjalan:

```
remote: access denied by the git proxy: dimasanwaraziz/thesis is not in this
session's authorized repository set, so the proxy will not inject a credential
for it. To fix, add the repository to the session's sources.
fatal: unable to access 'https://github.com/dimasanwaraziz/thesis.git/':
The requested URL returned error: 403
```

Langkah yang sudah dicoba: `git pull --rebase` (remote sudah up to date, tidak ada konflik) lalu push ulang sekali — hasilnya sama. Force push **tidak** dilakukan.

Ini adalah penolakan kebijakan lingkungan, bukan masalah yang bisa diselesaikan dengan mengulang percobaan. Agar run berikutnya bisa push otomatis, repo `dimasanwaraziz/thesis` perlu ditambahkan ke daftar *sources* / authorized repository milik scheduled task ini.

**Sementara itu, hasil kerja minggu ini tersedia dalam dua bentuk:**

1. `riset-thesis-2026-09-18.md` — dokumen ini.
2. `riset-thesis-2026-09-18.patch` — patch commit lengkap (format `git format-patch`), berisi seluruh perubahan pada `ref_database.bib`, `chapter_1.tex` s/d `chapter_5.tex`, dan file riset ini.

Cara menerapkannya di repo lokal:

```bash
cd /path/ke/thesis
git am < riset-thesis-2026-09-18.patch
git push origin main
```

Kalau `git am` menolak karena konteks berbeda, gunakan:

```bash
git apply --3way riset-thesis-2026-09-18.patch
```

Identitas commit di dalam patch sudah diset ke "Dimas Anwar Aziz" <dimasanwaraziz@gmail.com>.
