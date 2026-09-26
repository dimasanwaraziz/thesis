# Bedah Paper: *Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding*

| | |
|---|---|
| **Penulis** | Katandawa Alex Kingsley, Ari Moesriami Barmawi (Graduate School of Informatics, Telkom University) |
| **Jurnal** | *Journal of Information Hiding and Multimedia Signal Processing* (JIHMSP), Vol. 11, No. 1, Maret 2020, hlm. 14–43 |
| **ISSN** | 2073-4212 |
| **Hubungan** | Versi jurnal dari tesis Kingsley (`referensi/Kingsley Thesis Book.pdf`) |
| **PDF** | `referensi/Kingsley 2020 - Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding.pdf` (diambil dari arsip Wayback Machine; link asli jurnal sudah 404) |

---

## 1. Ringkasan Satu Paragraf

Paper ini memperbaiki metode **Molaei dkk. (2017)** — steganografi berbasis *Reed–Muller code* yang menyisipkan data ke LSB-1 dan LSB-2 **semua** piksel cover grayscale (kapasitas maks 150%, PSNR ≈ 48 dB). Kingsley mengusulkan:

1. Encode citra rahasia dengan **RM(1,4)** (5 bit → 16 bit, bisa koreksi 3 bit error).
2. Pakai **hanya ¾ piksel cover**, dipilih acak dengan PRNG **Blum Blum Shub (BBS)**, dan **hanya LSB-1** yang diubah.
3. Kalau bit ter-encode lebih banyak dari ¾·H·W, bit-bit tersebut di-**"re-embed"** (multiple embedding) ke piksel yang sama melalui rantai XOR bernama **Key Trace**. Hanya 1 bit hasil XOR yang benar-benar masuk ke cover; sisa bitnya (Key Trace) disimpan di **citra kedua (Agreed Image)**.
4. Parameter rahasia (seed, jumlah siklus, ukuran citra rahasia) dikirim lewat **(2,2) Visual Cryptography Scheme (VCS)**: Share 1 dikirim lewat kanal aman, Share 2 disisipkan ke stego.

Hasil klaim: kapasitas **450%** (3× Molaei), PSNR **≈ 52 dB**, dan ketahanan lebih baik terhadap noise, cropping, scratching, dan JPEG.

---

## 2. Dasar Teori yang Dipakai

### 2.1 Reed–Muller Code RM(r, m)

Untuk bilangan bulat $0 \le r \le m$:

$$
k = \sum_{i=0}^{r} \binom{m}{i} \qquad \text{(panjang pesan)} \tag{1}
$$

$$
N = 2^{m} \qquad \text{(panjang codeword)} \tag{2}
$$

$$
d_{\min} = 2^{m-r} \qquad \text{(jarak minimum)} \tag{3}
$$

$$
t = \left\lfloor \frac{2^{m-r} - 1}{2} \right\rfloor \qquad \text{(jumlah error yang bisa dikoreksi)} \tag{4}
$$

Notasi: $[\,2^m,\; k,\; 2^{m-r}\,]$-code.

**Contoh RM(1,4)** (yang dipakai Kingsley): $k = \binom{4}{0}+\binom{4}{1} = 5$, $N = 16$, $d_{\min} = 8$, $t = 3$.

| Kode | k | N | Ekspansi N/k | t | Kemampuan koreksi t/N | Dipakai oleh |
|---|---|---|---|---|---|---|
| RM(1,3) | 4 | 8 | 2 | 1 | 12.5% | Molaei (LSB-1) |
| RM(2,5) | 16 | 32 | 2 | 3 | 9.38% | Molaei (LSB-2) |
| **RM(1,4)** | **5** | **16** | **3.2** | **3** | **18.75%** | **Kingsley** |

#### Konstruksi rekursif (u | u+v)

$$
RM(r,m) = \{ (\mathbf{u},\, \mathbf{u}+\mathbf{v}) : \mathbf{u} \in RM(r, m-1),\; \mathbf{v} \in RM(r-1, m-1) \} \tag{5}
$$

#### Matriks generator

$$
G_{r,m} = \begin{bmatrix} G_{r,m-1} & G_{r,m-1} \\ \mathbf{0} & G_{r-1,m-1} \end{bmatrix} \tag{6}
$$

dengan $G_{0,m}$ = vektor 1 sepanjang $2^m$ dan $G_{m,m} = I_{2^m}$.

