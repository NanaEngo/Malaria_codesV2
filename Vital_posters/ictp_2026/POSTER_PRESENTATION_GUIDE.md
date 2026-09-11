# Poster Presentation Guide
## Uncertainty-Aware Deep Learning for Antimalarial Drug Discovery

**ICTP Advanced School in Applied Machine Learning (smr 4228)**  
**July 23-31, 2026 — Trieste, Italy**

---

## Overview

This guide provides a structured approach to presenting your research poster effectively during the ICTP conference. The poster focuses on **uncertainty quantification** and **robustness** in deep learning for antimalarial drug discovery.

---

## Pre-Presentation Preparation

### 1. Know Your Audience
- **Primary audience**: Machine learning researchers, computational scientists, drug discovery experts
- **Expertise level**: Advanced (PhD students, postdocs, faculty)
- **Background**: May not be familiar with malaria drug discovery but understand ML/AI concepts
- **Interest**: Uncertainty quantification, robustness, real-world applications of ML

### 2. Prepare Multiple Pitch Lengths

**30-Second Elevator Pitch** (for busy attendees):
> "We developed an uncertainty-aware deep learning framework for antimalarial drug discovery. By combining variational autoencoders with consensus validation, we identified 19,913 drug candidates with quantified confidence scores while reducing false positives by 12-45%. The key innovation is making AI predictions reliable enough for pharmaceutical applications."

**2-Minute Summary** (for interested attendees):
> "Malaria affects 247 million people annually, and new drugs are urgently needed. Current computational screening methods generate many false positives that waste experimental resources. We addressed this by developing an uncertainty-aware framework with three key components:
> 
> First, we trained variational autoencoders on 65,856 molecules to create probabilistic molecular representations. The 64D model achieves 93% reconstruction with KL divergence of 12.86, which quantifies uncertainty.
> 
> Second, we implemented consensus validation combining physics-based (AutoDock Vina) and machine learning (DiffDock) docking. Low correlation between methods (r=0.1-0.4) confirms they provide complementary information, reducing false positives by 12-45%.
> 
> Third, we validated robustness across multiple algorithms and external benchmarks like DEKOIS and MMV Malaria Box, achieving ROC-AUC of 0.924-1.000.
> 
> The result: 19,913 synthesizable leads with confidence scores, enabling risk-stratified experimental validation and 99% reduction in screening costs."

**5-Minute Deep Dive** (for serious collaborators):
Expand on the 2-minute version by covering:
- Technical details of VAE architecture (3-layer 1D convolutions on SMILES)
- Why 64D outperforms 32D (higher KL divergence = more explicit uncertainty)
- Clustering methodology (KMeans with Silhouette 0.229, Calinski-Harabasz 1501)
- Consensus validation strategy and why orthogonal methods matter
- External validation results and statistical significance
- Practical implications for drug discovery pipeline
- Open science approach (Zenodo DOI: 10.5281/zenodo.19608875)

### 3. Anticipate Questions

**Common technical questions:**

**Q: "Why use VAE instead of other generative models?"**  
A: "VAEs provide explicit uncertainty quantification through KL divergence and latent space variance, which are critical for pharmaceutical applications where we need confidence estimates. Other models like GANs don't naturally provide this."

**Q: "How do you know the consensus validation actually reduces false positives?"**  
A: "We validated on external benchmarks (DEKOIS 2.0 with 1200 decoys, MMV Malaria Box with 399 actives) where ground truth is known. The consensus approach achieved ROC-AUC 0.924-1.000 across four targets, significantly outperforming individual methods."

**Q: "What's the computational cost?"**  
A: "VAE training takes ~2-3 hours on a single GPU. The key efficiency gain is reducing screening from 65,856 to 484 centroids (99.3% reduction) while maintaining diversity. Consensus docking on these 484 is manageable."

**Q: "How do you handle epistemic vs aleatoric uncertainty?"**  
A: "Epistemic uncertainty (model uncertainty) is captured through latent space variance in the VAE. Aleatoric uncertainty (data uncertainty) is measured via reconstruction confidence. Both are tracked throughout the pipeline and reflected in our final confidence scores."

