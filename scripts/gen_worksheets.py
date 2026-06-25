#!/usr/bin/env python3
"""
gen_worksheets.py — Generate printable clinical worksheet PDFs (ReportLab).

House style (matches existing site PDFs):
  - Title: large, bold, teal #0d9488
  - Subtitle: "Greater Nashua Mental Health Center" (gray)
  - "Instructions:" italic paragraph
  - Body: teal section headings + lined writing space / labeled boxes /
    bordered tracking tables, appropriate to the worksheet's clinical purpose
  - Footer on every page: AI-assist disclaimer (centered) + "Page N"
  - US Letter, ~0.75in margins, Helvetica family

Run:  python3 scripts/gen_worksheets.py
Output: PDFs under pdfs/dbt, pdfs/act, pdfs/trauma, pdfs/skills, pdfs/recovery
"""

import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

# ----------------------------------------------------------------------------
# Palette / geometry
# ----------------------------------------------------------------------------
TEAL = HexColor("#0d9488")
TEAL_DARK = HexColor("#0f766e")
GRAY = HexColor("#6b7280")
LIGHT_GRAY = HexColor("#d1d5db")
LINE_GRAY = HexColor("#cbd5e1")
BOX_BORDER = HexColor("#94a3b8")
TEXT = HexColor("#1f2937")
SUBTLE_BG = HexColor("#f1f5f9")

PAGE_W, PAGE_H = letter
MARGIN = 0.75 * inch
CONTENT_W = PAGE_W - 2 * MARGIN

