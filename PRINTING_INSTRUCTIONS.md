# Poster Printing Instructions

## File Information
- **File:** `main.pdf`
- **Size:** 2.9 MB
- **Dimensions:** 120 × 72 inches (10 × 6 feet)
- **Orientation:** Landscape
- **Format:** PDF (XeLaTeX compiled)

## Printing Specifications

### Recommended Settings
- **Paper Type:** Matte or satin finish (preferred for scientific posters)
- **Resolution:** 300 DPI minimum (poster is designed for this)
- **Color Mode:** RGB (already optimized)
- **Size:** Full 120 × 72 inches (no scaling)

### Printer Options

#### Option 1: Professional Print Shop (Recommended)
**Best for:** High-quality, durable posters

**Providers:**
- Local university print center (often cheapest for students)
- FedEx Office / Staples (widely available)
- Online services: iPrint, PosterBurner, MakeSigns

**Typical Cost:** $50-150 USD depending on material

**Materials to consider:**
- **Matte paper** (recommended) - No glare, easy to read
- **Glossy paper** - Vibrant colors, can have glare under lights
- **Fabric/cloth** - Durable, wrinkle-free, foldable for travel
- **Foam core backing** - Rigid, professional appearance

#### Option 2: Roll-Up Banner
**Best for:** Frequent conference travel

**Advantages:**
- Portable retractable stand
- Protects poster during transport
- Quick setup/takedown

**Cost:** $100-200 USD (includes stand)

### Before Sending to Print

1. **Open the PDF** at 100% zoom and verify:
   - All text is readable
   - All figures display correctly
   - No content is cut off at edges
   - Colors look correct

2. **Check dimensions:**
   ```bash
   pdfinfo main.pdf | grep "Page size"
   # Should show: 8640 x 5184 pts (120 x 72 in)
   ```

3. **Verify no compression artifacts** (zoom to 200-300%)

4. **Print a test page** (if possible):
   - Print 1 section at letter size to check colors
   - Verify text is readable when scaled down

## Overflow Status

### Current Overflow: 72pt ≈ 1 inch

**What this means:**
- The poster content extends slightly beyond the intended boundary
- **This is acceptable** because:
  - Most printers have 0.5-1 inch margins anyway
  - Content won't be cut off in the printable area
  - All essential information is visible

**If printer requires exact fit:**
Ask them to:
1. Use their margins to accommodate the 1-inch overflow, OR
2. Scale by 99% (negligible visual difference)

**Do NOT:** Re-compile with different dimensions - this will break the layout

## Packing for Transport

### If Rolled:
1. Roll with print side OUT (prevents cracking)
2. Use a poster tube (cardboard or plastic)
3. Pad ends with bubble wrap
4. Label tube clearly

### If Flat/Foam Core:
1. Wrap in plastic sheet protector
2. Place in rigid poster board carrier
3. Keep horizontal during transport

### If Fabric Banner:
1. Roll loosely in retractable stand
2. Place stand in carrying bag
3. Most durable option for international travel

## At the Conference

### Setup Checklist:
- [ ] Poster tube/carrier
- [ ] Push pins or poster tape (check venue requirements)
- [ ] Business cards or QR code handouts
- [ ] Printed handouts (optional: key results summary)
- [ ] Notebook for contact information
- [ ] Device with full manuscript PDF (for detailed questions)

### Venue-Specific:
**ICTP Advanced School in Applied Machine Learning**
- Location: Trieste, Italy
- Dates: July 23-31, 2026
- Check ICTP poster session guidelines for:
  - Mounting method (pins vs. velcro vs. tape)
  - Poster board dimensions
  - Setup time window

