"""
Reproduces the experiments of Katandawa & Barmawi (2020):
  1. Capacity and imperceptibility (Table 1)
  2. Robustness against attacks (Tables 2-5), under two scenarios:
       A. the paper's assumption: only the stego is attacked, Key Trace (A') is safe
       B. the same attack also hits the agreed stego A'
  3. Whether Share 2 (the key) survives each attack

Outputs are written to ./hasil/.
"""
import os
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from skimage import data

import kingsley_stego as ks
from attacks import attack_suite

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "hasil")
SEED = 262139          # BBS seed used in the paper's key example
R = 0                  # reference key
SIZE = 512

# (H0, W0) -> secret bits: 480, 15 360, 196 608, 368 640 (sizes used in the paper)
SECRET_SHAPES = [(10, 6), (40, 48), (128, 192), (192, 240)]


def gray(img, shape):
    pil = Image.fromarray(img)
    if pil.mode != "L":
        pil = pil.convert("L")
    return np.array(pil.resize((shape[1], shape[0]), Image.BICUBIC))


def load_images():
    covers = {
        "Camera": gray(data.camera(), (SIZE, SIZE)),
        "Astronaut": gray(data.astronaut(), (SIZE, SIZE)),
        "Coffee": gray(data.coffee(), (SIZE, SIZE)),
    }
    agreed = gray(data.moon(), (SIZE, SIZE))
    secret_src = data.chelsea()
    return covers, agreed, secret_src


def fmt_bits(n):
    return f"{n:,}".replace(",", " ")


def experiment_capacity(covers, agreed, secret_src, rng):
    rows = []
    for cname, cover in covers.items():
        for shape in SECRET_SHAPES:
            secret = gray(secret_src, shape)
            t0 = time.time()
            stego, agreed_stego, s1, info = ks.embed(cover, secret, agreed, SEED, R, rng=rng)
            recovered, _ = ks.extract(stego, agreed_stego, s1, R)
            rows.append({
                "cover": cname, "bits": info["secret_bits"], "info": info,
                "psnr_stego": ks.psnr(cover, stego),
                "psnr_agreed": ks.psnr(agreed, agreed_stego),
                "ok": np.array_equal(recovered, secret),
                "sec": time.time() - t0,
            })
            print(f"  {cname:9s} {fmt_bits(info['secret_bits']):>9s} bit  "
                  f"EC={info['EC_paper'] * 100:6.2f}%  PSNR={rows[-1]['psnr_stego']:.2f} dB  "
                  f"recovered={'OK' if rows[-1]['ok'] else 'FAIL'}  ({rows[-1]['sec']:.1f}s)")
    return rows


def experiment_robustness(cover, agreed, secret_src, rng):
    results = []
    for shape in SECRET_SHAPES[1:]:
        secret = gray(secret_src, shape)
        stego, agreed_stego, s1, info = ks.embed(cover, secret, agreed, SEED, R, rng=rng)
        true_key = ks.recover_key(stego, s1)
        for label, attack in attack_suite():
            attacked = attack(stego, np.random.default_rng(7))
            try:
                key_ok = ks.recover_key(attacked, s1)["text"] == true_key["text"]
            except ks.KeyRecoveryError:
                key_ok = False

            # Key is taken as known so the secret channel is measured on its own.
            rec_a, _ = ks.extract(attacked, agreed_stego, s1, R, key=true_key)
            attacked_agreed = attack(agreed_stego, np.random.default_rng(8))
            rec_b, _ = ks.extract(attacked, attacked_agreed, s1, R, key=true_key)
            results.append({
                "bits": info["secret_bits"], "Nc": info["Nc"], "attack": label,
                "psnr_attacked": ks.psnr(stego, attacked, cap=np.inf),
                "psnr_a": ks.psnr(secret, rec_a), "ber_a": ks.bit_error_rate(secret, rec_a),
                "psnr_b": ks.psnr(secret, rec_b), "ber_b": ks.bit_error_rate(secret, rec_b),
                "key_ok": key_ok, "rec_a": rec_a, "rec_b": rec_b, "secret": secret,
            })
            r = results[-1]
            print(f"  {fmt_bits(r['bits']):>9s} bit  {label:24s} "
                  f"A: {r['psnr_a']:6.2f} dB  B: {r['psnr_b']:6.2f} dB  key: {'OK' if key_ok else 'RUSAK'}")
    return results


