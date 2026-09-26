# Menyembunyikan Foto di Dalam Foto — Paper Kingsley (2020) untuk Pembaca Awam

> Versi ramah-awam dari *Improving Data Hiding Capacity in Code Based Steganography using Multiple Embedding* (Katandawa Alex Kingsley & Ari Moesriami Barmawi, JIHMSP 2020).
> Versi teknisnya ada di [`paper-kingsley-2020-multiple-embedding.md`](paper-kingsley-2020-multiple-embedding.md), dan kode simulasinya di [`../simulasi_kingsley_multiple_embedding/`](../simulasi_kingsley_multiple_embedding/).

---

## Cara Membaca Dokumen Ini

Semua rumus di sini **asli dari paper** (nomornya ditulis seperti "Rumus (16)"). Setiap rumus disajikan dalam urutan yang sama:

| Lapisan | Isinya | Boleh dilewati? |
|---|---|---|
| 🧠 **Bayangkan** | Analogi sehari-hari | Jangan, ini yang paling penting |
| 📐 **Rumus** | Rumus asli dari paper | Boleh, kalau hanya ingin paham idenya |
| 🔍 **Cara baca** | Arti setiap simbol dalam kalimat biasa | — |
| 🔢 **Contoh** | Dihitung pakai angka sungguhan | — |
| ✅ **Intinya** | Satu kalimat kesimpulan | Jangan |

Bagian yang dilipat (▶) berisi rumus lanjutan. Boleh dilewati tanpa kehilangan alur cerita.

---

## Kamus Simbol (baca sekali, pakai terus)

| Simbol | Dibaca | Artinya | Contoh |
|---|---|---|---|
| $a \bmod b$ | "a modulo b" | **Sisa** pembagian $a$ oleh $b$. Seperti jam dinding: pukul 14 = pukul 2 karena $14 \bmod 12 = 2$ | $17 \bmod 5 = 2$ |
| $\oplus$ | "XOR" | Bandingkan dua bit: **sama → 0, beda → 1**. Seperti saklar: angka 1 membalik keadaan | $1 \oplus 1 = 0$, $1 \oplus 0 = 1$ |
| $\lceil x \rceil$ | "ceiling x" | Bulatkan **ke atas** | $\lceil 3.2 \rceil = 4$ |
| $\lfloor x \rfloor$ | "floor x" | Bulatkan **ke bawah** | $\lfloor 3.2 \rfloor = 3$ |
| $\sum$ | "sigma" | **Jumlahkan** semuanya | $\sum_{i=1}^{3} i = 1+2+3 = 6$ |
| $\binom{m}{i}$ | "m pilih i" | Banyaknya cara memilih $i$ benda dari $m$ benda | $\binom{4}{1} = 4$ |
| $2^m$ | "2 pangkat m" | 2 dikali dirinya sendiri $m$ kali | $2^4 = 16$ |
| $H \times W$ | "H kali W" | Tinggi × lebar gambar = jumlah piksel | $512 \times 512 = 262\,144$ |
| $\in$ | "anggota" | "termasuk dalam" | $R \in \{0,1\}$: R bernilai 0 atau 1 |

---

## Bab 0 — Tiga Hal yang Perlu Diketahui tentang Gambar Digital

### 0.1 Gambar = kumpulan kotak kecil (piksel)

Foto hitam-putih adalah tabel angka. Setiap kotak (**piksel**) punya kecerahan **0 (hitam) sampai 255 (putih)**. Foto 512×512 berisi **262 144 piksel**.

### 0.2 Setiap angka disimpan sebagai 8 "saklar" (bit)

Komputer menyimpan angka dalam **biner**, yaitu deretan 0 dan 1. Satu piksel = 8 bit.

$$
150 = \underbrace{1}_{128}\;\underbrace{0}_{64}\;\underbrace{0}_{32}\;\underbrace{1}_{16}\;\underbrace{0}_{8}\;\underbrace{1}_{4}\;\underbrace{1}_{2}\;\underbrace{\mathbf{0}}_{1} \qquad (128+16+4+2 = 150)
$$

Bit paling kanan disebut **LSB (Least Significant Bit)**, bit yang "paling tidak berarti". Nilainya hanya 1.

### 0.3 Mengubah LSB tidak terlihat mata

Mengubah LSB piksel 150 menjadi 1 menghasilkan **151**. Perbedaan kecerahan 150 vs 151 **mustahil dilihat mata manusia**. Jadi setiap LSB bisa dipakai untuk menyimpan 1 bit rahasia. Inilah dasar **steganografi**: menyembunyikan pesan sehingga keberadaannya pun tidak disadari.

---

## Bab 1 — Ceritanya

**Ani** ingin mengirim **foto kucing** (192×240 piksel) kepada **Budi** tanpa ada yang tahu. Caranya: foto kucing disembunyikan di dalam **foto kameramen** (512×512) yang terlihat biasa saja.

Ani punya 4 alat:

| Alat | Analogi | Gunanya |
|---|---|---|
| 🛡️ **Kode Reed–Muller** | Mengeja "B untuk Bravo" di telepon yang berisik | Pesan tetap terbaca walau sebagian rusak |
| 🎲 **Posisi acak (Blum Blum Shub)** | Menyebar potongan surat ke halaman acak sebuah buku | Tanpa "kunci", tak ada yang tahu di mana pesannya |
| 🧵 **Key Trace** (inti paper) | Foto utama hanya menyimpan "ringkasan", sisanya dititipkan di **foto kedua** (foto bulan) yang sudah disepakati | Menampung pesan jauh lebih banyak |
| 🔑 **Kriptografi visual (2,2)** | Kunci dicetak lalu dipecah jadi 2 lembar transparansi berpola acak; baru terbaca kalau ditumpuk | Mengirim kunci dengan aman |

Alurnya:

```
Foto kucing ──► jadi bit ──► 🛡️ diberi pengaman ──► 🧵 diringkas ──┬─► ringkasan ─► 🎲 disebar di foto kameramen
                                                                   └─► sisa ─────► dititipkan di foto bulan
Kunci (seed, ukuran) ──► 🔑 dipecah 2 lembar ──► lembar 1: diberikan langsung ke Budi
                                             └─► lembar 2: diselipkan di foto kameramen
```