**Q: "Can this framework be applied to other diseases?"**  
A: "Absolutely. The uncertainty-aware framework is disease-agnostic. You'd need to retrain the VAE on disease-specific compounds and select appropriate protein targets, but the methodology transfers directly."

**Q: "How do you select the consensus threshold?"**  
A: "We don't use a fixed threshold. Instead, we rank by agreement between methods. Compounds where both methods predict strong binding get highest confidence. The 12-45% false positive reduction comes from comparing top-ranked consensus hits vs single-method predictions on validation sets."

**Application-oriented questions:**

**Q: "Have any of these compounds been tested experimentally?"**  
A: "This is computational work. The 19,913 leads with confidence scores are ready for experimental validation. We've made all data available on Zenodo (DOI: 10.5281/zenodo.19608875) to enable collaborations with experimental groups."

**Q: "What's the synthesis feasibility?"**  
A: "All 19,913 leads passed synthetic accessibility filters. We focused on compounds expanded from known natural products and antimalarials, which tend to have drug-like properties (94.1% Lipinski-compliant)."

**Q: "How does this compare to existing drug discovery pipelines?"**  
A: "Traditional virtual screening doesn't quantify uncertainty, leading to high failure rates in experimental validation. Our framework provides explicit confidence scores, enabling risk-stratified testing—high-confidence compounds go to expensive assays first, medium-confidence to secondary screens, low-confidence are deprioritized. This optimizes resource allocation."

---

## Presentation Structure

### Opening (30 seconds)
**Goal**: Capture attention and state the problem

Stand beside your poster (not blocking it). Make eye contact. Use your elevator pitch:

> "Hi! My poster is about making AI predictions reliable for drug discovery. Current methods generate many false positives that waste experimental resources. We solved this by developing an uncertainty-aware framework that quantifies confidence in predictions."

**Then ask**: "Are you interested in uncertainty quantification, drug discovery, or both?"

This helps you tailor the rest of your presentation.

### Body (2-4 minutes)
**Goal**: Walk through the key findings using the poster visuals

**Follow the column structure:**

#### Column 1: Problem & Approach
Point to the **Research Question** box:
> "The key question is: can we make deep learning reliable through explicit uncertainty quantification?"

Point to the **flowchart**:
> "We started with 65,856 molecules, applied VAE for probabilistic representations, clustered in latent space, and used consensus validation to identify 19,913 high-confidence leads."

Point to **VAE comparison graphs**:
> "Here's the core innovation—we compared 32D vs 64D VAE models. The 64D model has higher reconstruction (93% vs 92%) and **critically**, higher KL divergence (12.86 vs 6.43), which quantifies uncertainty. This explicit uncertainty is what enables confidence scoring."

#### Column 2: Validation
Point to **consensus correlation**:
> "We validated using two orthogonal methods: physics-based Vina and ML-based DiffDock. The low correlation (0.1-0.4) confirms they provide complementary information."

Point to **hit rate comparison**:
> "This consensus approach reduced false positives by 12-45% across four malaria targets."

Point to **external validation graphs**:
> "We validated on external benchmarks—DEKOIS with 1200 decoys and MMV Malaria Box with 399 known actives—achieving ROC-AUC 0.924-1.000."

#### Column 3: Results & Impact
Point to **docking results**:
> "These are binding affinity distributions across four Plasmodium falciparum targets. Consensus hits show strong binding below -8 kcal/mol."

Point to **physicochemical properties**:
> "All leads maintain drug-like properties—molecular weight, LogP, hydrogen bond donors/acceptors all within optimal ranges."

Point to **Key Results** box:
> "Bottom line: 19,913 leads with uncertainty scores, over 70 polypharmacological candidates, 99% cost reduction, and validated performance across benchmarks."

### Closing (30 seconds)
**Goal**: Emphasize impact and invite further discussion

> "The key takeaway is that uncertainty quantification makes AI reliable enough for pharmaceutical applications. By providing confidence scores, we enable risk-stratified experimental validation—you test high-confidence compounds first, optimizing resources.
> 
> All our data and code are available on Zenodo [point to DOI]. I'd love to discuss potential collaborations or answer any questions about the methodology."