def save_figure(cover, agreed, secret_src, rng, robustness):
    shape = SECRET_SHAPES[-1]
    secret = gray(secret_src, shape)
    stego, agreed_stego, s1, info = ks.embed(cover, secret, agreed, SEED, R, rng=rng)
    recovered, key = ks.extract(stego, agreed_stego, s1, R)
    q, s2_bits = ks.share2_region(stego.size, ks.RM1())
    s2 = ks.rm_decode_bits(ks.modulus_extract(stego.ravel()[q:], 1).astype(np.uint8),
                           ks.RM1(), s2_bits).reshape(s1.shape)

    fig, axes = plt.subplots(3, 4, figsize=(16, 12))
    panels = [
        (cover, "Cover"), (stego, f"Stego I''  (PSNR {ks.psnr(cover, stego):.2f} dB)"),
        (np.abs(stego.astype(int) - cover.astype(int)) * 255, "|Stego - Cover| x255"),
        (secret, f"Secret {shape[0]}x{shape[1]} ({fmt_bits(info['secret_bits'])} bit)"),
        (agreed, "Agreed image A"),
        (agreed_stego, f"Agreed stego A'  (PSNR {ks.psnr(agreed, agreed_stego):.2f} dB)"),
        (np.abs(agreed_stego.astype(int) - agreed.astype(int)) * 32, "|A' - A| x32"),
        (recovered, "Recovered secret"),
        (1 - s1, "Share 1 (kanal aman)"), (1 - s2, "Share 2 (dari stego)"),
        (1 - ks.vcs_stack(s1, s2), "Share 1 + Share 2 (stacked)"),
    ]
    for ax, (img, title) in zip(axes.ravel(), panels):
        ax.imshow(img, cmap="gray", interpolation="nearest", aspect="auto" if img.shape[0] < 64 else "equal")
        ax.set_title(title, fontsize=10)
        ax.axis("off")
    ax = axes.ravel()[-1]
    ax.axis("off")
    ax.text(0, 0.95, "Kunci terbaca:\n" + key["text"].replace(" ", "\n"), va="top", family="monospace")
    ax.text(0, 0.35, f"E_T = {fmt_bits(info['ET'])} bit\nNc = {info['Nc']:.3f}\n"
                     f"|KT| = {fmt_bits(info['kt_len'])} bit\nnn = {info['nn']:.2f} bit/piksel A",
            va="top", family="monospace")
    fig.suptitle("Simulasi Kingsley & Barmawi (2020): Multiple Embedding, 450% capacity", fontsize=14)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "simulation_result.png"), dpi=110)
    plt.close(fig)

    Image.fromarray(stego).save(os.path.join(OUT_DIR, "stego.png"))
    Image.fromarray(agreed_stego).save(os.path.join(OUT_DIR, "agreed_stego.png"))
    Image.fromarray(recovered).save(os.path.join(OUT_DIR, "recovered_secret.png"))

    # Recovered secrets under a few attacks, scenario A vs B
    picks = [r for r in robustness if r["bits"] == info["secret_bits"]
             and r["attack"] in ("Salt & pepper 0.05", "Crop 0-512 x 0-360", "Scratch multiple (10)", "JPEG Q=75")]
    fig, axes = plt.subplots(2, len(picks), figsize=(4 * len(picks), 7))
    for col, r in enumerate(picks):
        for row, (img, psnr_val, tag) in enumerate([(r["rec_a"], r["psnr_a"], "A: KT aman"),
                                                   (r["rec_b"], r["psnr_b"], "B: A' ikut diserang")]):
            axes[row, col].imshow(img, cmap="gray")
            axes[row, col].set_title(f"{r['attack']}\n{tag}: {psnr_val:.2f} dB", fontsize=9)
            axes[row, col].axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "robustness_examples.png"), dpi=110)
    plt.close(fig)


def write_report(capacity, robustness):
    lines = ["# Hasil Simulasi Kingsley & Barmawi (2020)", "",
             f"Seed BBS = {SEED}, reference key R = {R}, RM(1,4), cover {SIZE}x{SIZE}.", "",
             "## 1. Kapasitas & imperceptibility (bandingkan dengan Tabel 1 paper)", "",
             "| Cover | Secret (bit) | E_T (bit) | Nc | EC paper | Payload murni (bpp) | EC 2 carrier | PSNR stego | PSNR A' | Pulih |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|:-:|"]
    for r in capacity:
        i = r["info"]
        lines.append(f"| {r['cover']} | {fmt_bits(r['bits'])} | {fmt_bits(i['ET'])} | {i['Nc']:.3f} | "
                     f"{i['EC_paper'] * 100:.2f}% | {i['payload_bpp']:.3f} | {i['EC_both_carriers'] * 100:.2f}% | "
                     f"{r['psnr_stego']:.2f} | {r['psnr_agreed']:.2f} | {'✔' if r['ok'] else '✘'} |")
    lines += ["", "PSNR A' = 100 berarti Agreed Image tidak berubah (tidak ada Key Trace).", "",
              "## 2. Robustness (bandingkan dengan Tabel 2–5 paper)", "",
              "- **A** = asumsi paper: hanya stego yang diserang, Agreed stego A' utuh.",
              "- **B** = serangan yang sama juga mengenai A'.",
              "- **Kunci** = apakah Share 2 di stego masih bisa didekode menjadi kunci yang benar.",
              "- PSNR 100 dB = citra rahasia pulih identik (konvensi paper).", "",
              "| Secret (bit) | Nc | Serangan | PSNR stego diserang | A: PSNR secret | A: BER | B: PSNR secret | B: BER | Kunci |",
              "|---:|---:|---|---:|---:|---:|---:|---:|:-:|"]
    for r in robustness:
        lines.append(f"| {fmt_bits(r['bits'])} | {r['Nc']:.2f} | {r['attack']} | {r['psnr_attacked']:.2f} | "
                     f"{r['psnr_a']:.2f} | {r['ber_a']:.4f} | {r['psnr_b']:.2f} | {r['ber_b']:.4f} | "
                     f"{'✔' if r['key_ok'] else '✘'} |")
    path = os.path.join(OUT_DIR, "hasil_simulasi.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    rng = np.random.default_rng(2020)
    covers, agreed, secret_src = load_images()

    print("== Eksperimen 1: kapasitas & PSNR")
    capacity = experiment_capacity(covers, agreed, secret_src, rng)

    print("\n== Eksperimen 2: robustness (cover Camera)")
    robustness = experiment_robustness(covers["Camera"], agreed, secret_src, rng)

    print("\n== Menyimpan gambar & laporan")
    save_figure(covers["Camera"], agreed, secret_src, rng, robustness)
    print("  " + write_report(capacity, robustness))


if __name__ == "__main__":
    main()