Budi membalik semua langkah ini untuk mendapatkan foto kucing kembali.

---

## Bab 2 — Langkah 1: Foto Kucing Diubah Jadi Deretan Bit

🧠 **Bayangkan:** membongkar lego menjadi keping-keping satuan agar bisa dimasukkan ke amplop.

📐 **Rumus** (Bagian 4.1.1):

$$
Y = 8 \times H_0 \times W_0
$$

🔍 **Cara baca:**
- $H_0, W_0$ = tinggi dan lebar foto rahasia
- $8$ = setiap piksel terdiri dari 8 bit
- $Y$ = jumlah bit rahasia total

🔢 **Contoh:** foto kucing 192×240 →
$$
Y = 8 \times 192 \times 240 = 368\,640 \text{ bit}
$$

✅ **Intinya:** foto kucing kini adalah deretan 368 640 angka 0/1.

---

## Bab 3 — Langkah 2: Memberi "Pengaman" dengan Kode Reed–Muller

### 3.1 Idenya

🧠 **Bayangkan:** Anda mengeja nama "BUDI" lewat telepon yang berisik. Kalau hanya bilang "B", bisa terdengar "D" atau "P". Maka Anda bilang **"Bravo–Uniform–Delta–India"**: lebih panjang, tapi walau ada suara yang putus, pendengar tetap bisa menebak dengan benar.

Kode Reed–Muller melakukan hal serupa: **setiap 5 bit pesan dipanjangkan menjadi 16 bit**. Tambahan 11 bit itu bukan asal, melainkan disusun sedemikian rupa sehingga **hingga 3 bit yang rusak bisa diperbaiki**.

### 3.2 Ukuran kode

📐 **Rumus (1)–(4):**

$$
k = \sum_{i=0}^{r} \binom{m}{i}
\qquad
N = 2^{m}
\qquad
d_{\min} = 2^{m-r}
\qquad
t = \left\lfloor \frac{2^{m-r} - 1}{2} \right\rfloor
$$

🔍 **Cara baca:**

| Simbol | Arti awam |
|---|---|
| $r, m$ | Dua "tombol pengatur" kode. Kingsley memakai $r = 1$, $m = 4$, ditulis **RM(1,4)** |
| $k$ | Berapa bit **pesan asli** per potong |
| $N$ | Berapa bit **setelah diberi pengaman** |
| $d_{\min}$ | Seberapa "berbeda" dua kode yang sah (makin besar, makin sulit tertukar) |
| $t$ | Berapa bit rusak yang **masih bisa diperbaiki** |

🔢 **Contoh RM(1,4):**

$$
k = \binom{4}{0} + \binom{4}{1} = 1 + 4 = 5
\qquad
N = 2^4 = 16
\qquad
d_{\min} = 2^{3} = 8
\qquad
t = \left\lfloor \tfrac{8-1}{2} \right\rfloor = \lfloor 3.5 \rfloor = 3
$$

✅ **Intinya:** setiap **5 bit** dipanjangkan menjadi **16 bit**, dan hingga **3 bit rusak** di antaranya bisa diperbaiki. Harganya: data membengkak **16 / 5 = 3.2 kali**.

<details>
<summary>▶ Kenapa $t$ = setengah dari $d_{\min}$? (opsional)</summary>

Bayangkan dua kode sah berjarak 8 langkah. Kalau ada 3 bit rusak, kode yang diterima masih lebih dekat (3 langkah) ke kode aslinya dibanding ke kode lain (≥ 5 langkah), jadi tebakan "yang terdekat" pasti benar. Kalau ada 4 bit rusak, jaraknya bisa seri 4–4, dan komputer tidak bisa memutuskan. Maka batas amannya $t = \lfloor (8-1)/2 \rfloor = 3$.

</details>

### 3.3 Cara memanjangkan pesan (encoding)

🧠 **Bayangkan:** ada 5 "stempel pola". Setiap bit pesan yang bernilai 1 berarti "pakai stempel ini". Semua stempel yang dipakai ditumpuk dengan XOR, dan hasilnya adalah kode 16 bit.

📐 **Rumus (6)–(7):** stempel-stempel itu disusun dalam **matriks generator** $G$:

$$
G_{1,4} =
\begin{bmatrix}
0000000011111111 \\
0000111100001111 \\
0011001100110011 \\
0101010101010101 \\
1111111111111111
\end{bmatrix}
\qquad
\mathbf{c} = \mathbf{u} \cdot G_{r,m}
$$

🔍 **Cara baca:**
- $\mathbf{u}$ = 5 bit pesan
- $G$ = 5 baris stempel pola
- $\mathbf{c}$ = kode 16 bit hasilnya
- Tanda "·" di sini berarti: ambil baris-baris $G$ yang posisinya bernilai 1 di $\mathbf{u}$, lalu XOR-kan semuanya

🔢 **Contoh:** pesan $\mathbf{u} = 1\,0\,1\,0\,1$ → pakai baris ke-1, ke-3, dan ke-5:

```
baris 1 :  0000000011111111
baris 3 :  0011001100110011
baris 5 :  1111111111111111
          ───────────────── XOR (sama→0, beda→1)
kode c  :  1100110000110011
```

✅ **Intinya:** pesan `10101` dikirim sebagai `1100110000110011`.

<details>
<summary>▶ Rumus (5)–(6): dari mana matriks G berasal? (opsional)</summary>

Paper membangun kode secara bertingkat, seperti boneka matryoshka: kode besar tersusun dari dua kode yang lebih kecil.

$$
RM(r,m) = \{ (\mathbf{u},\, \mathbf{u}+\mathbf{v}) : \mathbf{u} \in RM(r, m-1),\; \mathbf{v} \in RM(r-1, m-1) \}
$$

$$
G_{r,m} = \begin{bmatrix} G_{r,m-1} & G_{r,m-1} \\ \mathbf{0} & G_{r-1,m-1} \end{bmatrix}
$$