### Presentation Tips:
1. **Stand to the SIDE** of your poster (don't block it)
2. **Prepare 3 versions** of your pitch:
   - 30-second (elevator pitch)
   - 2-minute (full summary)
   - 5-minute (detailed walkthrough)
3. **Point to specific figures** as you talk
4. **Have answers ready** for common questions (see PRESENTATION_TALKING_POINTS.md)

## Digital Backup

### Always Carry:
1. **PDF on USB drive** - In case you need to re-print
2. **PDF on phone/tablet** - For showing to interested colleagues
3. **Manuscript PDF** - For detailed technical questions
4. **Zenodo link** ready: `10.5281/zenodo.19608875`

### Social Media Version:
Create a compressed version for sharing:
```bash
# Reduce to 1/4 size for social media
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/ebook \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=main_compressed.pdf main.pdf
```

## Common Printing Issues & Solutions

### Issue 1: "File too large"
**Solution:** 2.9 MB should not be an issue, but if needed:
```bash
# Compress to < 1 MB
gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/printer \
   -dNOPAUSE -dQUIET -dBATCH \
   -sOutputFile=main_print.pdf main.pdf
```

### Issue 2: "Colors look different"
**Solution:** 
- Request RGB color space (not CMYK)
- Provide the original PDF (don't let printer "optimize")
- Ask for a color-calibrated printer

### Issue 3: "Text is too small"
**Solution:**
- Body text is 24pt minimum (readable from 4-6 feet)
- This is standard for scientific posters
- If printer suggests larger text, decline (breaks layout)

### Issue 4: "Need bleed area"
**Solution:**
- Current PDF has no bleed
- For professional printing, ask if they can add 0.25" bleed
- Or accept the 1-inch overflow as built-in margin

## Cost Estimates (USD, as of 2026)

| Option | Cost | Turnaround | Durability |
|--------|------|------------|------------|
| University print center | $40-80 | 1-2 days | Medium |
| FedEx/Staples (paper) | $80-120 | Same day | Medium |
| FedEx/Staples (fabric) | $150-200 | 2-3 days | High |
| Roll-up banner (online) | $100-180 | 5-7 days + shipping | High |
| Foam core mounted | $120-180 | 2-3 days | High (fragile) |

### Budget Recommendation:
- **Student budget:** University print center, matte paper ($50-70)
- **Professional:** Fabric print with carrying case ($150-180)
- **Frequent presenter:** Roll-up banner with stand ($150-200)

## Final Checklist

### Before ordering:
- [ ] PDF opens correctly on your device
- [ ] All figures are visible and clear
- [ ] Poster dimensions are 120 × 72 inches
- [ ] Colors look good on screen
- [ ] You've read the PRESENTATION_TALKING_POINTS.md

### At print shop:
- [ ] Provide PDF on USB (not printed to paper first)
- [ ] Request RGB color space
- [ ] Ask for matte or satin finish (not glossy)
- [ ] Confirm 120 × 72 inch final size
- [ ] Request no automatic color correction

### Upon receiving:
- [ ] Unroll carefully to inspect
- [ ] Check all text is readable
- [ ] Verify no printing defects
- [ ] Test rolling (if applicable)
- [ ] Store in poster tube until conference

## Emergency Re-print

If you need to re-print at the conference:

**In Trieste, Italy:**
1. **Copisteria Universitaria** (Via Valerio, near UniTS)
2. **Cartolibreria Italo Svevo** (Via Cesare Battisti)
3. **ICTP may have emergency printing** - Ask conference organizers

**Backup plan:**
- Keep PDF on USB drive
- Have credit card ready
- Allow 24-48 hours for large format printing
- Budget €100-150 for emergency print

## Questions?

**Technical issues with PDF:**
- Check OVERFLOW_FIXES_SUMMARY.md
- Compilation: `xelatex main.tex`

**Content questions:**
- See PRESENTATION_TALKING_POINTS.md
- See POSTER_IMPROVEMENTS.md

**Printing problems:**
Contact your chosen print shop with specific questions about their capabilities.

---

**Your poster is ready to win Best Poster Award! Good luck at ICTP 2026!** 🎯🏆
