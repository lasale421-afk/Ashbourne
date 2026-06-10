import pygame

# ── Dialogue Scripts ──────────────────────────────────────────────────────────
# Each entry is a list of pages; each page is a list of lines.
# Special entries: {"choice": [...]} triggers a choice menu.

DIALOGUES = {
    "maren": {
        "default": [
            ["Maren looks up from a stack of papers.",
             "\"You made it back. Good.\""],
            ["\"The Undercroft entrance is at the south wall.",
             "Whatever came through ten years ago — it's still down there.",
             "The Order sealed it rather than destroyed it.\""],
            ["\"I've been trying to find out why.",
             "There are records missing. Deliberately removed.\""],
            ["\"Be careful. The things down there aren't",
             "just dangerous. They're patient.\""],
        ],
        "after_district_1": [
            ["Maren examines the Warden's Seal you brought back.",
             "Her expression doesn't change."],
            ["\"They sealed it because destroying it would have",
             "collapsed the district. Or so the logbook says.\""],
            ["\"The Order made a choice. Protect the city above,",
             "let something live beneath it.\""],
            ["\"The Merchant Quarter is next.",
             "I've heard things about the Broker.\""],
        ],
        "after_district_2": [
            ["Maren looks at you with something like respect."],
            ["\"The Broker is dead. The Merchant Quarter is safe.\""],
            ["\"But there's one more thing. The Spire. The old Order headquarters.\""],
            ["\"The Last Captain is still in there. Sealed himself in ten years ago.\""],
            ["\"You need to find him. And the truth about what the Order chose.\""],
        ],
        "after_district_3": [
            ["Maren is waiting for you at the center of the post."],
            ["\"The Captain. You found him. You know what the Order did.\""],
            ["\"The original Crack. It's still there. Still sealed.\""],
            ["\"The same choice. The same math. The city or the truth.\""],
            ["\"It's your choice now. The Crack is at the north wall.\""],
        ],
        "shop": [
            ["\"I have supplies. Take what you need.\""],
        ],
    },
    "notice_board": {
        "default": [
            ["WARDEN'S POST — NOTICE BOARD",
             "————————————————————————"],
            ["Active investigations will appear here.",
             "Report completed work to Maren."],
        ],
    },
    "tunnel": {
        "default": [
            ["A collapsed tunnel. Order markings on the stone.",
             "Someone sealed this deliberately."],
        ],
    },
    "dead_warden": {
        "default": [
            ["A warden's body. Dead for years.",
             "In the coat pocket: a sealed logbook."],
        ],
    },
    "chest": {
        "default": [
            ["You open the chest."],
        ],
        "empty": [
            ["The chest is empty."],
        ],
    },
    "portal_locked": {
        "default": [
            ["This district is not yet accessible.",
             "Complete the Undercroft first."],
        ],
    },
    "broker_contact_choice": {
        "choice": {
            "prompt": ["The Broker's contact. He knows you know.",
                       "He's sweating.",
                       "\"We can work something out,\" he says."],
            "options": [
                {"label": "Expose him to the district.",
                 "result": "expose",
                 "response": ["You turn him in.",
                              "He's arrested before sundown.",
                              "Maren hears about it. She nods once."]},
                {"label": "Accept his payment. Let him disappear.",
                 "result": "silence",
                 "response": ["He counts out the gold.",
                              "+150 gold. He's gone by morning.",
                              "Maren never finds out."]},
            ],
        },
    },
    "crack_broker": {
        "default": [
            ["The Broker stands here. Not as an enemy. As a witness."],
            ["\"I made a deal. The city survived. That's the math.\""],
            ["\"You want to blame me? Fine. But the cracks would have won without me.\""],
        ],
    },
    "crack_first": {
        "default": [
            ["The First Crack. The original. It doesn't attack."],
            ["It just... waits. Patient. Like it always was."],
            ["\"You could seal me again. Or you could end it.\""],
        ],
    },
    "crack_captain": {
        "default": [
            ["The Last Captain. He's different here."],
            ["\"I sealed myself in. I thought that was the end.\""],
            ["\"But you kept coming. You kept looking.\""],
            ["\"The Crack is the same choice. The city or the truth.\""],
            ["\"I've made my choice. Now you make yours.\""],
        ],
    },
    "captain_dialogue": {
        "talk": [
            ["The Last Captain doesn't raise his weapon.",
             "\"You found me. I wondered if anyone would.\""],
            ["\"The Order is gone because of what we decided.",
             "We chose silence. We chose the city over the truth.\""],
            ["\"I sealed myself in as penance.",
             "I didn't think anyone would come looking.\""],
            ["\"You've read the journals. You know what I know.",
             "Take the blade. You'll need it.\""],
        ],
        "fight": [
            ["The Captain raises his weapon.",
             "\"Then we do it the hard way.\""],
        ],
    },
    "crack_ending": {
        "seal": [
            ["You stand at the original crack.",
             "The same choice. The same math."],
            ["Seal it. Buy another ten years.",
             "The city survives. For now."],
            ["Behind you, Maren watches.",
             "She doesn't speak.",
             "The look on her face says enough."],
        ],
        "destroy": [
            ["You push past the seal.",
             "The crack tears open."],
            ["The collapse is fast.",
             "One district. Empty blocks, mostly. Some weren't."],
            ["The cracks stop.",
             "Permanently.",
             "Some things end cleanly. Most don't."],
        ],
    },
}