Artinya: separuh kiri kode adalah $\mathbf{u}$, separuh kanan adalah $\mathbf{u}$ ditambah $\mathbf{v}$. Pola setengah-setengah inilah yang membuat baris-baris $G$ terlihat seperti "blok 8, blok 4, blok 2, blok 1".

</details>

### 3.4 Cara memperbaiki kerusakan (decoding): pemungutan suara

🧠 **Bayangkan:** ada **8 saksi** untuk setiap bit pesan. Masing-masing saksi melihat pasangan bit yang berbeda di kode. Kalau ada bit yang rusak, paling banyak beberapa saksi yang "salah lihat". **Suara terbanyak menang.**

📐 **Rumus (persamaan saksi dari paper):**

$$
\begin{aligned}
u_1 &= c_1{+}c_2 = c_3{+}c_4 = c_5{+}c_6 = \dots = c_{15}{+}c_{16} \\
u_2 &= c_1{+}c_3 = c_2{+}c_4 = c_5{+}c_7 = \dots = c_{14}{+}c_{16} \\
u_3 &= c_1{+}c_5 = c_2{+}c_6 = c_3{+}c_7 = \dots = c_{12}{+}c_{16} \\
u_4 &= c_1{+}c_9 = c_2{+}c_{10} = c_3{+}c_{11} = \dots = c_8{+}c_{16}
\end{aligned}
$$

🔍 **Cara baca:** "$c_1 + c_9$" = XOR bit ke-1 dan bit ke-9. Kalau tidak ada kerusakan, **kedelapan saksi memberi jawaban yang sama**.

🔢 **Contoh dari paper:** Budi menerima `1110110010111011`. Dibanding kode asli `1100110000110011`, **3 bit rusak** (posisi 3, 9, 13). Hasil pemungutan suaranya:

| Bit | Jawaban 8 saksi | Suara "1" | Suara "0" | Keputusan |
|---|---|---|---|---|
| $u_4$ | 0 1 0 1 0 1 1 1 | 5 | 3 | **1** |
| $u_3$ | 0 0 1 0 0 0 0 0 | 1 | 7 | **0** |
| $u_2$ | 0 1 1 1 0 1 0 1 | 5 | 3 | **1** |
| $u_1$ | 0 1 0 0 1 0 1 0 | 3 | 5 | **0** |

Bit terakhir $u_0$ diputuskan dengan cara yang sama setelah pengaruh $u_1..u_4$ dihapus (Rumus 14), dan hasilnya **1**. Pesan terbaca: **`10101`**, benar walaupun 3 bit rusak.

✅ **Intinya:** dengan 3 bit rusak, saksi jujur (5) masih mengalahkan saksi yang tertipu (3). Kalau 4 bit rusak, hasilnya bisa seri 4–4 dan gagal. Karena itu batasnya $t = 3$.

<details>
<summary>▶ Rumus (8)–(15): versi umum pemungutan suara (opsional)</summary>

Tabel saksi di atas adalah kasus khusus RM(1,4). Paper juga menuliskan versi umum untuk RM(r,m) sembarang (dari buku Lin & Costello). Idenya tetap "cari kelompok saksi, lalu voting", hanya ditulis untuk semua ukuran.

**Kode ditulis sebagai jumlah pola (8):**
$$
\mathbf{c} = u_0\mathbf{v}_0 + \sum_{1\le i_1\le m} u_{i_1}\mathbf{v}_{i_1} + \sum_{1\le i_1 \le i_2\le m} u_{i_1 i_2}\mathbf{v}_{i_1}\mathbf{v}_{i_2} + \dots
$$
Artinya: kode = jumlah pola-pola dasar ($\mathbf{v}$) yang "dinyalakan" oleh bit pesan ($u$).

**Menentukan siapa saja saksinya (9)–(12):**
$$
S = \{a_{i_1-1}2^{i_1-1} + \dots + a_{i_{r-l}-1}2^{i_{r-l}-1} : a \in \{0,1\}\}
$$
$$
E = \{0,1,\dots,m-1\} \setminus \{i_1-1, \dots, i_{r-l}-1\}
$$
$$
S^c = \{d_{j_1}2^{j_1} + \dots + d_{j_{m-r+l}}2^{j_{m-r+l}} : d \in \{0,1\}\}
\qquad
B = q + S
$$
Artinya: $S$ = pola posisi dalam satu kelompok saksi, $S^c$ = titik awal setiap kelompok, $B$ = posisi-posisi bit yang dilihat oleh satu saksi. Untuk RM(1,4), inilah yang menghasilkan pasangan (1,9), (2,10), dst.

**Jawaban satu saksi (13):**
$$
A^{(l)} = \sum_{t\in B} x_t^{(l)}
$$
Saksi menjumlahkan (XOR) bit-bit di posisinya.

**Hapus pengaruh bit yang sudah diputuskan (14):**
$$
\mathbf{x}^{(l)} = \mathbf{x}^{(l-1)} - \sum u^*_{i_1\dots}\mathbf{v}_{i_1}\cdots
$$

**Ubah kode yang sudah bersih menjadi pesan (15):**
$$
\mathbf{u} = \mathbf{r}' \cdot G_{r,m}^{T}
$$

</details>

### 3.5 Memotong pesan menjadi potongan 5 bit

📐 **Rumus (Definisi 4.2):**

$$
n = \left\lceil \frac{Y}{k} \right\rceil
\qquad
Z_n = n \cdot k - Y
\qquad
E_T = n \cdot N
$$

🔍 **Cara baca:**
- $n$ = jumlah potongan (dibulatkan ke atas, karena potongan terakhir boleh tidak penuh)
- $Z_n$ = jumlah angka 0 "pengganjal" agar potongan terakhir genap 5 bit
- $E_T$ = total bit **setelah** diberi pengaman

🔢 **Contoh kecil dari paper:** 13 bit `1010111100110`

$$
n = \lceil 13/5 \rceil = \lceil 2.6 \rceil = 3
\qquad
Z_n = 3 \times 5 - 13 = 2
$$

→ `10101` · `11100` · `110`**`00`** (dua angka 0 pengganjal)

🔢 **Contoh foto kucing:**