SUBTITLE = "Greater Nashua Mental Health Center"
FOOTER_NOTE = "AI-assisted clinical resource — clinician review required"

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ----------------------------------------------------------------------------
# Sheet — a small layout engine that flows content top-to-bottom and paginates
# ----------------------------------------------------------------------------
class Sheet:
    def __init__(self, path, title):
        self.path = path
        self.title = title
        self.page = 1
        self.c = canvas.Canvas(path, pagesize=letter)
        self._start_page(first=True)

    # -- page lifecycle ----------------------------------------------------
    def _start_page(self, first=False):
        self.y = PAGE_H - MARGIN
        if first:
            self._draw_header()
        else:
            self._draw_running_header()
        self._footer()

    def _draw_header(self):
        c = self.c
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 22)
        # wrap title if very long
        for line in self._wrap(self.title, "Helvetica-Bold", 22, CONTENT_W):
            c.drawString(MARGIN, self.y - 22, line)
            self.y -= 26
        self.y -= 2
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 11)
        c.drawString(MARGIN, self.y - 11, SUBTITLE)
        self.y -= 20
        c.setStrokeColor(TEAL)
        c.setLineWidth(1.5)
        c.line(MARGIN, self.y, PAGE_W - MARGIN, self.y)
        self.y -= 16

    def _draw_running_header(self):
        c = self.c
        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(MARGIN, self.y - 12, self.title + "  (continued)")
        self.y -= 18
        c.setStrokeColor(LIGHT_GRAY)
        c.setLineWidth(0.75)
        c.line(MARGIN, self.y, PAGE_W - MARGIN, self.y)
        self.y -= 14

    def _footer(self):
        c = self.c
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7.5)
        c.drawCentredString(PAGE_W / 2, 0.45 * inch, FOOTER_NOTE)
        c.drawRightString(PAGE_W - MARGIN, 0.45 * inch, "Page %d" % self.page)

    def page_break(self):
        self.c.showPage()
        self.page += 1
        self._start_page(first=False)

    def need(self, h):
        """Ensure at least h vertical points remain; else page-break."""
        if self.y - h < 0.7 * inch:
            self.page_break()

    # -- text helpers ------------------------------------------------------
    def _wrap(self, text, font, size, max_w):
        self.c.setFont(font, size)
        words = text.split()
        lines, cur = [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if self.c.stringWidth(trial, font, size) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines or [""]

    def gap(self, h=10):
        self.y -= h

    def instructions(self, text):
        self.need(40)
        c = self.c
        c.setFillColor(TEXT)
        for line in self._wrap("Instructions: " + text, "Helvetica-Oblique", 10, CONTENT_W):
            c.setFont("Helvetica-Oblique", 10)
            c.drawString(MARGIN, self.y - 10, line)
            self.y -= 13
        self.y -= 6

    def heading(self, text):
        self.need(30)
        c = self.c
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(MARGIN, self.y - 13, text)
        self.y -= 18

    def subheading(self, text):
        self.need(22)
        c = self.c
        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(MARGIN, self.y - 11, text)
        self.y -= 15

    def body(self, text, size=9.5, indent=0):
        c = self.c
        c.setFillColor(TEXT)
        for line in self._wrap(text, "Helvetica", size, CONTENT_W - indent):
            self.need(size + 4)
            c.setFont("Helvetica", size)
            c.drawString(MARGIN + indent, self.y - size, line)
            self.y -= size + 3.5
        self.y -= 2

    def bullet(self, text, size=9.5):
        c = self.c
        c.setFillColor(TEAL)
        self.need(size + 4)
        c.setFont("Helvetica-Bold", size)
        c.drawString(MARGIN + 4, self.y - size, "•")
        c.setFillColor(TEXT)
        first = True
        for line in self._wrap(text, "Helvetica", size, CONTENT_W - 18):
            self.need(size + 4)
            c.setFont("Helvetica", size)
            c.drawString(MARGIN + 16, self.y - size, line)
            self.y -= size + 3.5
            first = False
        self.y -= 1

    # -- writing space -----------------------------------------------------
    def lines(self, n=3, gap=22, label=None):
        if label:
            self.subheading(label)
        c = self.c
        c.setStrokeColor(LINE_GRAY)
        c.setLineWidth(0.6)
        for _ in range(n):
            self.need(gap)
            yy = self.y - gap + 6
            c.line(MARGIN, yy, PAGE_W - MARGIN, yy)
            self.y -= gap
        self.y -= 4

    def box(self, label, height=46, note=None):
        """Labeled blank box for free writing."""
        self.need(height + 22)
        c = self.c
        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(MARGIN, self.y - 11, label)
        self.y -= 15
        if note:
            c.setFillColor(GRAY)
            c.setFont("Helvetica-Oblique", 8.5)
            c.drawString(MARGIN, self.y - 9, note)
            self.y -= 11
        c.setStrokeColor(BOX_BORDER)
        c.setLineWidth(0.8)
        c.roundRect(MARGIN, self.y - height, CONTENT_W, height, 4, stroke=1, fill=0)
        self.y -= height + 10

    def checklist(self, items, cols=1, size=9.5):
        c = self.c
        if cols == 1:
            for it in items:
                self.need(size + 8)
                c.setStrokeColor(BOX_BORDER)
                c.setLineWidth(0.8)
                box = 9
                c.rect(MARGIN, self.y - box - 1, box, box, stroke=1, fill=0)
                c.setFillColor(TEXT)
                c.setFont("Helvetica", size)
                for i, line in enumerate(self._wrap(it, "Helvetica", size, CONTENT_W - 20)):
                    if i > 0:
                        self.need(size + 4)
                    c.drawString(MARGIN + 16, self.y - size + 1, line)
                    self.y -= size + 3
                self.y -= 3
        else:
            col_w = CONTENT_W / cols
            i = 0
            while i < len(items):
                row = items[i:i + cols]
                self.need(size + 10)
                base = self.y
                for j, it in enumerate(row):
                    x = MARGIN + j * col_w
                    c.setStrokeColor(BOX_BORDER)
                    c.setLineWidth(0.8)
                    c.rect(x, base - 9 - 1, 9, 9, stroke=1, fill=0)
                    c.setFillColor(TEXT)
                    c.setFont("Helvetica", size)
                    txt = it
                    while c.stringWidth(txt, "Helvetica", size) > col_w - 22 and len(txt) > 4:
                        txt = txt[:-2]
                    if txt != it:
                        txt = txt.rstrip() + "…"
                    c.drawString(x + 15, base - size + 1, txt)
                self.y = base - (size + 9)
                i += cols
            self.y -= 3

    def table(self, headers, col_widths, rows=4, row_h=26, header_bg=True):
        """Bordered tracking grid. `rows` = blank rows for the client to fill."""
        total = sum(col_widths)
        scale = CONTENT_W / total
        widths = [w * scale for w in col_widths]
        header_h = 20
        self.need(header_h + rows * row_h + 6)
        c = self.c
        x0 = MARGIN
        top = self.y
        # header row
        if header_bg:
            c.setFillColor(SUBTLE_BG)
            c.rect(x0, top - header_h, CONTENT_W, header_h, stroke=0, fill=1)
        c.setFillColor(TEAL_DARK)
        c.setFont("Helvetica-Bold", 8.5)
        cx = x0
        for h, w in zip(headers, widths):
            txt = h
            while c.stringWidth(txt, "Helvetica-Bold", 8.5) > w - 6 and len(txt) > 3:
                txt = txt[:-2]
            c.drawString(cx + 3, top - header_h + 6, txt if txt == h else txt + "…")
            cx += w
        # grid
        c.setStrokeColor(BOX_BORDER)
        c.setLineWidth(0.7)
        bottom = top - header_h - rows * row_h
        c.rect(x0, bottom, CONTENT_W, header_h + rows * row_h, stroke=1, fill=0)
        # column separators
        cx = x0
        for w in widths[:-1]:
            cx += w
            c.line(cx, bottom, cx, top)
        # row separators
        yy = top - header_h
        c.line(x0, yy, x0 + CONTENT_W, yy)
        for _ in range(rows):
            yy -= row_h
            c.setStrokeColor(LINE_GRAY)
            c.line(x0, yy, x0 + CONTENT_W, yy)
            c.setStrokeColor(BOX_BORDER)
        self.y = bottom - 12

    def scale_row(self, label, low="0", high="10"):
        """A 0-10 rating scale row."""
        self.need(24)
        c = self.c
        c.setFillColor(TEXT)
        c.setFont("Helvetica", 9.5)
        c.drawString(MARGIN, self.y - 10, label)
        # ticks on the right half
        sx = MARGIN + CONTENT_W * 0.52
        sw = CONTENT_W * 0.48
        n = 11
        c.setStrokeColor(BOX_BORDER)
        c.setLineWidth(0.7)
        yy = self.y - 12
        c.line(sx, yy, sx + sw, yy)
        for i in range(n):
            x = sx + sw * i / (n - 1)
            c.line(x, yy - 3, x, yy + 3)
        c.setFillColor(GRAY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(sx, yy - 11, low)
        c.drawCentredString(sx + sw, yy - 11, high)
        self.y -= 26

    def save(self):
        self.c.showPage()
        self.c.save()


# ----------------------------------------------------------------------------
# Worksheet builders — each is clinically grounded
# ----------------------------------------------------------------------------

def w_tipp(s):
    s.instructions(
        "TIPP is a DBT crisis-survival skill for rapidly lowering extreme emotional arousal "
        "when you are in crisis and cannot think clearly. Use it for short-term distress, then "
        "follow up with other coping skills. Check with a clinician before cold-water or intense "
        "exercise if you have a heart condition or eating disorder.")
    s.heading("T — Temperature")
    s.body("Change your body temperature with cold water to activate the dive reflex and slow your heart rate. "
           "Hold your breath and put your face in cold water (or a cold pack over your eyes/cheeks) for 30 seconds.")
    s.box("My plan for cold temperature change:", height=38)
    s.heading("I — Intense Exercise")
    s.body("Engage in brief, intense aerobic exercise (even 5–10 minutes) to expend the body's stored physical "
           "energy that accompanies strong emotion — jumping jacks, fast walking, running in place.")
    s.box("Intense exercise I can do right now:", height=38)
    s.heading("P — Paced Breathing")
    s.body("Slow your breathing to about 5–6 breaths per minute. Make your exhale longer than your inhale "
           "(e.g., breathe in for 4, out for 6) to engage the parasympathetic nervous system.")
    s.scale_row("Distress BEFORE paced breathing (0 = calm, 10 = crisis):")
    s.scale_row("Distress AFTER paced breathing:")
    s.heading("P — Paired Muscle Relaxation")
    s.body("While breathing out, tense a muscle group, notice the tension, then release and notice the difference. "
           "Work through the body — hands, arms, shoulders, face, legs.")
    s.lines(2, label="Which TIPP skill helped most, and when will I use it next?")


def w_dearman(s):
    s.instructions(
        "DEAR MAN is a DBT interpersonal-effectiveness skill for asking for something or saying no while "
        "keeping your self-respect and the relationship. Plan your script below before a difficult conversation.")
    s.box("Situation / what I want to ask for or decline:", height=40)
    s.heading("DEAR — What you say")
    s.subheading("D — Describe the facts (no judgment)")
    s.lines(2)
    s.subheading("E — Express your feelings and opinions (use 'I' statements)")
    s.lines(2)
    s.subheading("A — Assert your ask clearly (ask for what you want or say no plainly)")
    s.lines(2)
    s.subheading("R — Reinforce (explain the positive effect of getting what you ask for)")
    s.lines(2)
    s.heading("MAN — How you say it")
    s.bullet("Mindful — stay focused on your goal; use the 'broken record' and ignore attacks.")
    s.bullet("Appear confident — eye contact, steady voice, upright posture; no whispering or hedging.")
    s.bullet("Negotiate — be willing to give to get; offer alternatives and ask for other solutions.")
    s.box("My fallback / what I'm willing to negotiate:", height=40)


def w_please(s):
    s.instructions(
        "PLEASE is a DBT emotion-regulation skill that reduces emotional vulnerability by caring for your body. "
        "Track these basics for one week — when the body is depleted, emotions hit harder.")
    s.heading("PL — Treat PhysicaL illness")
    s.body("Take prescribed medication; see a doctor when needed. Untreated illness lowers emotional resilience.")
    s.lines(1)
    s.heading("E — Balanced Eating")
    s.body("Eat regularly and in a balanced way; avoid foods that make you feel overly emotional.")
    s.lines(1)
    s.heading("A — Avoid mood-Altering substances")
    s.body("Stay off non-prescribed drugs and limit alcohol — they destabilize mood and impair coping.")
    s.lines(1)
    s.heading("S — Balanced Sleep")
    s.body("Aim for the hours your body needs; keep a consistent sleep/wake schedule.")
    s.lines(1)
    s.heading("E — Exercise")
    s.body("Get some movement most days; even a short walk builds mastery and lifts mood.")
    s.heading("Weekly PLEASE tracker")
    s.table(["Day", "Meds", "Ate balanced", "No substances", "Sleep (hrs)", "Exercise"],
            [14, 14, 22, 22, 18, 18], rows=7, row_h=22)


def w_radical_acceptance(s):
    s.instructions(
        "Radical Acceptance is a DBT distress-tolerance skill: fully accepting reality as it is, without approving "
        "of it, to stop the added suffering that comes from fighting what cannot be changed. Acceptance is a "
        "practice you choose again and again.")
    s.box("The reality I am struggling to accept:", height=44)
    s.heading("Acceptance vs. fighting reality")
    s.body("Pain + non-acceptance = suffering. We cannot change the past or facts outside our control; refusing "
           "to accept them keeps us stuck. Acceptance frees energy to respond skillfully.")
    s.subheading("What part of this is outside my control?")
    s.lines(2)
    s.subheading("How have I been fighting reality (e.g., 'this shouldn't be', bitterness, avoidance)?")
    s.lines(2)
    s.subheading("What would change if I accepted the facts of this situation?")
    s.lines(2)
    s.heading("Turning the mind & willingness")
    s.body("Acceptance is a choice you renew. Notice when you've turned away from it and gently turn back. "
           "Practice a coping or 'half-smile / willing hands' posture as you read your acceptance statement.")
    s.box("My acceptance statement (e.g., 'I can accept that... even though it is painful'):", height=44)


def w_wise_mind(s):
    s.instructions(
        "Wise Mind is the DBT state where Reasonable Mind (logic, facts) and Emotion Mind (feelings, urges) "
        "overlap — calm, centered inner knowing. Use this sheet to notice which state you're in and access "
        "Wise Mind for a decision.")
    s.heading("States of Mind")
    s.subheading("Reasonable Mind — describe a recent moment of pure logic/facts:")
    s.lines(2)
    s.subheading("Emotion Mind — describe a recent moment driven by feelings/urges:")
    s.lines(2)
    s.subheading("Wise Mind — describe a time you 'just knew' the right thing calmly:")
    s.lines(2)
    s.heading("A current decision")
    s.box("The decision or situation I'm facing:", height=36)
    s.subheading("What does Emotion Mind say?")
    s.lines(2)
    s.subheading("What does Reasonable Mind say?")
    s.lines(2)
    s.subheading("Wise Mind practice: breathe in 'wise', out 'mind'; ask the question and listen.")
    s.box("What does my Wise Mind say?", height=44)


def w_check_the_facts(s):
    s.instructions(
        "Check the Facts is a DBT emotion-regulation skill: many emotions are driven by our thoughts and "
        "interpretations rather than the event itself. Examine the facts to see whether the emotion fits, "
        "then decide how to respond.")
    s.box("The event (just the facts, like a camera would record):", height=38)
    s.subheading("What emotion am I feeling, and how intense (0–100)?")
    s.lines(1)
    s.subheading("What am I assuming or interpreting about the event?")
    s.lines(2)
    s.subheading("What are the facts that support my interpretation?")
    s.lines(2)
    s.subheading("What are the facts that do NOT support it? Is there another explanation?")
    s.lines(2)
    s.subheading("Am I assuming a threat? How likely is the outcome I fear, really?")
    s.lines(2)
    s.heading("Does the emotion (and its intensity) fit the facts?")
    s.checklist(["Yes — the emotion fits; problem-solve or accept.",
                 "No / partly — practice opposite action and re-check the facts."])
    s.box("My next skillful step:", height=40)


def w_values(s):
    s.instructions(
        "In ACT, values are chosen life directions — not goals to complete, but qualities of how you want to "
        "live. Rate how important each domain is and how consistently you've been living it, then choose one "
        "small committed action.")
    s.heading("Life domains")
    s.body("For each domain, write a word or two about the kind of person you want to be there. "
           "Then rate Importance (1–10) and how well you're Living it now (1–10).")
    s.table(["Domain", "What matters here / who I want to be", "Import.", "Living"],
            [22, 56, 11, 11], rows=8, row_h=24)
    s.body("Domains: Family · Intimate relationships · Friendship · Work/Education · Health · "
           "Recreation/Fun · Personal growth/Spirituality · Community/Citizenship.", size=8.5)
    s.heading("Committed action")
    s.subheading("Which domain has the biggest gap between importance and living?")
    s.lines(1)
    s.box("One small, doable action this week that moves toward that value:", height=40)


def w_defusion(s):
    s.instructions(
        "Cognitive defusion (ACT) helps you unhook from sticky thoughts by changing your relationship to them "
        "rather than their content. You are not your thoughts — you are the one noticing them. Practice the "
        "techniques below with a real thought that hooks you.")
    s.box("A thought that hooks me (write it exactly as it shows up):", height=36)
    s.heading("Defusion techniques to try")
    s.bullet("Name the story: 'I'm having the thought that...' then 'I notice I'm having the thought that...'")
    s.bullet("Thank your mind: silently say 'Thanks, mind' for the warning, without obeying it.")
    s.bullet("Silly voice / singing: say the thought in a cartoon voice or sing it to a familiar tune.")
    s.bullet("Repeat a key word aloud for 30 seconds until it loses its meaning and becomes just a sound.")
    s.bullet("Leaves on a stream: picture each thought placed on a leaf and floating away.")
    s.subheading("How 'fused' was I with the thought before (0–10)?")
    s.lines(1)
    s.subheading("After practicing defusion, how 'fused' am I now (0–10)? What shifted?")
    s.lines(2)
    s.box("If this thought no longer ran the show, what valued action would I take?", height=40)


def w_breathing_bodyscan(s):
    s.instructions(
        "Mindful breathing and the body scan build present-moment awareness and down-regulate the stress "
        "response. There is no 'right' feeling — the practice is simply noticing and gently returning attention.")
    s.heading("Mindful breathing (5 minutes)")
    s.bullet("Sit comfortably, eyes soft or closed. Let the breath be natural — don't force it.")
    s.bullet("Notice where you feel the breath most clearly (nostrils, chest, or belly).")
    s.bullet("Silently count: in for 4, out for 6. When the mind wanders, label 'thinking' and return.")
    s.scale_row("Tension BEFORE breathing (0 = relaxed, 10 = very tense):")
    s.scale_row("Tension AFTER breathing:")
    s.heading("Body scan (10 minutes)")
    s.body("Slowly move attention through the body, pausing at each area. Notice sensations — warmth, tension, "
           "tingling, neutrality — with curiosity, not judgment. Breathe into areas of tightness and let them soften.")
    s.checklist(["Feet & legs", "Hips & lower back", "Belly & chest", "Hands & arms",
                 "Shoulders & neck", "Face & head"], cols=2)
    s.subheading("Where did I notice the most tension or sensation?")
    s.lines(2)
    s.subheading("What did I notice about my mind wandering, and how did I respond?")
    s.lines(2)


def w_observing_self(s):
    s.instructions(
        "The Observing Self (ACT) is the part of you that has been watching your experiences your whole life — "
        "the constant 'you' behind changing thoughts, feelings, and roles. 'Leaves on a Stream' is a practice "
        "for stepping back into that observer perspective.")
    s.heading("Leaves on a Stream — guided practice")
    s.bullet("Picture a gently flowing stream with leaves drifting on the surface.")
    s.bullet("For a few minutes, place each thought that arises onto a leaf and let it float by.")
    s.bullet("Don't speed up or slow the stream; don't push thoughts away. Just notice and place.")
    s.bullet("When you notice you've been swept downstream (lost in a thought), gently step back and resume.")
    s.subheading("How many times did I get 'hooked' and step back? What kinds of thoughts pulled me?")
    s.lines(2)
    s.heading("Noticing the Observing Self")
    s.body("Notice: the same 'you' that is aware right now is the 'you' that was aware as a child. Thoughts, "
           "feelings, and bodies change — the observer remains. This perspective is a safe place to stand.")
    s.box("Reflection: what is it like to be the one who notices, rather than the thoughts themselves?", height=50)


def w_window_tolerance(s):
    s.instructions(
        "The Window of Tolerance describes the zone of arousal where you can think, feel, and stay present. "
        "Above it is hyperarousal (fight/flight); below it is hypoarousal (freeze/shutdown). Mapping your "
        "signs and skills helps you stay in — or return to — the window.")
    s.heading("Hyperarousal (above the window)")
    s.body("Anxiety, panic, anger, racing thoughts, overwhelmed, on edge, can't sit still.")
    s.box("My signs of hyperarousal:", height=38)
    s.box("Skills to come DOWN (e.g., paced breathing, cold water, grounding, slow movement):", height=38)
    s.heading("Window of Tolerance (regulated)")
    s.body("Calm and alert, able to think clearly, feel emotions without being flooded, connect with others.")
    s.box("What being in my window feels like:", height=34)
    s.heading("Hypoarousal (below the window)")
    s.body("Numb, shut down, disconnected, foggy, exhausted, 'not really here', collapsed.")
    s.box("My signs of hypoarousal:", height=38)
    s.box("Skills to come UP (e.g., movement, cold/sour taste, 5-4-3-2-1, stand up, splash water):", height=38)


def w_grounding(s):
    s.instructions(
        "Grounding skills bring you back to the present moment during flashbacks, dissociation, panic, or "
        "overwhelming urges. They work by anchoring attention in the senses and the here-and-now. Practice "
        "them when calm so they're available in distress.")
    s.heading("5-4-3-2-1 sensory grounding")
    s.body("Name them out loud or write them down:")
    s.lines(1, label="5 things I can SEE")
    s.lines(1, label="4 things I can FEEL / TOUCH")
    s.lines(1, label="3 things I can HEAR")
    s.lines(1, label="2 things I can SMELL")
    s.lines(1, label="1 thing I can TASTE")
    s.heading("More grounding tools")
    s.checklist(["Hold something cold or textured", "Name today's date, place, and your age aloud",
                 "Press feet firmly into the floor", "Sip cold water slowly",
                 "Describe an object in detail", "Count backward from 100 by 7s",
                 "Notice 5 colors in the room", "Stretch and feel your muscles"], cols=2)
    s.box("Which grounding tools work best for me, and where will I keep this list?", height=42)


def w_grief(s):
    s.instructions(
        "Grief is love with nowhere to go — it has no fixed timeline or 'stages' to complete. 'Continuing bonds' "
        "means staying connected to who or what you lost in a way that honors them, rather than 'letting go'. "
        "Use this sheet gently and at your own pace.")
    s.box("Who or what I am grieving:", height=34)
    s.heading("Remembering")
    s.subheading("A memory I treasure:")
    s.lines(3)
    s.subheading("Something they taught me or that I carry forward from them:")
    s.lines(2)
    s.heading("Continuing the bond")
    s.subheading("Ways I can stay connected (rituals, talking to them, an object, a place, their values):")
    s.lines(3)
    s.box("Something I wish I could say to them now:", height=46)
    s.heading("Caring for myself in grief")
    s.subheading("What do I need today — and who can support me?")
    s.lines(2)


def w_trigger_tracking(s):
    s.instructions(
        "Tracking triggers builds awareness of what activates trauma responses or strong urges, and what helps. "
        "Over time, patterns emerge that you and your clinician can use to plan coping ahead of time.")
    s.heading("Trigger log")
    s.table(["Date/Time", "Trigger (what happened)", "Body/emotion response", "Coping I used", "Helped? 0-10"],
            [14, 30, 24, 22, 12], rows=6, row_h=30)
    s.heading("Patterns & planning")
    s.subheading("What triggers show up most often (people, places, sensations, times of day)?")
    s.lines(2)
    s.subheading("Earliest warning sign in my body that a trigger is building:")
    s.lines(1)
    s.box("My go-to coping plan when I notice that early warning sign:", height=44)


def w_anger_iceberg(s):
    s.instructions(
        "Anger is often the visible 'tip of the iceberg' — underneath it are softer or more vulnerable emotions "
        "that are harder to show. Identifying what's beneath your anger helps you respond to the real need.")
    s.heading("Above the surface")
    s.box("The situation, and how my anger showed up (words, tone, body, actions):", height=44)
    s.heading("Below the surface — what's underneath?")
    s.body("Check any feelings that may be hiding beneath the anger:")
    s.checklist(["Hurt", "Fear / anxiety", "Embarrassment / shame", "Disrespected",
                 "Sadness / grief", "Rejection", "Helplessness", "Guilt",
                 "Jealousy", "Disappointment", "Feeling unheard", "Overwhelm"], cols=3)
    s.subheading("Which of these feels most true right now, and what does it tell me I need?")
    s.lines(3)
    s.box("A more direct way to express the underlying feeling or need:", height=42)


def w_anger_timeout(s):
    s.instructions(
        "A time-out plan interrupts escalating anger before it leads to words or actions you regret. Plan it in "
        "advance with anyone it affects, so a time-out is understood as a coping skill — not walking away from "
        "the relationship.")
    s.heading("My early warning signs")
    s.body("Physical (e.g., clenched jaw, hot face, fast heart), thoughts, and behaviors that signal rising anger:")
    s.lines(3)
    s.scale_row("The anger number where I will call a time-out (0 = calm, 10 = explosive):")
    s.heading("My time-out steps")
    s.bullet("Signal: the word or gesture I'll use (e.g., 'I need a time-out').")
    s.bullet("Leave the situation calmly — no last word, no slamming.")
    s.bullet("How long I'll take: ____ minutes. Where I'll go: ____________________.")
    s.bullet("What I'll do to cool down (walk, paced breathing, cold water, NOT rumination or substances).")
    s.box("My specific cool-down activities:", height=40)
    s.heading("Coming back")
    s.subheading("How I'll return and re-engage respectfully once I'm under my anger number:")
    s.lines(2)


def w_emotion_log(s):
    s.instructions(
        "Daily emotion logging builds awareness of patterns between situations, emotions, intensity, and "
        "responses. Over a week, review for triggers and which coping skills actually helped.")
    s.heading("Daily emotion log")
    s.table(["Date", "Situation", "Emotion", "Intensity 0-10", "Thoughts/urges", "What I did"],
            [12, 26, 16, 14, 24, 22], rows=7, row_h=28)
    s.heading("Weekly review")
    s.subheading("My most frequent or intense emotion this week, and what tended to trigger it:")
    s.lines(2)
    s.subheading("Coping responses that helped vs. ones that made things worse:")
    s.lines(2)
    s.box("One thing I want to try differently next week:", height=40)


def w_accepts(s):
    s.instructions(
        "Distress tolerance skills help you get through a crisis without making it worse, when you can't fix the "
        "situation right now. ACCEPTS distracts; self-soothing uses the five senses. Plan yours in advance.")
    s.heading("ACCEPTS — Distract wisely")
    s.subheading("A — Activities (engaging things to do)")
    s.lines(1)
    s.subheading("C — Contributing (help someone, do something kind)")
    s.lines(1)
    s.subheading("C — Comparisons (to a time you coped, or to those coping with less)")
    s.lines(1)
    s.subheading("E — Emotions (opposite emotion: funny video, uplifting music)")
    s.lines(1)
    s.subheading("P — Pushing away (set the problem aside briefly; imagine a box on a shelf)")
    s.lines(1)
    s.subheading("T — Thoughts (count, puzzles, recite something)")
    s.lines(1)
    s.subheading("S — Sensations (hold ice, hot shower, strong taste)")
    s.lines(1)
    s.heading("Self-soothe with the five senses")
    s.table(["Vision", "Hearing", "Smell", "Taste", "Touch"],
            [20, 20, 20, 20, 20], rows=2, row_h=28)
    s.box("My crisis-survival kit — items/activities to keep ready:", height=42)


def w_self_esteem(s):
    s.instructions(
        "Low self-esteem narrows attention to faults and discounts strengths. This inventory helps you build a "
        "fairer, evidence-based view of yourself. If it feels hard, that's common — start small and be honest.")
    s.heading("Positive qualities inventory")
    s.body("List strengths, traits, skills, and values you have. If stuck, think how a good friend would describe you.")
    s.lines(4)
    s.heading("Evidence for my strengths")
    s.subheading("A time I showed one of these qualities (what I did and the result):")
    s.lines(3)
    s.heading("Reframing the inner critic")
    s.box("A harsh thing I say to myself:", height=32)
    s.box("What I'd say to a friend who believed that about themselves:", height=40)
    s.heading("Affirmations I can believe")
    s.body("Write 2–3 realistic, kind statements about yourself (not hype — things you can actually accept):")
    s.lines(3)


def w_assertive(s):
    s.instructions(
        "Assertive communication expresses your needs and feelings honestly while respecting others — the "
        "middle ground between passive (silencing yourself) and aggressive (steamrolling others). 'I-statements' "
        "are its core tool.")
    s.heading("Communication styles")
    s.bullet("Passive: avoid, give in, hint — needs go unmet, resentment builds.")
    s.bullet("Aggressive: blame, demand, attack — others get hurt, relationships strain.")
    s.bullet("Assertive: clear, calm, respectful — 'I feel ___ when ___ because ___. I'd like ___.'")
    s.heading("Build an I-statement")
    s.box("Situation:", height=32)
    s.subheading("I feel... (name the emotion)")
    s.lines(1)
    s.subheading("...when... (describe the behavior/facts, not the person)")
    s.lines(1)
    s.subheading("...because... (the effect on me)")
    s.lines(1)
    s.subheading("I'd like / I would appreciate... (a clear, specific request)")
    s.lines(2)
    s.heading("Practice")
    s.box("Rewrite a recent passive or aggressive moment as an assertive I-statement:", height=46)


def w_urge_surfing(s):
    s.instructions(
        "Urges rise, peak, and fall like a wave — they always pass, whether or not you act on them. 'Urge "
        "surfing' means riding the wave with mindful awareness instead of fighting or giving in. HALT flags four "
        "states that make urges stronger.")
    s.heading("HALT check — am I...")
    s.checklist(["Hungry", "Angry", "Lonely", "Tired"], cols=4)
    s.subheading("If any are checked, what can I do to address that need first?")
    s.lines(2)
    s.heading("Surf the urge")
    s.box("The urge I'm noticing (substance, behavior, etc.):", height=30)
    s.scale_row("Urge intensity at its peak (0 = none, 10 = overpowering):")
    s.bullet("Notice where you feel the urge in your body; describe it like a curious observer.")
    s.bullet("Breathe with it. Remind yourself: urges peak and pass, usually within 20–30 minutes.")
    s.bullet("Don't fight or feed it — just watch the wave rise and fall.")
    s.subheading("How long did the urge take to ease, and what helped me ride it out?")
    s.lines(2)
    s.box("My plan / supports for next time an urge hits:", height=40)


def w_sleep(s):
    s.instructions(
        "Sleep hygiene is a set of habits that support healthy sleep. Pick a few changes to focus on rather than "
        "all at once. If sleep problems persist despite good habits, talk with your clinician.")
    s.heading("Sleep hygiene checklist")
    s.checklist([
        "Consistent wake time, 7 days a week",
        "No screens 30–60 min before bed",
        "Bedroom dark, cool, and quiet",
        "Caffeine cut off by early afternoon",
        "No large meals or alcohol close to bedtime",
        "Bed used for sleep only (not work/scrolling)",
        "Wind-down routine (reading, stretching, breathing)",
        "Get up if awake >20 min, return when sleepy",
        "Daytime light exposure / movement",
        "Limit naps to early afternoon, under 30 min",
    ])
    s.heading("My sleep plan")
    s.subheading("My target bedtime and wake time:")
    s.lines(1)
    s.box("Two or three habits I will change this week:", height=40)
    s.heading("Simple sleep diary (1 week)")
    s.table(["Day", "Bedtime", "Wake time", "Hrs slept", "Quality 1-5", "Notes"],
            [12, 16, 16, 14, 16, 26], rows=7, row_h=22)


def w_gratitude(s):
    s.instructions(
        "Regularly noticing good moments and doing pleasant or meaningful activities (behavioral activation) "
        "counteracts the negativity bias and lifts mood over time. Aim for specifics — small and genuine beats "
        "big and forced.")
    s.heading("Daily gratitude")
    s.body("Each day, write three specific things you're grateful for and why they mattered.")
    s.table(["Day", "Three good things (and why they mattered)"],
            [14, 86], rows=7, row_h=30)
    s.heading("Positive activity log")
    s.body("Plan and rate pleasant or meaningful activities. Note mood before and after (0–10).")
    s.table(["Activity", "Planned day", "Mood before", "Mood after"],
            [44, 22, 17, 17], rows=6, row_h=24)
    s.subheading("Which activities lifted my mood most? When can I do more of them?")
    s.lines(2)


# ----------------------------------------------------------------------------
# Registry — (subfolder, filename, title, builder)
# ----------------------------------------------------------------------------
WORKSHEETS = [
    # DBT Skills
    ("dbt", "tipp-crisis-survival.pdf", "TIPP — Crisis Survival Skills", w_tipp),
    ("dbt", "dear-man.pdf", "DEAR MAN — Interpersonal Effectiveness", w_dearman),
    ("dbt", "please-emotion-regulation.pdf", "PLEASE — Reducing Emotional Vulnerability", w_please),
    ("dbt", "radical-acceptance.pdf", "Radical Acceptance", w_radical_acceptance),
    ("dbt", "wise-mind.pdf", "Wise Mind & States of Mind", w_wise_mind),
    ("dbt", "check-the-facts.pdf", "Check the Facts", w_check_the_facts),
    # ACT & Mindfulness
    ("act", "values-clarification.pdf", "Values Clarification", w_values),
    ("act", "cognitive-defusion.pdf", "Cognitive Defusion Practice", w_defusion),
    ("act", "mindful-breathing-body-scan.pdf", "Mindful Breathing & Body Scan", w_breathing_bodyscan),
    ("act", "observing-self-leaves.pdf", "The Observing Self — Leaves on a Stream", w_observing_self),
    # Trauma & Grief
    ("trauma", "window-of-tolerance.pdf", "Window of Tolerance", w_window_tolerance),
    ("trauma", "grounding-skills.pdf", "Grounding Skills", w_grounding),
    ("trauma", "grief-continuing-bonds.pdf", "Grief Processing & Continuing Bonds", w_grief),
    ("trauma", "trigger-tracking.pdf", "Trigger Tracking & Coping Log", w_trigger_tracking),
    # Emotion & Anger
    ("skills", "anger-iceberg.pdf", "The Anger Iceberg", w_anger_iceberg),
    ("skills", "anger-time-out-plan.pdf", "Anger Time-Out Plan", w_anger_timeout),
    ("skills", "distress-tolerance-accepts.pdf", "Distress Tolerance — ACCEPTS & Self-Soothe", w_accepts),
    # Self-Esteem, Communication & Recovery
    ("recovery", "self-esteem-inventory.pdf", "Self-Esteem & Positive Qualities Inventory", w_self_esteem),
    ("recovery", "assertive-communication.pdf", "Assertive Communication & I-Statements", w_assertive),
    ("recovery", "urge-surfing-halt.pdf", "Urge Surfing & HALT", w_urge_surfing),
    ("recovery", "sleep-hygiene-plan.pdf", "Sleep Hygiene Plan", w_sleep),
    ("recovery", "gratitude-positive-activity.pdf", "Gratitude & Positive Activity Log", w_gratitude),
]


def main():
    generated = []
    for sub, fname, title, builder in WORKSHEETS:
        out_dir = os.path.join(ROOT, "pdfs", sub)
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, fname)
        sheet = Sheet(path, title)
        builder(sheet)
        sheet.save()
        rel = "pdfs/%s/%s" % (sub, fname)
        generated.append((rel, path))
        print("  generated", rel)
    print("\nTotal worksheets generated:", len(generated))
    return generated


if __name__ == "__main__":
    main()