class DialogueManager:
    def __init__(self, font_small, font_med, screen_w, screen_h):
        self.font_small = font_small
        self.font_med   = font_med
        self.sw = screen_w
        self.sh = screen_h
        self.active = False
        self.pages   = []
        self.page_idx = 0
        self.choice_data = None
        self.choice_sel  = 0
        self.on_choice   = None   # callback(result)
        self.on_done     = None   # callback()
        self.speaker     = ""
        self._anim_timer = 0
        self._anim_chars = 0

    def start(self, pages, speaker="", on_done=None):
        self.pages    = pages
        self.page_idx = 0
        self.active   = True
        self.speaker  = speaker
        self.choice_data = None
        self.on_done  = on_done
        self._anim_chars = 0
        self._anim_timer = 0

    def start_choice(self, prompt_lines, options, speaker="", on_choice=None, on_done=None):
        self.active      = True
        self.pages       = [prompt_lines]
        self.page_idx    = 0
        self.choice_data = options
        self.choice_sel  = 0
        self.speaker     = speaker
        self.on_choice   = on_choice
        self.on_done     = on_done
        self._anim_chars = 0
        self._anim_timer = 0

    def advance(self):
        if not self.active:
            return
        current = self.pages[self.page_idx] if self.page_idx < len(self.pages) else []
        full_text = " ".join(current)
        if self._anim_chars < len(full_text):
            self._anim_chars = len(full_text)
            return
        if self.choice_data and self.page_idx == len(self.pages) - 1:
            return
        self.page_idx += 1
        self._anim_chars = 0
        if self.page_idx >= len(self.pages):
            if not self.choice_data:
                self.active = False
                if self.on_done:
                    self.on_done()

    def select_choice(self):
        if not self.choice_data:
            return
        opt = self.choice_data[self.choice_sel]
        if self.on_choice:
            self.on_choice(opt["result"], opt.get("response", []))
        self.active = False
        if self.on_done:
            self.on_done()

    def handle_input(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if self.choice_data and self.page_idx == len(self.pages) - 1:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.choice_sel = max(0, self.choice_sel - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.choice_sel = min(len(self.choice_data) - 1, self.choice_sel + 1)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
                    self.select_choice()
            else:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e,
                                 pygame.K_z):
                    self.advance()
            return True
        return False

    def update(self, dt):
        if not self.active or self.choice_data:
            return
        self._anim_timer += dt
        if self._anim_timer >= 0.02:
            self._anim_timer = 0
            self._anim_chars += 1

    def draw(self, surface):
        if not self.active:
            return
        bw = self.sw - 80
        bh = 160
        bx = 40
        by = self.sh - bh - 30
        # Box background
        overlay = pygame.Surface((bw, bh), pygame.SRCALPHA)
        overlay.fill((10, 8, 6, 220))
        surface.blit(overlay, (bx, by))
        pygame.draw.rect(surface, (120, 100, 70), (bx, by, bw, bh), 2)

        # Speaker name
        if self.speaker:
            name_surf = self.font_med.render(self.speaker, True, (200, 170, 100))
            surface.blit(name_surf, (bx + 12, by + 8))
            text_y = by + 34
        else:
            text_y = by + 12

        # Dialogue text with typewriter effect
        if self.page_idx < len(self.pages):
            lines = self.pages[self.page_idx]
            full_text = " ".join(lines)
            visible = full_text[:self._anim_chars] if self._anim_chars < len(full_text) else full_text
            self._draw_wrapped(surface, visible, bx + 12, text_y, bw - 24, bh - 60)

        # Choice menu
        if self.choice_data and self.page_idx == len(self.pages) - 1:
            choice_y = by + bh - len(self.choice_data) * 22 - 10
            for i, opt in enumerate(self.choice_data):
                color = (220, 200, 120) if i == self.choice_sel else (140, 130, 110)
                prefix = "> " if i == self.choice_sel else "  "
                surf = self.font_small.render(prefix + opt["label"], True, color)
                surface.blit(surf, (bx + 16, choice_y + i * 22))
        else:
            # Continue prompt
            if self._anim_chars >= len(" ".join(self.pages[self.page_idx]
                                                 if self.page_idx < len(self.pages) else [""])):
                prompt = self.font_small.render("[SPACE / E]", True, (120, 110, 90))
                surface.blit(prompt, (bx + bw - prompt.get_width() - 12,
                                      by + bh - 20))

    def _draw_wrapped(self, surface, text, x, y, max_width, max_height):
        words = text.split()
        line = ""
        line_y = y
        for word in words:
            test = line + (" " if line else "") + word
            if self.font_small.size(test)[0] > max_width:
                surf = self.font_small.render(line, True, (200, 195, 185))
                surface.blit(surf, (x, line_y))
                line_y += 20
                line = word
                if line_y > y + max_height:
                    break
            else:
                line = test
        if line:
            surf = self.font_small.render(line, True, (200, 195, 185))
            surface.blit(surf, (x, line_y))