---

## Body Language & Engagement Tips

### Positioning
- **Stand to the SIDE** of your poster, not in front
- **Face the attendee** at a 45° angle so you can see both them and the poster
- **Leave space** for multiple people to view simultaneously
- **Step back** when pointing to give them a clear view

### Gestures
- **Point specifically** to figures when discussing them (use a pen or your hand)
- **Use hand gestures** to emphasize key numbers ("19,913 leads" - hold up fingers)
- **Trace workflows** with your finger (the flowchart arrows)
- **Show scale** with hands (e.g., "from 65,000 down to 484")

### Eye Contact
- **Make eye contact** 70% of the time
- **Look at the poster** 30% of the time (when pointing to specific elements)
- **Scan the audience** if multiple people are listening
- **Watch for engagement signals** (nodding, frowning, looking confused)

### Voice
- **Speak clearly** and at moderate pace (not too fast despite nervousness)
- **Vary your tone** to emphasize key points
- **Pause** after important statements to let them sink in
- **Project** so people 6 feet away can hear (poster sessions are noisy)

### Energy
- **Show enthusiasm** about your work (it's contagious!)
- **Smile** when appropriate (especially when greeting)
- **Stay alert** even after many repetitions
- **Take breaks** if the session is long (have water nearby)

---

## Handling Different Attendee Types

### The Skeptic
**Characteristics**: Challenges methodology, asks critical questions

**Strategy**:
- **Stay calm and professional** (don't get defensive)
- **Acknowledge valid concerns**: "That's a great point..."
- **Point to validation evidence**: "Which is why we validated on external benchmarks..."
- **Offer to discuss offline**: "I'd love to discuss this in more depth. Do you have a card?"

**Example exchange**:
> Skeptic: "Consensus validation seems like just averaging two methods."  
> You: "Great question! It's actually more nuanced. The low correlation (0.1-0.4) means the methods provide complementary information—they fail in different ways. When both agree on strong binding, we have higher confidence. We validated this on DEKOIS with known actives and decoys [point to graph]. The consensus approach significantly outperformed either method alone with ROC-AUC of 0.924-1.000."

### The Collaborator
**Characteristics**: Interested in your methods, potential partnership

**Strategy**:
- **Go deeper technically** if they have time
- **Highlight reproducibility**: "All code and data on Zenodo..."
- **Exchange contact information**
- **Follow up** after the conference

**Example exchange**:
> Collaborator: "We have 10,000 compounds to screen. Could your method help?"  
> You: "Absolutely! The framework is transferable. You'd train the VAE on your compounds, then apply consensus validation on your targets. The uncertainty scores would help you prioritize which compounds to test first. Let me give you my email, and we can discuss the specifics of your project."

### The Novice
**Characteristics**: Interested but limited background in ML or drug discovery

**Strategy**:
- **Use analogies**: "Think of uncertainty like error bars on experimental measurements"
- **Avoid jargon** or define terms: "Variational autoencoder—that's a neural network that learns to compress and reconstruct molecules while tracking uncertainty"
- **Focus on concepts** over technical details
- **Point to visuals** more (graphs are universal)

**Example exchange**:
> Novice: "What's KL divergence?"  
> You: "Great question! Think of it like this: the VAE learns to represent molecules in a compressed space. KL divergence measures how different this learned representation is from a simple baseline. Higher KL divergence (12.86 in our case) means the model is capturing more complex patterns, which also gives us better uncertainty estimates. See how the 64D model [point] has higher KL than 32D? That's why we chose it."

### The Time-Constrained
**Characteristics**: Glances at poster, "just browsing"

**Strategy**:
- **Give elevator pitch** immediately (30 seconds)
- **Offer a handout** if you have one
- **Point to one key figure**: "The main result is here [point to Key Results box]"
- **Let them go** gracefully: "Feel free to come back if you have questions!"

---

## Interactive Elements

### Use Your Hands
- **Trace the pipeline**: Use your finger to follow the flowchart arrows
- **Compare visually**: Hold your hands apart to show "65,000 compounds [wide] down to 484 [narrow]"
- **Count on fingers**: "Three key innovations: 1) uncertainty quantification, 2) consensus validation, 3) external benchmarking"

### Engage with Questions
**Ask them**:
- "Are you familiar with variational autoencoders?" (gauges their background)
- "Which part would you like to hear more about?" (lets them guide)
- "Do you work in drug discovery or machine learning?" (helps you tailor)
- "What do you think about this approach?" (invites discussion)

**Invite interaction**:
- "Let me show you the key difference between these two models..." [point to comparison]
- "Notice how these graphs [consensus] show low correlation—that's the key insight..."
- "Look at this validation result [point]—perfect ROC-AUC..."

---

## Time Management

### Gauge Interest Quickly (first 30 seconds)
- **High interest** signals: stops walking, makes eye contact, asks questions, takes photo
  - → Give 2-5 minute presentation
- **Medium interest** signals: glances, polite listening, checking phone
  - → Give 1-2 minute summary, offer handout
- **Low interest** signals: keeps walking, looks distracted, says "just looking"
  - → Give 30-second pitch, let them go

### Manage Long Conversations
- If someone is monopolizing your time and others are waiting:
  - "These are great questions! I see others waiting. Can I give you my email and we can continue this discussion later?"
- If you need a break:
  - "Excuse me for one moment, I need to grab some water. Feel free to browse, and I'll be right back."

---

## Logistics & Materials

### Before the Session

**Print materials** (optional but helpful):
- Business cards with your email
- 1-page handout with:
  - Poster thumbnail
  - Key findings (bullet points)
  - Zenodo DOI for data/code
  - Your contact information
- Notebook for collecting contact info

**Bring supplies**:
- Water bottle (you'll talk a lot!)
- Pen for pointing and taking notes
- Phone/tablet to show supplementary materials if needed
- Sticky notes for marking questions to follow up on

**Test your setup**:
- Arrive 15 minutes early
- Ensure poster is properly mounted (not sagging or curling)
- Check lighting (can people read the text?)
- Stand back 6 feet and verify readability

### During the Session

**Stay present**:
- Don't sit (looks disengaged)
- Don't read from phone (looks bored)
- Don't eat or drink in front of poster (unprofessional)
- Don't turn your back to the crowd

**Engage passersby**:
- Make eye contact with people walking by
- Smile and nod
- If someone slows down: "Would you like me to give you a quick overview?"
- If someone takes a photo: "Feel free to take a picture! Would you like me to email you the PDF?"

**Take notes**:
- Write down good questions (might be paper ideas!)
- Collect business cards
- Note collaboration opportunities
- Track common points of confusion (improve next poster!)

### After the Session

**Follow up** (within 3 days):
- Email people you promised to contact
- Send poster PDF if requested
- Send relevant papers or code
- Thank them for their interest

**Reflect**:
- What questions came up repeatedly? (address in paper)
- What parts were confusing? (redesign for next poster)
- What collaboration opportunities emerged?

---

## Emergency Scenarios

### "I don't understand this at all"
**Response**: "Let me start with the big picture. Malaria kills hundreds of thousands yearly. Finding new drugs is expensive because we test many compounds that fail. Our AI helps predict which compounds are most likely to work, saving time and money. The key innovation is quantifying how confident we are in each prediction."

**Then ask**: "Does that help? Which part would you like me to clarify?"

### "This is wrong because..."
**Response**: "That's an interesting point. Let me show you our validation [point to benchmarks]. We tested on external datasets with known ground truth and achieved 0.924-1.000 ROC-AUC. But I'd love to hear more about your concern. Do you have a few minutes to discuss?"

**Stay professional**. If they're combative, offer to continue via email.

### "Can you explain this equation/term?"
**Response**: "Sure! [Define in simple terms]. The key takeaway is [concept in plain English]."

**Example**: "KL divergence measures how much information the model retains about uncertainty. Higher is better for our application because we need confidence estimates."

### "I do similar work, this is my poster..."
**Response**: "That's great! Let's exchange information. Maybe we can find synergies or even collaborate."

**Ask**: "What overlap do you see? Are you also working on uncertainty quantification?"

### "How is this different from [paper/method]?"
**Response**: 
- **If you know it**: "Great reference! We build on that work but add [your innovation]. Specifically..."
- **If you don't know it**: "I'm not familiar with that work—can you send me the reference? I'd love to read it and see the connections."

**Never fake knowledge**. It's fine to say "I don't know."

---

## Confidence Builders

### Remember:
- **You know this work better than anyone** in the room
- **Enthusiasm is persuasive** even if you're nervous
- **Mistakes are okay** (if you misspeak, just correct yourself)
- **Not everyone will be interested** and that's fine
- **Difficult questions are compliments** (it means they're engaged)

### If You Get Nervous:
- **Breathe deeply** (slow, controlled breaths)
- **Pause before answering** (it's not a race)
- **Focus on one person** at a time (not the whole crowd)
- **Remember your why** (this work matters!)

### Practice Makes Perfect:
- **Rehearse** your 30-second, 2-minute, and 5-minute pitches
- **Practice with friends** who don't know your field
- **Record yourself** and watch for filler words ("um," "like")
- **Visualize success** (imagine smooth conversations)

---

## Success Metrics

### Good Session Indicators:
- ✅ Multiple people stop to listen (not just glance)
- ✅ People ask follow-up questions
- ✅ You collect several business cards/emails
- ✅ Someone takes a photo of your poster
- ✅ Potential collaborations emerge
- ✅ You learn something from questions/discussions
- ✅ You feel energized (not drained) afterward

### What to Track:
- **Number of substantive conversations** (>2 minutes)
- **Collaboration leads** (people who want to follow up)
- **Common questions** (what people care about)
- **Compliments on specific aspects** (what resonated)

---

## Cultural Considerations (ICTP Conference)

### International Audience:
- **Speak clearly** (many non-native English speakers)
- **Avoid idioms/slang** ("knocked it out of the park" → "performed very well")
- **Write down key terms** if there's confusion
- **Be patient** if someone struggles to articulate their question
- **Offer to continue in their language** if you share one

### Academic Hierarchy:
- **Treat everyone respectfully** (student or professor)
- **Don't name-drop** excessively
- **Give credit** to collaborators and prior work
- **Be humble** about your contributions ("We built on X's foundation...")

### Disciplinary Differences:
- **Machine learning people** care about: model architecture, training details, generalization
- **Drug discovery people** care about: hit rates, synthesis, ADMET, clinical relevance
- **Adapt your language** to your audience

---

## Final Checklist

### Day Before:
- [ ] Review this guide
- [ ] Practice 30-second, 2-minute, 5-minute pitches
- [ ] Prepare answers to anticipated questions
- [ ] Print business cards and handouts
- [ ] Get good sleep (you'll need energy!)

### Morning Of:
- [ ] Dress professionally but comfortably (you'll stand all day)
- [ ] Eat a good breakfast
- [ ] Arrive early to set up
- [ ] Do a quick readability check

### During Session:
- [ ] Stand beside poster (not in front)
- [ ] Greet passersby with eye contact and smile
- [ ] Use visuals to guide discussion
- [ ] Collect contact information
- [ ] Take notes on good questions

### After Session:
- [ ] Follow up with interested parties (within 3 days)
- [ ] Reflect on what worked and what didn't
- [ ] Save good questions for future paper/poster improvements

---

## Remember: You Got This! 🎉

Your research is valuable. Your poster is well-designed. You've prepared thoroughly. Now go out there and share your work with confidence and enthusiasm!

**Key mindset**: This is a **conversation**, not a performance. You're sharing something exciting with people who are genuinely interested in your field. Enjoy the experience!

---

## Contact for Questions

If attendees have follow-up questions after the conference, direct them to:
- **Email**: myke-vital.sao@facsciences-uy1.cm
- **Data/Code**: Zenodo DOI: 10.5281/zenodo.19608875
- **Institution**: Department of Physics, University of Yaoundé I, Cameroon

Good luck at ICTP! 🚀