$$
n = \frac{368\,640}{5} = 73\,728 \text{ potongan}
\qquad
E_T = 73\,728 \times 16 = 1\,179\,648 \text{ bit}
$$

✅ **Intinya:** setelah diberi pengaman, foto kucing membengkak dari 368 640 bit menjadi **1 179 648 bit**.

> ⚠️ Di paper, rumus pengganjal tertulis $Z_n = Y \bmod k$. Tapi contoh angka di paper sendiri memakai $n \cdot k - Y$ (hasilnya 2, bukan $13 \bmod 5 = 3$). Yang benar adalah versi contoh.

---

## Bab 4 — Langkah 3: Masalahnya, Muatannya Kebanyakan!

🧠 **Bayangkan:** Anda punya **1 179 648 kelereng** (bit), tapi hanya boleh memakai **196 608 kotak** (piksel). Aturannya, setiap kotak hanya boleh diubah sedikit (1 LSB).

Kenapa hanya 196 608 kotak? Kingsley sengaja memakai **¾ piksel saja** agar foto tetap mulus:

$$
P = \tfrac{3}{4} \times 512 \times 512 = 196\,608 \text{ piksel}
$$

### 4.1 Berapa kelereng per kotak?

📐 **Rumus (31):**

$$
N_c = \frac{E_T}{\tfrac{3}{4} \cdot H_1 \cdot W_1}
$$

🔍 **Cara baca:**
- $N_c$ ("number of cycles") = berapa bit yang harus "dijejalkan" ke setiap piksel
- $H_1 \times W_1$ = ukuran foto kameramen (cover)

🔢 **Contoh foto kucing:**
$$
N_c = \frac{1\,179\,648}{196\,608} = 6
$$
→ setiap piksel harus menanggung **6 bit**, padahal 1 LSB hanya muat 1 bit. Solusinya ada di Bab 5.

### 4.2 Kalau hasil baginya tidak bulat

🧠 **Bayangkan:** 10 kelereng dibagi ke 3 kotak = 3.33 per kotak. Tidak mungkin sepertiga kelereng, jadi 1 kotak dapat 4 dan 2 kotak dapat 3.

📐 **Rumus (32)–(33):**

$$
h = \frac{3 \cdot H_1 \cdot W_1 \cdot (N_c - \lfloor N_c \rfloor)}{4}
\qquad
h' = \frac{3 \cdot H_1 \cdot W_1}{4} - h
$$

🔍 **Cara baca:**
- $h$ = jumlah piksel yang kebagian $\lceil N_c \rceil$ bit (jatah dibulatkan ke atas)
- $h'$ = jumlah piksel sisanya, yang kebagian $\lfloor N_c \rfloor$ bit
- $(N_c - \lfloor N_c \rfloor)$ = bagian pecahannya saja (contoh: 3.2 → 0.2)

🔢 **Contoh foto kucing yang lebih kecil** (196 608 bit rahasia → $E_T$ = 629 152 bit):

$$
N_c = \frac{629\,152}{196\,608} \approx 3.2
\qquad
h = 39\,328 \text{ piksel dapat 4 bit}
\qquad
h' = 157\,280 \text{ piksel dapat 3 bit}
$$

Cek: $39\,328 \times 4 + 157\,280 \times 3 = 629\,152$ ✔

✅ **Intinya:** bit-bit dibagi rata ke setiap piksel. Kalau tidak bisa rata, sebagian piksel kebagian satu bit lebih banyak.

---

## Bab 5 — Langkah 4: Key Trace, Trik Utama Paper Ini 🧵

### 5.1 Idenya

🧠 **Bayangkan:** Anda harus menitipkan 6 digit PIN ke seseorang, tapi orang itu hanya bisa mengingat **1 digit**. Maka Anda berikan **1 "digit ringkasan"** kepada orang itu, sedangkan 5 digit lainnya (dalam bentuk tersandi) dicatat di **buku kedua** yang sudah Anda dan penerima sepakati. Penerima yang punya keduanya bisa menyusun ulang PIN lengkap.

Dalam paper ini:
- **"Orang yang ingat 1 digit"** = LSB piksel foto kameramen
- **"Buku kedua"** = **foto bulan** (*Agreed Image*) yang sudah disepakati Ani dan Budi sebelumnya
- **"Catatan tersandi"** = **Key Trace**

### 5.2 Cara membuat Key Trace (Algoritma 1)

🧠 **Bayangkan** barisan orang yang saling berbisik dari belakang ke depan. Orang paling belakang mulai dari angka rahasia $R$. Setiap orang menggabungkan (XOR) bit miliknya dengan bisikan dari belakang, lalu meneruskannya ke depan. Setiap bisikan dicatat di buku kedua (Key Trace). Hasil paling depan ($E$) dititipkan ke foto kameramen.

📐 **Rumus (Algoritma 1, ditulis rapi):**

$$
\begin{aligned}
CK_{N_c-1} &= db_{N_c} \oplus R \\
CK_{t-1} &= db_t \oplus CK_t \qquad \text{(mundur dari belakang)} \\
E &= db_1 \oplus CK_1
\end{aligned}
$$

🔍 **Cara baca:**
- $db_1, \dots, db_{N_c}$ = bit-bit milik **satu piksel** (dalam contoh ini 6 bit)
- $R$ = **Reference Key**, satu bit (0 atau 1) yang disepakati Ani dan Budi
- $CK$ = catatan bisikan → disimpan di **foto bulan** (Key Trace)
- $E$ = satu bit ringkasan → disimpan di **LSB foto kameramen**

🔢 **Contoh:** 6 bit untuk satu piksel = `1 0 1 1 0 1`, dengan $R = 0$:

| Langkah | Hitungan | Hasil |
|---|---|---|
| mulai | $CK_5 = db_6 \oplus R = 1 \oplus 0$ | 1 |
| | $CK_4 = db_5 \oplus CK_5 = 0 \oplus 1$ | 1 |
| | $CK_3 = db_4 \oplus CK_4 = 1 \oplus 1$ | 0 |
| | $CK_2 = db_3 \oplus CK_3 = 1 \oplus 0$ | 1 |
| | $CK_1 = db_2 \oplus CK_2 = 0 \oplus 1$ | 1 |
| selesai | $E = db_1 \oplus CK_1 = 1 \oplus 1$ | **0** |