Untuk RM(1,4):

$$
G_{1,4} = \begin{bmatrix}
0000000011111111 \\
0000111100001111 \\
0011001100110011 \\
0101010101010101 \\
1111111111111111
\end{bmatrix}
$$

#### Encoding

$$
\mathbf{c} = \mathbf{u} \cdot G_{r,m} \pmod 2 \tag{7}
$$

**Contoh:** $\mathbf{u} = (1,0,1,0,1)$ → $\mathbf{c}$ = baris1 ⊕ baris3 ⊕ baris5 = `1100110000110011`.

> ⚠️ **Errata di paper:** hasil encoding pada hlm. 17 ditulis `0000111001101011`, padahal hasil perkalian yang benar adalah `1100110000110011` (saya verifikasi ulang; nilai ini juga muncul sebagai *corrected vector* $cc$ di hlm. 19 paper itu sendiri).

#### Decoding: Majority Logic (Reed decoding)

Untuk RM(1,4), setiap bit pesan $u_1..u_4$ punya **8 persamaan check-sum** yang independen:

$$
\begin{aligned}
u_1 &= c_1{+}c_2 = c_3{+}c_4 = c_5{+}c_6 = \dots = c_{15}{+}c_{16} \\
u_2 &= c_1{+}c_3 = c_2{+}c_4 = c_5{+}c_7 = \dots = c_{14}{+}c_{16} \\
u_3 &= c_1{+}c_5 = c_2{+}c_6 = c_3{+}c_7 = \dots = c_{12}{+}c_{16} \\
u_4 &= c_1{+}c_9 = c_2{+}c_{10} = c_3{+}c_{11} = \dots = c_8{+}c_{16}
\end{aligned}
$$

Nilai $u_i$ diambil dari **mayoritas** 8 check-sum. Lalu $u_0$ ditentukan dari mayoritas vektor sisa:

$$
\mathbf{x}' = \mathbf{x} - (u_1,u_2,u_3,u_4 \text{ bagian}) \cdot G \tag{14}
$$

Karena tiap check-sum melibatkan 2 bit, satu error hanya merusak 1 dari 8 persamaan → hingga 3 error masih kalah suara → **terkoreksi**.

Konversi codeword terkoreksi ke pesan:

$$
\mathbf{u} = \mathbf{r}' \cdot G_{r,m}^{T} \tag{15}
$$

Bentuk umum majority decoding (r+1 tahap) memakai himpunan indeks $S$, $E$, $S^c$, $B = q + S$ dan persamaan keputusan $A^{(l)} = \sum_{t\in B} x_t^{(l)}$ (Pers. 8–13 di paper, diambil dari Lin & Costello).

### 2.2 Modulus Function (Thien & Lin, 2003)

Menyisipkan nilai $z_i \in [0, 2^n-1]$ ke $n$ bit rendah piksel $x_i$ dengan perubahan sekecil mungkin.

**Selisih:**

$$
dd_i = z_i - (x_i \bmod 2^n) \tag{16}
$$

**Minimisasi perubahan:**

$$
dd_i' =
\begin{cases}
dd_i, & -\left\lfloor \frac{2^n-1}{2} \right\rfloor \le dd_i \le \left\lceil \frac{2^n-1}{2} \right\rceil \\[4pt]
dd_i + 2^n, & -2^n+1 \le dd_i \le -\left\lfloor \frac{2^n-1}{2} \right\rfloor \\[4pt]
dd_i - 2^n, & \left\lceil \frac{2^n-1}{2} \right\rceil \le dd_i \le 2^n
\end{cases} \tag{17}
$$

**Koreksi overflow/underflow:**

$$
x_i' =
\begin{cases}
x_i + dd_i', & 0 \le x_i + dd_i' \le 255 \\
x_i + dd_i' + 2^n, & x_i + dd_i' < 0 \\
x_i + dd_i' - 2^n, & x_i + dd_i' > 255
\end{cases} \tag{18}
$$

**Ekstraksi:**

$$
z_i = x_i' \bmod 2^n \tag{19}
$$

> Catatan: Kingsley selalu memakai $n = 1$. Untuk $n=1$ fungsi ini praktis menjadi **LSB ±1** — piksel berubah paling banyak 1 level, dan hanya jika LSB-nya tidak sama dengan bit rahasia (peluang ≈ 50%).

---

## 3. Metode Pembanding: Molaei dkk. (2017)

