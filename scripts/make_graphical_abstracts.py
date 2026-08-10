#!/usr/bin/env python3
"""Generate J. Cheminformatics-compliant graphical abstracts (920x300 px, white bg, <150 KB).

Sources:
  P3: results/figures/p3_auc_benchmark_bar.png + manuscript Graphics/p3_tda_promiscuity.png
  P4: manuscript Graphics/pareto_front.png + benchmark_reward_bar.png
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = "/home/nanaengo/Malaria_codesV2"
W, H = 920, 300
OUT = {
    "p3": os.path.join(ROOT, "Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX/Graphics/Graphical_Abstract_P3.png"),
    "p4": os.path.join(ROOT, "Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/Graphics/Graphical_Abstract_P4.png"),
}


def try_font(size, bold=False):
    cands = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for c in cands:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def fit(img, maxw, maxh):
    img.thumbnail((maxw, maxh), Image.LANCZOS)
    return img


def load(path, maxw, maxh):
    im = Image.open(path).convert("RGB")
    return fit(im, maxw, maxh)


def draw_fit(draw, xy, text, font, fill, max_width, min_size=10, max_size=None):
    """Draw text, shrinking the font until it fits max_width (no overflow).
    Returns the font actually used."""
    f = font
    while f.size > min_size:
        w = draw.textlength(text, font=f)
        if w <= max_width:
            break
        f = ImageFont.truetype(f.path, f.size - 1) if hasattr(f, "path") else font
    if hasattr(f, "path"):
        f = ImageFont.truetype(f.path, f.size)
    draw.text(xy, text, font=f, fill=fill)
    return f


def compose_p3():
    canvas = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(canvas)
    f_title = try_font(26, bold=True)
    f_sub = try_font(17)
    f_lab = try_font(14, bold=True)

    # Left text panel
    draw.text((28, 16), "Quantum-inspired representations of", font=f_title, fill=(20, 20, 60))
    draw.text((28, 48), "African antimalarial natural products", font=f_title, fill=(20, 20, 60))
    draw.text((28, 92), "TFP \u00b7 persistent homology   TNE \u00b7 tensor networks   QKS \u00b7 quantum kernel", font=f_sub, fill=(90, 90, 140))
    draw.text((28, 122), "n = 19,836 \u00b7 5-fold CV \u00b7 ECFP4 baseline", font=f_sub, fill=(90, 90, 140))

    # Right: two figures side by side
    bar = load(os.path.join(ROOT, "Project3_Quantum_Inspired_RepresentationsV2607/results/figures/p3_auc_benchmark_bar.png"), 300, 230)
    tda = load(os.path.join(ROOT, "Project3_Quantum_Inspired_RepresentationsV2607/manuscript/LaTeX/Graphics/p3_tda_promiscuity.png"), 300, 230)
    canvas.paste(bar, (360, 34))
    canvas.paste(tda, (600, 34))
    draw_fit(draw, (360, 268), "AUC benchmark (ECFP4 0.948 > hybrid 0.888)", f_lab, (40, 40, 90), 300)
    draw_fit(draw, (600, 268), "Scaffold paradox: H\u2081 conserved, H\u2080 divergent", f_lab, (40, 40, 90), 300)

    # verdict strip
    draw.rectangle([24, 200, 340, 252], fill=(238, 242, 250), outline=(160, 170, 210))
    draw.text((40, 210), "Honest-negative result:", font=f_lab, fill=(150, 30, 30))
    draw_fit(draw, (40, 230), "QKS \u2248 RBF (p = 0.060) \u2014 ECFP4 remains the", f_sub, (40, 40, 90), 300)
    draw_fit(draw, (40, 246), "recommended primary descriptor.", f_sub, (40, 40, 90), 300)
    return canvas


def compose_p4():
    canvas = Image.new("RGB", (W, H), "white")
    draw = ImageDraw.Draw(canvas)
    f_title = try_font(26, bold=True)
    f_sub = try_font(17)
    f_lab = try_font(14, bold=True)

    draw.text((28, 16), "Pareto-guided MCTS for de novo", font=f_title, fill=(20, 20, 60))
    draw.text((28, 48), "antimalarial design", font=f_title, fill=(20, 20, 60))
    draw.text((28, 92), "Multi-objective exploration, not scalar superiority", font=f_sub, fill=(90, 90, 140))
    draw.text((28, 122), "20 seeds \u00b7 MPO \u00b7 SYBA \u00b7 RRS proxy \u00b7 PNS proxy", font=f_sub, fill=(90, 90, 140))

    pareto = load(os.path.join(ROOT, "Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/Graphics/pareto_front.png"), 300, 230)
    bench = load(os.path.join(ROOT, "Project4_Advanced_Monte_CarloV2607/manuscript/LaTeX/Graphics/benchmark_reward_bar.png"), 300, 230)
    canvas.paste(pareto, (360, 34))
    canvas.paste(bench, (600, 34))
    draw_fit(draw, (360, 268), "Post-hoc Pareto front (HV 1.237)", f_lab, (40, 40, 90), 300)
    draw_fit(draw, (600, 268), "Scalar benchmark: random 0.672 > MCTS 0.665", f_lab, (40, 40, 90), 300)

    draw.rectangle([24, 200, 340, 252], fill=(238, 242, 250), outline=(160, 170, 210))
    draw.text((40, 210), "Contribution:", font=f_lab, fill=(150, 30, 30))
    draw_fit(draw, (40, 230), "Transparent objective-space exploration", f_sub, (40, 40, 90), 300)
    draw_fit(draw, (40, 246), "with RRS/PNS-informed design dimensions.", f_sub, (40, 40, 90), 300)
    return canvas


def main():
    for key, path in OUT.items():
        canvas = compose_p3() if key == "p3" else compose_p4()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        canvas.save(path, "PNG")
        kb = os.path.getsize(path) / 1024
        print(f"{key}: {path}  {canvas.size[0]}x{canvas.size[1]}  {kb:.0f} KB")
        assert kb < 150, f"too large: {kb:.0f} KB"


if __name__ == "__main__":
    main()