→ Foto kameramen menerima **1 bit**: `0`
→ Foto bulan menerima **5 bit** Key Trace: `1 1 0 1 1`

✅ **Intinya:** dari 6 bit, hanya **1 bit** yang masuk ke foto utama. **5 bit sisanya** pindah ke foto kedua.

> 💡 **Rahasia kecil:** kalau diuraikan, $E$ ternyata hanya "ganjil atau genap"-nya jumlah angka 1 dalam blok itu:
> $$E = db_1 \oplus db_2 \oplus \dots \oplus db_{N_c} \oplus R$$
> Contoh: `101101` punya empat angka 1 (genap) → $E = 0$ ✔

### 5.3 Cara Budi menyusun ulang (Algoritma 2)

🧠 **Bayangkan:** Budi menjajarkan semua catatan dalam satu baris, lalu membandingkan **setiap dua tetangga**. Kalau keduanya sama, hasilnya 0; kalau beda, hasilnya 1.

📐 **Rumus:**

$$
kb = (E,\; CK_1,\; CK_2,\; \dots,\; CK_{N_c-1},\; R)
\qquad
db_j = kb_j \oplus kb_{j+1}
$$

🔢 **Contoh lanjutan:**

```
kb       :  0   1   1   0   1   1   0      ← (E, CK1..CK5, R)
            └─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘└─┬─┘
db       :    1   0   1   1   0   1        ← kembali utuh! ✔
```

✅ **Intinya:** bit asli didapat kembali dengan membandingkan setiap pasangan catatan yang bertetangga.

### 5.4 Total catatan di foto bulan

📐 **Rumus** (Rumus 34, versi yang sudah dikoreksi):

$$
|K_T| = h\,(\lceil N_c \rceil - 1) + h'\,(\lfloor N_c \rfloor - 1) = E_T - \tfrac34 H_1 W_1
$$

🔍 **Cara baca:** setiap piksel "menitipkan" semua bitnya **kecuali satu** ke foto bulan. Jadi total titipan = semua bit dikurangi jumlah piksel yang dipakai.

🔢 **Contoh foto kucing:**
$$
|K_T| = 1\,179\,648 - 196\,608 = 983\,040 \text{ bit}
$$

> ⚠️ Di paper tertulis $|K_T| = h\lceil N_c\rceil + h' N_c$ (tanpa "− 1"). Itu bertentangan dengan penjelasan paper sendiri bahwa "blok ukuran n menghasilkan Key Trace ukuran n − 1".

---

## Bab 6 — Langkah 5: Memilih Piksel Secara Acak 🎲

🧠 **Bayangkan:** kalau Ani menaruh bit rahasia berurutan dari pojok kiri atas, penyerang tinggal membaca dari pojok. Selain itu, kalau foto tergores di satu area, banyak bit dari **potongan kode yang sama** rusak bersamaan. Jadi Ani mengacak urutannya dengan mesin pengocok yang hanya bisa diulang oleh orang yang tahu **angka awal (seed)**.

📐 **Rumus Blum Blum Shub** (rumus standar dari referensi paper [13]; paper tidak menuliskannya secara eksplisit):

$$
x_{i+1} = x_i^{2} \bmod M, \qquad M = p \times q
$$

🔍 **Cara baca:**
- $p, q$ = dua bilangan prima rahasia (keduanya bersisa 3 bila dibagi 4)
- $x_0$ = dihitung dari **seed**
- Setiap langkah: kuadratkan, lalu ambil sisa bagi $M$
- Dari setiap $x$ diambil **bit terakhirnya** (ganjil = 1, genap = 0)
- Setiap 18 bit digabung menjadi satu nomor piksel ($2^{18} = 262\,144$ = jumlah piksel 512×512)

🔢 **Contoh mainan** ($p = 7$, $q = 11$, $M = 77$, seed $= 3$ → $x_0 = 3^2 = 9$):

| $i$ | Hitungan | $x_i$ | Ganjil/genap → bit |
|---|---|---|---|
| 1 | $9^2 = 81$, sisa bagi 77 | 4 | 0 |
| 2 | $4^2 = 16$ | 16 | 0 |
| 3 | $16^2 = 256$, sisa bagi 77 | 25 | 1 |
| 4 | $25^2 = 625$, sisa bagi 77 | 9 | 1 |

→ bit acak: `0 0 1 1 …` (di praktiknya $p$ dan $q$ sangat besar, sehingga polanya tidak cepat berulang)

📐 **Rumus (35)** — berapa piksel yang perlu dipilih:

$$
L =
\begin{cases}
E_T, & \text{jika } E_T \le \tfrac34 H_1 W_1 \quad \text{(muatan sedikit: 1 bit per piksel cukup)} \\
|E_m|, & \text{jika } E_T > \tfrac34 H_1 W_1 \quad \text{(muatan banyak: 1 piksel per blok Key Trace)}
\end{cases}
$$

✅ **Intinya:** tanpa seed, lokasi bit rahasia tidak bisa ditebak, dan kerusakan lokal (goresan) tersebar ke banyak potongan kode sehingga bisa diperbaiki.

---

## Bab 7 — Langkah 6: Menyelipkan Bit ke Piksel dengan Perubahan Sekecil Mungkin

🧠 **Bayangkan:** Anda ingin jarum jam menunjuk angka "genap". Kalau sekarang pukul 7, Anda bisa memutarnya ke 6 atau ke 8. Keduanya hanya 1 langkah, tidak perlu memutar jauh. **Fungsi modulus** memilih putaran terpendek.

### 7.1 Hitung selisih

📐 **Rumus (16):**

$$
dd_i = z_i - (x_i \bmod 2^n)
$$

🔍 **Cara baca:**
- $x_i$ = nilai piksel sekarang (0–255)
- $n$ = berapa bit terakhir yang dipakai (untuk foto kameramen $n = 1$)
- $x_i \bmod 2^n$ = nilai bit-bit terakhir piksel saat ini
- $z_i$ = nilai rahasia yang ingin diselipkan
- $dd_i$ = "harus bergeser berapa"