1. Bit rahasia $SD$ dibagi dua bagian:
   - $B$ bit pertama → blok ukuran $k_0 = 4$, encode RM(1,3) → sisipkan ke **LSB-1** semua piksel.
     $$ nb_0 = \left\lceil \frac{B}{k_0} \right\rceil \tag{20} $$
   - Sisa $(SD - B)$ → blok ukuran $k_1 = 16$, encode RM(2,5) → sisipkan ke **LSB-2**.
     $$ nb_1 = \left\lceil \frac{SD - B}{k_1} \right\rceil \tag{21} $$
2. Penyisipan **berurutan (serial)** dengan modulus function.

**Kapasitas maksimum:**

$$
D_{\max} = \sum_{i=0}^{n} \frac{H \cdot W}{2^{m_i}} \cdot k_i \tag{22}
\qquad
P = \frac{D_{\max}}{H \cdot W} \tag{23}
$$

**Kelemahan menurut Kingsley:** (a) LSB-2 ikut diubah → MSE naik → PSNR ≈ 48 dB; (b) kapasitas mentok 150%; (c) penyisipan serial → rawan *burst error* (satu goresan/crop merusak banyak bit dari codeword yang sama).

---

## 4. Metode Usulan Kingsley — Cara Kerjanya

### 4.1 Gambaran Umum

```
                               ┌──────────────┐
                               │ Agreed Image │
                               └──────┬───────┘
                                      ▼
Secret ─► Encoding ─► Generate ─KT─► Embed KT ────────────► Agreed Stego A'
image     RM(1,4)     Key Trace       into A
                         │ Em (1 bit/piksel)
                         ▼
Cover ──► BBS random ─► Embed Em ke LSB-1 ─► Share gen ─► Embed S2 ─► Stego I''
image     positions     (modulus, n=1)      (2,2)-VCS     (RM encoded)
                                               │
                                               ▼
                                     Share 1 (kanal aman)
```

Input: **Cover image** $CI$ ($H_1 \times W_1$), **Secret image** $SI$ ($H_0 \times W_0$), **Agreed image** $A$ ($H_2 \times W_2$, disepakati sebelumnya).
Output: **Stego image** $I''$, **Agreed stego** $A'$, **Share 1** $S_1$.

### 4.2 Definisi Kapasitas (Definisi 4.1)

Jika dipakai $p \le \tfrac{3}{4} H W$ piksel dan tiap LSB di-*re-embed* dengan $n$ bit tambahan:

$$
S_T = p \cdot (n + 1) \tag{25}
$$

$$
EC = \frac{S_T}{H \cdot W} = \frac{p\,(n+1)}{H \cdot W} \tag{26}
$$

**Contoh:** $H = W = 512$, $p = \tfrac34 \cdot 512^2 = 196\,608$, $n = 5$:

$$
S_T = 196\,608 \times 6 = 1\,179\,648 \text{ bit}, \qquad
EC = \frac{1\,179\,648}{262\,144} = 4.5 = 450\% \tag{27–28}
$$

### 4.3 Langkah 1 — Encoding Citra Rahasia

1. **Dekomposisi piksel → bit.** Tiap piksel 8 bit, total $Y = 8 \cdot H_0 \cdot W_0$ bit.
2. **Bagi menjadi blok** $k_2 = 5$ bit. Jumlah blok $n = \lceil Y / k_2 \rceil$; blok terakhir di-*padding* nol sebanyak

   $$ Z_n = n \cdot k_2 - Y $$

   > ⚠️ Pers. (29) di paper tertulis $Z_n = Y \bmod k_2$, tapi contoh di paper sendiri memakai $n k_2 - Y$ (13 bit → 15 − 13 = 2 bit padding). Yang benar adalah versi contoh.

   Contoh: `1010111100110` → `10101`, `11100`, `110`**`00`**.
3. **Encode tiap blok** dengan RM(1,4) → codeword 16 bit. Total bit ter-encode:

   $$ E_T = \frac{8 \cdot H_0 \cdot W_0 \cdot N_2}{k_2} = 3.2 \times Y $$

### 4.4 Langkah 2 — Key Trace (inti "Multiple Embedding")

Hanya dijalankan jika $E_T > \tfrac34 H_1 W_1$.

**Jumlah siklus per piksel (Teorema 4.1):**