### 7.2 Pilih arah geser terpendek

📐 **Rumus (17):**

$$
dd_i' =
\begin{cases}
dd_i, & -\left\lfloor \frac{2^n-1}{2} \right\rfloor \le dd_i \le \left\lceil \frac{2^n-1}{2} \right\rceil \quad \text{(sudah dekat, pakai apa adanya)} \\[4pt]
dd_i + 2^n, & dd_i \text{ terlalu negatif} \quad \text{(lebih dekat kalau memutar ke atas)} \\[4pt]
dd_i - 2^n, & dd_i \text{ terlalu positif} \quad \text{(lebih dekat kalau memutar ke bawah)}
\end{cases}
$$

### 7.3 Jaga agar tetap di rentang 0–255

📐 **Rumus (18):**

$$
x_i' =
\begin{cases}
x_i + dd_i', & \text{jika hasilnya tetap di } 0..255 \\
x_i + dd_i' + 2^n, & \text{jika hasilnya di bawah } 0 \\
x_i + dd_i' - 2^n, & \text{jika hasilnya di atas } 255
\end{cases}
$$

### 7.4 Membaca kembali

📐 **Rumus (19):**

$$
z_i = x_i' \bmod 2^n
$$

🔢 **Contoh** (semuanya sudah diuji di simulasi):

| Piksel $x$ | Mau selipkan $z$ | $n$ | $dd$ (16) | $dd'$ (17) | Hasil $x'$ (18) | Cek $x' \bmod 2^n$ (19) |
|---|---|---|---|---|---|---|
| 150 | 1 | 1 | $1 - 0 = 1$ | 1 | **151** | $151 \bmod 2 = 1$ ✔ |
| 151 | 0 | 1 | $0 - 1 = -1$ | $-1 + 2 = 1$ | **152** | $152 \bmod 2 = 0$ ✔ |
| 150 | 0 | 1 | $0 - 0 = 0$ | 0 | **150** (tidak berubah) | $150 \bmod 2 = 0$ ✔ |
| 255 | 0 | 1 | $-1$ | $+1$ → 256 (kelebihan!) | $256 - 2 =$ **254** | $254 \bmod 2 = 0$ ✔ |
| 100 | 3 | 2 | $3 - 0 = 3$ | $3 - 4 = -1$ | **99** | $99 \bmod 4 = 3$ ✔ |

Baris terakhir menunjukkan kepintaran fungsi ini. Cara naif adalah menambah 3 (100 → 103). Fungsi modulus menemukan bahwa **mundur 1 (100 → 99)** memberi hasil yang sama dengan perubahan jauh lebih kecil.

✅ **Intinya:** setiap piksel foto kameramen berubah **paling banyak ±1**, dan kira-kira separuh piksel bahkan tidak berubah sama sekali (karena bitnya kebetulan sudah cocok).

---

## Bab 8 — Langkah 7: Menitipkan Key Trace ke Foto Bulan

📐 **Rumus (37):**

$$
nn = \frac{|K_T|}{H_2 \times W_2}
$$

🔍 **Cara baca:**
- $H_2 \times W_2$ = ukuran foto bulan
- $nn$ = berapa bit yang harus dititipkan di **setiap piksel foto bulan**

🔢 **Contoh foto kucing:**
$$
nn = \frac{983\,040}{512 \times 512} = 3.75 \text{ bit per piksel}
$$

→ 196 608 piksel dititipi **4 bit**, 65 536 piksel dititipi **3 bit**. Cek: $196\,608 \times 4 + 65\,536 \times 3 = 983\,040$ ✔

Penyelipan memakai fungsi modulus yang sama (Bab 7), dengan $n = 4$ atau $n = 3$.

✅ **Intinya:** foto kameramen hanya berubah di 1 bit terakhir, tetapi **foto bulan dijejali 3–4 bit terakhir** di setiap piksel.

---

## Bab 9 — Langkah 8: Mengirim Kunci dengan Dua Lembar Transparansi 🔑

🧠 **Bayangkan:** Ani menulis kunci (seed, jumlah siklus, ukuran foto kucing) di selembar kertas, lalu memecahnya menjadi **dua lembar plastik transparan** berbintik acak. Setiap lembar sendirian hanya terlihat seperti bintik-bintik tak bermakna. Kalau **ditumpuk**, tulisannya muncul.

📐 **Aturan (2,2) Visual Cryptography:** setiap titik kunci dipecah menjadi 2 sub-titik di masing-masing lembar:

| Titik kunci | Lembar 1 | Lembar 2 | Setelah ditumpuk |
|---|---|---|---|
| ⬜ putih | ⬛⬜ | ⬛⬜ (**sama**) | ⬛⬜ → setengah gelap = "putih" |
| ⬛ hitam | ⬛⬜ | ⬜⬛ (**kebalikan**) | ⬛⬛ → gelap penuh = "hitam" |

(Pola di Lembar 1 dipilih acak: ⬛⬜ atau ⬜⬛. Karena itu satu lembar saja tidak membocorkan apa pun.)

Contoh isi kunci di paper: `262139 0.01 10 6` → seed = 262139, $N_c$ = 0.01, tinggi = 10, lebar = 6.

- **Lembar 1** → diberikan langsung ke Budi lewat jalur aman.
- **Lembar 2** → diberi pengaman Reed–Muller, lalu diselipkan di foto kameramen.

Budi juga dicek keasliannya: Budi mengirim **sidik jari (hash SHA-512)** dari seed yang dibacanya, dan Ani mencocokkannya.

✅ **Intinya:** kunci tidak pernah dikirim utuh. Yang lewat jalur umum hanya separuhnya.

---

## Bab 10 — Seberapa Banyak yang Bisa Disembunyikan?

📐 **Rumus (25)–(26):**

$$
S_T = p \cdot (n + 1)
\qquad
EC = \frac{S_T}{H \times W} = \frac{p \cdot (n+1)}{H \times W}
$$

🔍 **Cara baca:**
- $p$ = jumlah piksel yang dipakai (¾ dari foto)
- $n$ = berapa kali bit **ditumpuk ulang** di piksel yang sama
- $n + 1$ = total bit per piksel (1 bit pertama + $n$ bit tumpukan)
- $S_T$ = total bit yang tersimpan
- $EC$ (*Embedding Capacity*) = rata-rata bit per piksel, ditulis sebagai persen

🔢 **Contoh dari paper:**
$$
S_T = 196\,608 \times (5 + 1) = 1\,179\,648 \text{ bit}
\qquad
EC = \frac{1\,179\,648}{262\,144} = 4.5 = \mathbf{450\%}
$$

🧠 **Arti 450%:** rata-rata **4.5 bit per piksel**. Pembanding (metode Molaei) hanya 150% = 1.5 bit per piksel.

✅ **Intinya:** kapasitas naik 3× lipat… tapi baca dulu Bab 13 sebelum terkesan. 😉

---

## Bab 11 — Mengukur "Apakah Kelihatan?": MSE dan PSNR

### 11.1 MSE: rata-rata kerusakan

🧠 **Bayangkan:** Anda membandingkan foto asli dan foto yang sudah disisipi, piksel demi piksel. Hitung selisihnya, kuadratkan (supaya minus tidak saling menghapus), lalu rata-ratakan.

📐 **Rumus (40):**