$$
N_c = \frac{E_T}{\tfrac34 \cdot H_1 \cdot W_1} \tag{31}
$$

**Jika $N_c$ bukan bilangan bulat (Teorema 4.2)**, sebagian piksel menampung $\lceil N_c \rceil$ bit, sisanya $\lfloor N_c \rfloor$ bit:

$$
h = \frac{3 \cdot H_1 \cdot W_1 \cdot (N_c - \lfloor N_c \rfloor)}{4} \tag{32}
$$

$$
h' = \frac{3 \cdot H_1 \cdot W_1}{4} - h \tag{33}
$$

Bit ter-encode $eb$ dipotong menjadi $h$ blok $db$ berukuran $\lceil N_c\rceil$ dan $h'$ blok $db'$ berukuran $\lfloor N_c\rfloor$. **Satu blok = satu piksel cover.**

#### Algoritma 1 — Generate Key Trace & bit untuk cover

Diberikan blok $db = (db_1, \dots, db_{N_c})$ dan **Reference Key** $R \in \{0,1\}$, dibangun rantai XOR dari belakang:

$$
\begin{aligned}
CK_{N_c-1} &= db_{N_c} \oplus R \\
CK_{t-1} &= db_t \oplus CK_t, \qquad t = N_c-1, \dots, 2 \\
E &= db_1 \oplus CK_1
\end{aligned}
$$

- $E$ (**1 bit**) → disisipkan ke **LSB-1 piksel cover**.
- $CK_1, \dots, CK_{N_c-1}$ (**$N_c - 1$ bit**) → menjadi **Key Trace**, disimpan di **Agreed Image**.

Jika diuraikan, $E$ ternyata hanyalah **paritas seluruh blok** di-XOR dengan $R$:

$$
E = db_1 \oplus db_2 \oplus \dots \oplus db_{N_c} \oplus R
$$

> ⚠️ Pseudocode Algoritma 1 di paper tidak konsisten (baris 2 dan baris 8 sama-sama menulis $CK_{t-1}$ pada iterasi pertama, dan cabang `t == 1` tidak mengurangi `t` sehingga *loop* tidak berhenti). Rumus di atas adalah interpretasi yang konsisten dengan Algoritma 2 (ekstraksi), dan sudah saya uji *round-trip* pada 2000 blok acak — selalu kembali ke data asli.

**Contoh (Nc = 6, R = 0):**

| | $db_1$ | $db_2$ | $db_3$ | $db_4$ | $db_5$ | $db_6$ |
|---|---|---|---|---|---|---|
| Data blok | 1 | 0 | 1 | 1 | 0 | 1 |

$$
\begin{aligned}
CK_5 &= db_6 \oplus R = 1 \oplus 0 = 1 \\
CK_4 &= db_5 \oplus CK_5 = 0 \oplus 1 = 1 \\
CK_3 &= db_4 \oplus CK_4 = 1 \oplus 1 = 0 \\
CK_2 &= db_3 \oplus CK_3 = 1 \oplus 0 = 1 \\
CK_1 &= db_2 \oplus CK_2 = 0 \oplus 1 = 1 \\
E &= db_1 \oplus CK_1 = 1 \oplus 1 = \mathbf{0}
\end{aligned}
$$

→ Cover menerima **1 bit** (`0`); Agreed Image menerima Key Trace **`11011`** (5 bit).

**Total Key Trace:**

$$
|K_T| = h\,(\lceil N_c \rceil - 1) + h'\,(\lfloor N_c \rfloor - 1) = E_T - \tfrac34 H_1 W_1
$$

> Paper menulis Pers. (34) sebagai $|K_T| = h\lceil N_c\rceil + h' N_c$, yang tidak konsisten dengan kalimat "blok ukuran $n$ menghasilkan Key Trace ukuran $n-1$". Pada Bagian 7.2 paper sendiri memakai $K_T = \frac{|S| \cdot N}{k} - \frac34 H W$, yang sama dengan rumus di atas.

### 4.5 Langkah 3 — Posisi Piksel Acak (Blum Blum Shub)

BBS (CSPRNG) dengan **seed** $SE$ menghasilkan deret bit → dipotong per **18 bit** → dikonversi ke integer $1 \le pp_i \le H_1 W_1$ (18 bit cukup karena $2^{18} = 262\,144 = 512 \times 512$).

Panjang deret:

$$
L =
\begin{cases}
E_T, & 1 \le E_T \le \tfrac34 H_1 W_1 \\
|E_m|, & E_T > \tfrac34 H_1 W_1
\end{cases} \tag{35}
$$

Rumus BBS standar (dari referensi Junod, tidak ditulis eksplisit di paper): $x_{i+1} = x_i^2 \bmod M$, $M = p \cdot q$ dengan $p \equiv q \equiv 3 \pmod 4$, output = LSB dari $x_i$.

Tujuan: (a) keamanan — tanpa seed, posisi tidak diketahui; (b) **menyebar bit** sehingga kerusakan lokal (goresan/crop) tidak menumpuk di satu codeword → menghindari *burst error*.

### 4.6 Langkah 4 — Sisipkan ke Cover

Bit yang disisipkan:

$$
EB =
\begin{cases}
eb, & 1 \le E_T \le \tfrac34 H_1 W_1 \\
E_m, & E_T > \tfrac34 H_1 W_1
\end{cases} \tag{36}
$$

Untuk tiap $EB_i$ dan piksel $px$ di posisi $pp_i$: modulus function dengan $n = 1$ (Pers. 16–18). Hasil: stego $I'$.

### 4.7 Langkah 5 — Sisipkan Key Trace ke Agreed Image

Jumlah LSB per piksel yang diperlukan di Agreed Image:

$$
nn = \frac{|K_T|}{H_2 \times W_2} \tag{37}
$$

Jika $nn$ bukan bulat, sebagian piksel memakai $\lceil nn \rceil$ bit dan sisanya $\lfloor nn \rfloor$ bit. Penyisipan pakai modulus function dengan $n = \lceil nn \rceil$ atau $\lfloor nn \rfloor$. Hasil: $A'$.

### 4.8 Langkah 6 — Share dari Secret Key ((2,2) VCS)

1. Bentuk teks $Txt = SE \;\text{␣}\; N_c \;\text{␣}\; H_0 \;\text{␣}\; W_0$.
   Contoh: `262139 0.01 10 6`.
2. Tiap karakter di-*render* sebagai matriks biner $16 \times 14$ → digabung menjadi citra biner $T'$ (**Secret Key**).
3. (2,2) VCS memecah $T'$ menjadi **Share 1** $S_1$ dan **Share 2** $S_2$ (ukuran $mm \times 2nn$, *pixel expansion* 2).
4. $S_1$ dikirim ke penerima via kanal aman.

### 4.9 Langkah 7 — Sisipkan Share 2 ke Stego

$S_2$ di-*flatten*, dibagi blok, di-encode RM, lalu disisipkan ke LSB piksel stego $I'$ (modulus, $n=1$) mulai dari penanda posisi $q$:

$$
E_{TT} = \frac{n'' \cdot 2 \cdot m'' \cdot N_1}{k_1}
$$

Hasil akhir: **stego $I''$**.

---

## 5. Proses Ekstraksi

```
Stego I'' ─► ekstrak S2 (LSB dari posisi q) ─► RM decode ─┐
                                                           ├─► tumpuk S1+S2 ─► baca SE, Nc, H0, W0
Share 1 ───────────────────────────────────────────────────┘
SE ─► BBS ─► posisi pp ─► ambil LSB piksel stego ─► E'
Agreed stego A' ─► ekstrak LSB ─► Key Trace
E' + Key Trace + R ─► Algoritma 2 ─► bit ter-encode ─► RM(1,4) decode ─► susun jadi citra
```