$$
MSE = \frac{1}{H \times W} \sum_{i=1}^{H} \sum_{j=1}^{W} \left( I_{ij} - I'_{ij} \right)^2
$$

🔍 **Cara baca:**
- $I_{ij}$ = piksel foto asli di baris $i$, kolom $j$
- $I'_{ij}$ = piksel foto setelah disisipi
- $\sum\sum$ = jumlahkan untuk semua piksel
- $\frac{1}{H \times W}$ = bagi dengan jumlah piksel → rata-rata

### 11.2 PSNR: skor kemiripan dalam desibel

📐 **Rumus (39):**

$$
PSNR = 10 \log_{10} \frac{255^2}{MSE}
$$

🔍 **Cara baca:** membandingkan "sinyal terkuat yang mungkin" ($255^2$) dengan "kerusakan" (MSE). **Makin tinggi PSNR, makin mirip.** Patokan kasar:

| PSNR | Artinya |
|---|---|
| < 30 dB | Perbedaan mulai terlihat |
| 30–40 dB | Bagus |
| > 40 dB | Mata manusia praktis tidak bisa membedakan |
| 100 dB | Konvensi paper untuk **identik sempurna** |

🔢 **Contoh mini** (foto 2×2 piksel):

$$
\text{Asli} = \begin{bmatrix} 100 & 150 \\ 200 & 50 \end{bmatrix}
\quad
\text{Stego} = \begin{bmatrix} 101 & 150 \\ 199 & 50 \end{bmatrix}
$$

$$
MSE = \frac{(100-101)^2 + 0 + (200-199)^2 + 0}{4} = \frac{2}{4} = 0.5
\qquad
PSNR = 10 \log_{10} \frac{65\,025}{0.5} \approx 51.1 \text{ dB}
$$

🔢 **Kenapa paper selalu dapat ≈ 52 dB?** Hanya ¾ piksel yang dipakai, separuhnya berubah, dan setiap perubahan hanya 1:

$$
MSE \approx \tfrac34 \times \tfrac12 \times 1^2 = 0.375
\qquad
PSNR \approx 10 \log_{10} \frac{65\,025}{0.375} \approx 52.4 \text{ dB}
$$

Paper melaporkan 52.0–52.1 dB, dan simulasi kita mendapat 52.34 dB. Cocok.

✅ **Intinya:** foto kameramen yang sudah disisipi tidak bisa dibedakan dari aslinya oleh mata manusia.

---

## Bab 12 — Bisakah Detektor Menemukannya? (Steganalisis)

🧠 **Bayangkan:** detektif yang tidak tahu isi pesan, tetapi bisa **mengukur kejanggalan statistik** di foto. Contohnya, di foto alami pasangan piksel tetangga punya pola tertentu, dan menyisipkan LSB merusak pola itu. Detektif bernama **Triples** (Ker, 2005) memeriksa kelompok **3 piksel bertetangga** untuk menebak berapa banyak isi rahasianya.

📐 **Rumus (47)** — cara paper menilai hasil detektif:

$$
P = \frac{E_p}{T_p}
$$

🔍 **Cara baca:**
- $T_p$ = porsi pesan yang **sebenarnya**
- $E_p$ = porsi pesan **tebakan detektif**
- $P$ mendekati 1 = tebakan detektif jitu (buruk bagi Ani)
- $P$ jauh di bawah 1 = detektif meleset (baik bagi Ani)

🔢 **Contoh dari Tabel 6 paper:**

| Secret | Molaei | Kingsley | Lebih sulit dideteksi |
|---|---|---|---|
| 15 360 bit | $P = 0.053 / 0.059 = 0.91$ | $P = 0.101 / 0.128 = 0.79$ | Kingsley |
| 196 608 bit | $P = 0.47 / 0.75 = 0.63$ | $P = 0.396 / 0.409 = 0.97$ | Molaei |

Hasilnya campuran: pada secret kecil Kingsley lebih sulit dideteksi, tetapi pada 196 608 bit tebakan detektif terhadap Kingsley justru lebih jitu. Paper berargumen bahwa untuk muatan yang lebih besar, tebakan detektif "mentok" di sekitar 0.3–0.4 karena detektif hanya melihat lapisan terakhir, sehingga rasio $P$ turun cepat.

<details>
<summary>▶ Rumus (41)–(46): cara kerja detektif Triples (opsional)</summary>

**Kelompokkan 3 piksel bertetangga (41):**
$$
C_{m,n} = \left\{(s_1,s_2,s_3) : \left\lfloor \tfrac{s_2}{2} \right\rfloor = \left\lfloor \tfrac{s_1}{2} \right\rfloor + m,\; \left\lfloor \tfrac{s_3}{2} \right\rfloor = \left\lfloor \tfrac{s_2}{2} \right\rfloor + n \right\}
$$
Artinya: kelompokkan trio piksel berdasarkan selisih nilainya **setelah LSB dibuang** ($\lfloor s/2 \rfloor$). Bagian ini tidak disentuh penyisipan LSB, jadi menjadi "patokan tetap".

**Pecah lagi berdasarkan ganjil/genap (42)–(43):**
$$
E_{m,n}: \; s_2 = s_1 + m,\; s_3 = s_2 + n,\; m \text{ genap}
\qquad
O_{m,n}: \; \text{sama, } m \text{ ganjil}
$$
Di foto alami, jumlah trio "genap" dan "ganjil" nyaris seimbang (**simetri paritas**). Penyisipan LSB merusak keseimbangan ini.

**Peluang sebuah trio berpindah kelompok:** $p^i(1-p)^{3-i}$, dengan $i$ = berapa piksel dari trio itu yang LSB-nya berubah.

**Tebak kondisi foto asli (44):**
$$
\mathbf{x}'' = T_3^{-1}\,\mathbf{x}'
$$
Artinya: "putar balik" efek penyisipan dengan matriks transisi $T_3$.

**Ukur seberapa tidak seimbang (45):**
$$
\epsilon_{m,n} = \tfrac18\big[(d_0{+}d_1{+}d_2{+}d_3) + q(3d_0{+}d_1{-}d_2{-}3d_3) + q^2(3d_0{-}d_1{-}d_2{+}3d_3) + q^3(d_0{-}d_1{+}d_2{-}d_3)\big]
$$

**Cari tebakan yang membuat foto paling seimbang (46):**
$$
S(q) = \sum_{m,n} \epsilon_{m,n}^2
\qquad\Rightarrow\qquad
\hat p = \tfrac12\left(1 - \tfrac1q\right)
$$
Artinya: coba semua kemungkinan $q$, pilih yang membuat total ketidakseimbangan paling kecil, lalu ubah menjadi tebakan porsi pesan $\hat p$.

</details>

✅ **Intinya:** detektor tetap bisa mendeteksi **adanya** pesan, tetapi pada muatan besar tebakan **jumlah** pesannya makin meleset.

---

## Bab 13 — Jadi, Seberapa Hebat Sebenarnya? (Catatan Kritis)

Setelah memahami semua langkahnya, ada beberapa hal yang tidak ditonjolkan paper:

### 13.1 "450%" itu kebanyakan disimpan di foto kedua

Dari setiap 6 bit, **hanya 1 bit** yang masuk ke foto kameramen. **5 bit sisanya** masuk ke foto bulan. Tetapi rumus kapasitas (26) hanya membagi dengan ukuran foto kameramen:

$$
EC_{\text{paper}} = \frac{1\,179\,648}{262\,144} = 450\%
\qquad\text{vs.}\qquad
EC_{\text{2 foto}} = \frac{1\,179\,648}{262\,144 + 262\,144} = 225\%
$$

### 13.2 "450%" masih termasuk "pengaman"

Ingat, Reed–Muller membengkakkan data 3.2 kali. Isi foto kucing yang **sebenarnya** hanya:

$$
\frac{368\,640}{262\,144} \approx 1.41 \text{ bit per piksel}
$$

### 13.3 Foto bulan cukup rusak, tapi tidak dilaporkan

Simulasi kita mengukur foto bulan setelah dititipi 3.75 bit per piksel: **PSNR 35.78 dB**, jauh di bawah foto kameramen (52 dB).

### 13.4 Ketahanan "100 dB" dijamin oleh strukturnya

🧠 **Bayangkan:** dari setiap potongan kode 16 bit, hanya **paling banyak 3 bit** yang tersimpan di foto kameramen, karena hanya 1 dari setiap 6 bit yang masuk ke sana:

$$
\left\lceil \frac{16}{6} \right\rceil = 3 \;\le\; t = 3
$$

Jadi **serangan seberat apa pun** pada foto kameramen (asalkan Budi sudah memegang kunci) hanya bisa merusak paling banyak 3 bit per potongan, dan itu pas dengan batas yang bisa diperbaiki Reed–Muller. Simulasi membuktikannya: 13 dari 13 serangan pulih sempurna.

Tetapi kalau **foto bulan ikut diserang**, hasilnya anjlok ke **7.8–30 dB**. Keunggulan itu datang dari asumsi bahwa foto kedua selalu aman.

### 13.5 Ringkasan

| Klaim paper | Kenyataannya |
|---|---|
| Kapasitas 450% | Benar, **kalau** hanya dihitung terhadap foto utama dan termasuk bit pengaman |
| PSNR ≥ 51 dB | Benar untuk foto utama; foto kedua ≈ 36 dB |
| Tahan semua serangan (secret besar) | Benar, **selama** foto kedua dan kunci tidak ikut diserang |

---

## Ringkasan Satu Halaman

| # | Langkah | Rumus kunci | Dalam satu kalimat |
|---|---|---|---|
| 1 | Foto → bit | $Y = 8 H_0 W_0$ | Setiap piksel jadi 8 bit |
| 2 | Pengaman | $k=5,\ N=16,\ t=3$; $\mathbf{c} = \mathbf{u}G$ | 5 bit dipanjangkan jadi 16, tahan 3 kerusakan |
| 3 | Bagi rata | $N_c = E_T / (\tfrac34 H_1W_1)$ | Berapa bit per piksel |
| 4 | Key Trace | $E = db_1 \oplus \dots \oplus db_{N_c} \oplus R$ | 1 bit ke foto utama, sisanya ke foto kedua |
| 5 | Acak lokasi | $x_{i+1} = x_i^2 \bmod M$ | Lokasi hanya diketahui pemegang seed |
| 6 | Selipkan | $dd = z - (x \bmod 2^n)$ | Geser piksel sesedikit mungkin |
| 7 | Foto kedua | $nn = \lvert K_T \rvert / (H_2W_2)$ | 3–4 bit per piksel foto bulan |
| 8 | Kunci | (2,2) VCS | Kunci dipecah 2 lembar transparansi |
| 9 | Ukur | $EC = S_T/(HW)$; $PSNR = 10\log_{10}(255^2/MSE)$ | 450% dan 52 dB |