1. **Rekonstruksi Key:** ekstrak $S_2$ dari $I''$ → decode RM → tumpuk (*stack*/OR) dengan $S_1$ → seed, $N_c$, $H_0$, $W_0$ terbaca secara visual.
2. **Regenerasi posisi:** BBS dengan seed yang sama.
3. **Ekstraksi LSB:** $E'_i = px'_{pp_i} \bmod 2$.
4. **Ekstraksi Key Trace** dari $A'$ (modulus, Pers. 19, dengan $n = \lceil ns \rceil$ / $\lfloor ns \rfloor$, $ns = |K_T| / (H_2 W_2)$).
5. **Algoritma 2 — rekonstruksi blok:** bentuk
   $$ kb = (E',\; CK_1,\; CK_2,\; \dots,\; CK_{N_c-1},\; R) $$
   lalu XOR tiap pasangan bertetangga:
   $$ db_j = kb_j \oplus kb_{j+1}, \qquad j = 1, \dots, N_c $$
   *Contoh lanjutan:* $kb = (0,1,1,0,1,1,0)$ → $db = (1,0,1,1,0,1)$ ✔
6. **Decode RM(1,4)** per 16 bit (majority logic) → blok 5 bit → gabungkan, buang padding.
7. **Rekonstruksi citra:** tiap 8 bit → 1 piksel (0–255) → matriks $H_0 \times W_0$.

---

## 6. Model Keamanan (3 Fase)

1. **Registrasi:** pengirim membuat $S_1, S_2$; $S_1$ dikirim via kanal aman; penerima membalas `"RECEIVED"`.
2. **Autentikasi:** penerima menumpuk share, membaca seed, mengirim $H_1 = \text{SHA-512}(\text{seed})$. Pengirim membandingkan dengan $H_2 = \text{SHA-512}(\text{seed miliknya})$.
3. **Pertukaran stego:** hanya jika autentikasi valid.

Asumsi penting: **Agreed Image $A$ sudah dipertukarkan sebelumnya lewat kanal aman.**

---

## 7. Evaluasi & Hasil

### 7.1 Metrik

$$
EC = \frac{|S|}{H \cdot W} \tag{38}
$$

$$
PSNR = 10 \log_{10} \frac{255^2}{MSE} \tag{39}
$$

$$
MSE = \frac{1}{H \cdot W} \sum_{i=1}^{H} \sum_{j=1}^{W} \left( I_{ij} - I'_{ij} \right)^2 \tag{40}
$$

Setup: 30 cover grayscale 512×512, 20 citra rahasia berbagai ukuran (kapasitas); 20 cover × 20 secret × 33 ukuran (robustness & steganalisis).

### 7.2 Kapasitas & PSNR (Tabel 1)

| Cover | Secret (bit) | EC Molaei | EC Usulan | PSNR Molaei | PSNR Usulan |
|---|---|---|---|---|---|
| Peppers | 480 | 0.37% | 0.59% | 75.58 | 62.64 |
| | 196 608 | 150% | 240% | 48.13 | 52.09 |
| | 368 640 | — | **450%** | — | **52.08** |
| Lena | 480 | 0.37% | 0.59% | 75.61 | 62.36 |
| | 196 608 | 150% | 240% | 48.12 | 52.03 |
| | 368 640 | — | **450%** | — | **52.04** |
| Baboon | 480 | 0.37% | 0.59% | 75.62 | 62.29 |
| | 196 608 | 150% | 240% | 48.10 | 52.02 |
| | 368 640 | — | **450%** | — | **52.01** |

**Mengapa PSNR usulan ≈ 52 dB dan stabil?** Maksimal $\tfrac34$ piksel diubah, masing-masing peluang berubah ≈ ½ dan besar perubahan 1:

$$
MSE \approx \tfrac34 \cdot \tfrac12 \cdot 1^2 = 0.375
\;\Rightarrow\;
PSNR \approx 10\log_{10}\frac{65025}{0.375} \approx 52.4 \text{ dB}
$$

Cocok dengan tabel. Berapa pun ukuran rahasianya, yang berubah di cover tetap hanya ≤ 196 608 LSB — sisanya pindah ke Agreed Image.

### 7.3 Robustness (Tabel 2–5, ringkas)

| Serangan | Temuan |
|---|---|
| Salt & pepper (density 0.05) | Usulan pulih sempurna (PSNR 100 dB) untuk secret kecil; Molaei 28 dB |
| Gaussian / Speckle / S&P berat | Secret kecil: keduanya gagal. Secret ≥ 368 640 bit: usulan pulih 100 dB |
| Cropping | Secret besar (368 640 bit): usulan pulih 100 dB; Molaei ≤ 16 dB |
| Scratch tunggal | Usulan umumnya pulih penuh (bit acak → tidak ada *burst error*) |
| Scratch majemuk | Usulan gagal untuk secret kecil, berhasil untuk secret besar; Molaei gagal |
| JPEG | Molaei gagal; usulan hanya berhasil penuh untuk secret besar |

**Pola kunci:** *makin besar secret, makin robust* — kebalikan dari intuisi umum. Penjelasannya ada di Bagian 8.

### 7.4 Kemampuan koreksi

$$
E_c = \frac{t}{N} = \frac{3}{16} = 18.75\% \quad \text{vs.} \quad \text{Molaei: } \tfrac18 = 12.5\%,\; \tfrac{3}{32} = 9.38\%
$$

### 7.5 Steganalisis — *Triples Analysis* (Ker, 2005)

Mengestimasi fraksi pesan $p$ ($0 \le p \le 0.5$) dari struktur *trace set* 3-tuple piksel:

$$
C_{m,n} = \{(s_1,s_2,s_3) : \lfloor s_2/2 \rfloor = \lfloor s_1/2 \rfloor + m,\; \lfloor s_3/2 \rfloor = \lfloor s_2/2 \rfloor + n\} \tag{41}
$$

$E_{m,n}$ / $O_{m,n}$ = subset dengan $m$ genap / ganjil (Pers. 42–43). Probabilitas transisi antar subset: $p^i (1-p)^{3-i}$. Estimasi subset cover: $\mathbf{x}'' = T_3^{-1}\mathbf{x}'$ (44). Galat simetri paritas:

$$
\epsilon_{m,n} = \tfrac18\big[(d_0{+}d_1{+}d_2{+}d_3) + q(3d_0{+}d_1{-}d_2{-}3d_3) + q^2(3d_0{-}d_1{-}d_2{+}3d_3) + q^3(d_0{-}d_1{+}d_2{-}d_3)\big] \tag{45}
$$

Minimisasi $S(q) = \sum_{m,n} \epsilon_{m,n}^2$ (polinom derajat 6, Pers. 46), lalu

$$
\hat p = \tfrac12\left(1 - \tfrac1q\right)
$$

Perbandingan memakai rasio

$$
P = \frac{E_p}{T_p} \tag{47}
$$

($E_p$ = estimasi, $T_p$ = nilai sebenarnya). $P$ kecil = detektor meleset = lebih aman.

| Secret (bit) | Molaei $T_p$ / $E_p$ | Usulan $T_p$ / $E_p$ |
|---|---|---|
| 15 360 | 0.0586 / 0.053 | 0.128 / 0.10 |
| 196 608 | 0.75 / 0.40–0.47 | 0.409 / 0.39 |
| 368 640 | — | 0.405 / 0.38 |

Klaim: Triples hanya "melihat" siklus terakhir di LSB, sehingga $E_p$ tertahan ≈ 0.3–0.4 walaupun payload riil naik → rasio $P$ turun cepat.

---

## 8. Analisis Kritis (penting untuk Bab 2 / *research gap*)

Poin-poin ini hasil pembacaan dan verifikasi saya sendiri, **tidak dinyatakan eksplisit** di paper.

1. **"Multiple embedding" sebenarnya adalah pemindahan payload ke carrier kedua.**
   Secara fisik, setiap piksel cover tetap hanya menyimpan **1 bit** ($E$ = paritas blok ⊕ R). Sisa $N_c - 1$ bit per piksel disimpan di **Agreed Image**. Contoh 450%: cover memuat 196 608 bit, Agreed Image 512×512 memuat 983 040 bit (**3.75 bit/piksel**!).

2. **Kapasitas dihitung terhadap ukuran cover saja.** $EC = S_T / (H_1 W_1)$ mengabaikan piksel Agreed Image. Jika dihitung terhadap total piksel kedua carrier (2 × 512²), kapasitas ter-encode = 225%.

3. **EC dihitung dari bit ter-encode (termasuk redundansi RM), bukan payload asli.** Verifikasi dari Tabel 1:
   - 368 640 bit × 16/5 = 1 179 648 → 450% ✔
   - 196 608 bit × 16/5 = 629 146 → 240% ✔; Molaei: 196 608 × 2 = 393 216 → 150% ✔

   Payload rahasia **murni** pada klaim 450% = 368 640 / 262 144 ≈ **1.41 bpp**. Sebagian "keunggulan 3×" berasal dari RM(1,4) yang lebih boros (ekspansi 3.2 vs 2).

4. **PSNR Agreed Image $A'$ tidak dilaporkan**, padahal di skenario 450% citra itu diubah 3–4 LSB per piksel (jauh lebih terdistorsi dari cover).

5. **Robustness sangat bergantung pada asumsi Key Trace "bebas serangan".** Karena $db_1 = E \oplus CK_1$ dan $db_j = CK_{j-1} \oplus CK_j$, satu bit error di cover hanya merusak **1 dari $N_c$ bit** blok. Makin besar secret → makin besar $N_c$ → makin kecil fraksi bit yang rentan. Inilah alasan "makin besar secret, makin robust". Jika $A'$ juga diserang, keunggulan ini hilang.

6. **Cover hanya grayscale**, piksel dipilih acak tanpa mempertimbangkan tekstur/tepi — tidak ada adaptivitas terhadap HVS.

7. **Beberapa inkonsistensi penulisan** (lihat kotak ⚠️ di atas): hasil contoh encoding RM, Pers. (29) padding, pseudocode Algoritma 1, Pers. (34), dan penyebutan "RM(5,2)" yang seharusnya RM(2,5).

### 8.1 Temuan dari Simulasi

Kode ada di `simulasi_kingsley_multiple_embedding/`, dan hasil lengkapnya di `hasil/hasil_simulasi.md`.

| Temuan | Angka simulasi |
|---|---|
| Kapasitas & PSNR cover sesuai Tabel 1 | 240% → 52.36–52.46 dB; 450% → 52.34–52.36 dB (paper: 52.0–52.1 dB) |
| Distorsi Agreed Image (tidak dilaporkan paper) | PSNR A' = **35.78 dB** pada kasus 450% (nn = 3.75 bit/piksel) |
| Secret 368 640 bit, skenario A (A' utuh) | **100 dB untuk 13/13 serangan**, termasuk crop 70%, Gaussian var 0.1, JPEG Q=75 |
| Secret yang sama, skenario B (A' ikut diserang) | 7.8–30 dB, tidak ada yang pulih penuh |
| Share 2 (kunci) di stego | Rusak pada semua serangan noise, JPEG, dan crop 0–512×0–360 |

**Mengapa 100 dB selalu tercapai pada 450%?** Ini jaminan struktural, bukan kebetulan. Dengan $N_c = 6$, hanya bit pertama tiap blok ($db_1 = E \oplus CK_1$) yang bergantung pada cover, sehingga hanya 1 dari 6 bit ter-encode yang rentan. Sebuah codeword 16 bit hanya bisa memuat paling banyak $\lceil 16/6 \rceil = 3$ bit rentan, dan RM(1,4) mengoreksi tepat $t = 3$ error. Jadi **serangan apa pun terhadap cover (bahkan menghapus seluruh cover) tetap terkoreksi sempurna**, selama A' dan kunci utuh. Artinya, robustness "100 dB" di paper lebih mencerminkan bahwa ~83% payload berada di carrier yang tidak diserang, bukan kekuatan kode koreksinya.

Pada 240% ($N_c = 3.2$, blok 3–4 bit) satu codeword bisa memuat hingga 5 bit rentan, sehingga robustness langsung turun (14–26 dB untuk noise/crop). Ini sesuai pola "makin besar secret, makin robust" yang dilaporkan paper.

---

## 9. Relevansi dengan Tesis MES (RGB, Parallel Embedding)

| Aspek | Kingsley (2020) | Tesis MES |
|---|---|---|
| Arti "multiple embedding" | *Re-embed* berurutan ke piksel yang sama via rantai XOR + carrier kedua | Penyisipan **paralel** ke 3 kanal R, G, B sebagai carrier independen |
| Carrier | Grayscale cover + Agreed Image | Satu citra RGB |
| Pemilihan piksel | Acak (BBS), ¾ piksel | Adaptif (tepi/tekstur, HVS) |
| Proteksi error | RM(1,4) | (sesuai desain MES) |
| Kanal tambahan | Share VCS + Agreed Image harus dikirim terpisah | Tidak perlu |

Posisi yang bisa diambil di Bab 2: Kingsley menaikkan kapasitas nominal dengan **menambah carrier eksternal** (Agreed Image) dan menghitung kapasitas terhadap cover saja; MES menaikkan kapasitas **di dalam satu citra** dengan memanfaatkan ketiga kanal warna secara paralel, sehingga perbandingan kapasitas perlu memakai definisi yang sama (payload murni per piksel carrier).

---

## 10. Sitasi (BibTeX)

```bibtex
@article{katandawa2020improving,
  author  = {Katandawa, Alex Kingsley and Barmawi, Ari Moesriami},
  title   = {Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding},
  journal = {Journal of Information Hiding and Multimedia Signal Processing},
  volume  = {11},
  number  = {1},
  pages   = {14--43},
  year    = {2020},
  issn    = {2073-4212}
}
```
