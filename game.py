# This is pure hardwork without any borrowed code. :)

import json
import time
from typing import List, Tuple
from black import os

import pygame
import pygame.mixer

__version__ = "1.0.0"


def analyze(asm: str) -> dict:
    """
    Analyzes given assembly instructions and returns
    an analysis for label line locations, errors in
    instructions.

    For example given the following

    ```asm
    #loop
    add a1 a2 0
    jump loop
    ```

    should return

    ```json
    {
        "labels": {
            "loop": 0
        }
    }
    ```
    """
    d = {"labels": {}}
    for i, x in enumerate(asm.splitlines()):
        x = x.strip()
        if x == "":
            pass
        if x.startswith("#"):
            d["labels"][x[1:]] = i


class TextButton:
    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color=(0, 0, 0),
        hover_color=(255, 255, 255),
        dest=(0, 0),
        invis_width=0,
        padding_h=20,
        padding_w=30,
        event=None,
        centering: bool = True,
        bottom_aligned: bool = False,
    ):
        self.text_normal = font.render(text, False, (hover_color))
        self.text_hover = font.render(text, False, color)
        self.mouse_down = False
        self.rect = self.text_normal.get_rect()
        self.outer_rect = self.text_normal.get_rect()
        self.outer_rect.width += padding_w
        self.outer_rect.height += padding_h
        if invis_width == 0:
            invis_width = self.outer_rect.width + dest[0] * 2
        self.outer_outer_rect = pygame.Rect(
            (
                0,
                dest[1]
                - (
                    (self.outer_rect.h // 2)
                    if centering
                    else self.outer_rect.h
                    if bottom_aligned
                    else 0
                ),
            ),
            (invis_width, self.outer_rect.height),
        )
        self.outer_rect.center = self.outer_outer_rect.center
        self.rect.center = self.outer_rect.center
        self.color = color
        self.hover = False
        self.hover_color = hover_color
        self.event_bind = event

    def render(self, surf: pygame.Surface):
        if (self.mouse_down and self.hover) or not self.hover:
            surf.fill((self.color), self.outer_rect)
            surf.blit(self.text_normal, self.rect)
            pygame.draw.rect(surf, self.hover_color, self.outer_rect, 1)
        else:
            surf.fill((self.hover_color), self.outer_rect)
            surf.blit(self.text_hover, self.rect)
            # pygame.draw.rect(surf, self.hover_color, self.outer_rect, 1)

    def mouse_button(self, x: int, y: int, mouse: bool):
        self.mouse_down = mouse
        self.mouse_hover(x, y)
        if not mouse and self.hover and self.event_bind is not None:
            self.event_bind()
            self.hover = False

    def mouse_hover(self, x: int, y: int):
        if self.outer_rect.collidepoint(x, y):
            self.hover = True
        else:
            self.hover = False


class Label:
    def __init__(
        self,
        text: str,
        font: pygame.font.Font,
        color=(255, 255, 255),
        invis_width=0,
        dest=(0, 0),
    ):
        self.text_normal = font.render(text, False, color)
        self.rect = self.text_normal.get_rect()
        self.outer_rect = pygame.Rect(0, dest[1] - self.rect.h // 2, invis_width, 0)
        self.rect.center = self.outer_rect.center

    def render(self, surf: pygame.Surface):
        surf.blit(self.text_normal, self.rect)

    def mouse_button(self, _x: int, _y: int, _bool: bool):
        pass

    def mouse_hover(self, _x: int, _y: int):
        pass


def load_sprite_sheet(frame_size: Tuple[int, int], file: str) -> List[pygame.Surface]:
    width, height = frame_size
    im = pygame.image.load(file)
    number_of_frames = int(im.get_width() / width)
    frames = []
    for x in range(number_of_frames):
        dst = pygame.Surface(frame_size, pygame.SRCALPHA)
        dst.blit(im, (0, 0), pygame.Rect(width * x, 0, width, height))
        frames.append(dst)
    return frames


class GameSave:
    def __init__(self):
        home = os.path.expanduser("~/.config/progventures")
        os.makedirs(home, exist_ok=True)
        if not os.path.exists(home + "/gamesave.json"):
            with open(home + "/gamesave.json", "w") as file:
                json.dump({"unlock_level": 0}, file)
        with open(home + "/gamesave.json", "r") as file:
            info = json.load(file)
            self.unlock_level = info["unlock_level"]


class Game:
    def __init__(
        self, window: pygame.Surface, fps: int, ppcm: int, font: str
    ):  # This is where all the assets are really loaded. Too long for a init function
        self.gamesave = GameSave()
        self.window = window
        self.font = font
        self.window.fill((0, 0, 0))
        self.text_renderer = pygame.font.Font(font, ppcm)

        loading_text = self.text_renderer.render("Booting", False, (255, 255, 255))
        loading_text_rect = loading_text.get_rect()
        loading_text_rect.center = self.window.get_rect().center

        self.window.blit(loading_text, loading_text_rect)

        pygame.mixer.music.load("assets/music/startup_start.mp3")
        pygame.mixer.music.play()
        pygame.mixer.music.queue("assets/music/startup_loop.mp3", loops=-1)

        pygame.display.update()

        self.height = window.get_height()
        self.width = window.get_width()
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.ppcm = ppcm
        self.text_rendererx3 = pygame.font.Font(font, ppcm * 3)
        self.text_rendererh2 = pygame.font.Font(font, ppcm // 2)

        self.scene = "mainmenu"
        self.cursor_state = "up"
        self.running = False

        def evt_start():
            self.scene = "stageselect"

        def evt_quit():
            self.running = False

        # Component Main Menu
        self.mainmenu_buttons = {
            "label": Label(
                "Progventures",
                self.text_rendererx3,
                invis_width=self.width,
                dest=(0, (self.height // 3)),
            ),
            "start": TextButton(
                "Start",
                self.text_renderer,
                invis_width=self.width,
                dest=(
                    self.width // 2,
                    self.height // 2.5 + 0 * (ppcm + int(0.1 * ppcm)),
                ),
                padding_h=0,
                event=evt_start,
            ),
            "about": TextButton(
                "About",
                self.text_renderer,
                invis_width=self.width,
                dest=(
                    self.width // 2,
                    (self.height // 2.5) + 1 * (ppcm + int(0.1 * ppcm)),
                ),
                padding_h=0,
            ),
            "tutorial": TextButton(
                "Tutorial",
                self.text_renderer,
                invis_width=self.width,
                dest=(
                    self.width // 2,
                    (self.height // 2.5) + 2 * (ppcm + int(0.1 * ppcm)),
                ),
                padding_h=0,
            ),
            "help": TextButton(
                "Help",
                self.text_renderer,
                invis_width=self.width,
                dest=(
                    self.width // 2,
                    (self.height // 2.5) + 3 * (ppcm + int(0.1 * ppcm)),
                ),
                padding_h=0,
            ),
            "quit": TextButton(
                "Quit",
                self.text_renderer,
                invis_width=self.width,
                dest=(
                    self.width // 2,
                    (self.height // 2.5) + 4 * (ppcm + int(0.1 * ppcm)),
                ),
                padding_h=0,
                event=evt_quit,
            ),
        }
        self.version_text = self.text_rendererh2.render(
            "v" + __version__, False, (255, 255, 255)
        )
        self.version_text_rect = self.version_text.get_rect()
        self.version_text_rect.bottomright = (self.width - 1, self.height - 1)

        # Cursor Setup
        self.cursor = load_sprite_sheet((24, 24), "assets/images/cursor.png")
        for i, im in enumerate(self.cursor):
            self.cursor[i] = pygame.transform.scale2x(im)
        self.cursor_name = ["up", "down"]
        self.cursor_pos = (0, 0)

        # Logo Setup # Scene "stageselect"
        logos = load_sprite_sheet((32, 32), "assets/images/logo.png")
        self.logo_names = logo_names = [
            "helios",
            "dos",
            "win95",
            "osx",
            "windows",
            "freebsd",
            "macos",
            "linux",
        ]
        self.logos = {
            k: pygame.transform.scale(
                v, (int(0.3 * self.height), int(0.3 * self.height))
            )
            for k, v in zip(logo_names, logos)
        }
        self.logo_information = {
            "helios": {
                "company": "SoftCorp",
                "name": "Helios 1.0",
                "year": "1970",
                "security-level": "0",
                "security-measures": ["Null"],
                "isa": ["Base"],
                "weakness": ["Buffer Overflow", "Fibinocci Password"],
            },  # Helios 1.0
            "dos": {
                "company": "MicroSoft",
                "name": "MS DOS",
                "year": "1981",
                "security-level": "1",
                "security-measures": ["CipherPass 1.0"],
                "isa": ["Base", "IO", "SysCall"],
                "weakness": [
                    "Buffer Overflow",
                    "CipherBased Password",
                    "Disk Unencrypted",
                ],
            },  # MS DOS
            "win95": {
                "company": "MicroSoft",
                "name": "Windows 95",
                "year": "1995",
                "security-level": "3",
                "security-measures": ["Passcryption 8-bit"],
                "isa": ["Base", "IO", "SysCall", "32-bit Ext"],
                "weakness": [
                    "Buffer Overflow",
                    "Password 8-bit",
                    "No Limit Password",
                    "Disk Unencrypted",
                ],
            },  # Windows 95
            "osx": {
                "company": "Apple Inc.",
                "name": "Mac OS X",
                "year": "2001",
                "security-level": "3",
                "security-measures": ["iPassword 32-bit", "iPhoneUnlock 1.0"],
                "isa": ["Base", "IO", "SysCall", "32-bit Ext", "DualCore"],
                "weakness": [
                    "iPhoneUnlock Immitation",
                    "DualCore Race Condition",
                    "FBI Backdoor",
                ],
            },  # OS X
            "windows": {
                "company": "MicroSoft",
                "name": "Windows 10",
                "year": "2015",
                "security-level": "6",
                "security-measures": [
                    "Wincrypt AES",
                    "Windows Hello",
                    "FingerLock 1.0 (TM)",
                    "DiscCrypt32",
                ],
                "isa": ["Base", "IO", "SysCall", "64-bit Ext", "OctaCore"],
                "weakness": [
                    "Malformed URL",
                    "Memory Leaks",
                    "FBI Backdoor",
                    "Scammers",
                    "Common Passwords",
                ],
            },  # Windows 10
            "freebsd": {
                "company": "Community",
                "name": "FreeBSD 12",
                "year": "2018",
                "security-level": "7",
                "security-measures": [
                    "LibreCrypt AES64",
                    "LibreHash256",
                    "DNS over SSL",
                    "Https",
                    "BinGPG",
                    "Firewalld",
                ],
                "isa": [
                    "Base",
                    "IO",
                    "SysCall",
                    "64-bit Ext",
                    "SingleRegister",
                    "SecureReg",
                ],
                "weakness": ["RegisterOverflow", "Log4j", "DDOS"],
            },  # FreeBSD 12
            "macos": {
                "company": "Apple Inc.",
                "name": "MacOS BigSur",
                "year": "2020",
                "security-level": "8",
                "security-measures": [
                    "Secure Enclave",
                    "Aarch64",
                    "AES.64",
                    "iCrypt 3000",
                ],
                "isa": [
                    "BaseT2",
                    "BaseMathT2",
                    "EnclaveIO",
                    "Syscall",
                    "Redundent Registers",
                    "ECC Memory",
                ],
                "weakness": [
                    "No Password",
                    "EFI Partition Mounted",
                    "Bootloader Debug Symbols",
                ],
            },  # MacOS BigSur
            "linux": {
                "company": "Linux Foundation",
                "name": "Linux 5.16 (Arch)",
                "year": "2022",
                "security-level": "10",
                "security-measures": [
                    "Ram Sweeper",
                    "GPG Verify",
                    "Time Limited Execution",
                    "Process Monitor",
                    "512-bit Password",
                ],
                "isa": [
                    "BaseT2",
                    "BaseMathT2",
                    "HubIO",
                    "Verified Syscall",
                    "Network",
                    "CSR",
                    "GPU",
                ],
                "weakness": ["SIGKILL", "Log4j", "Ram Overload", "HDD Swapfile"],
            },  # Linux 5.16
        }
        self.logo_visible_rect = pygame.Rect(
            0, 0, int(0.3 * self.height), int(0.3 * self.height)
        )
        self.logo_visible_bound_rect = pygame.Rect(
            0, 0, int(0.3 * self.height) + 20, int(0.3 * self.height) + 20
        )
        self.logo_visible_rect.center = (self.width // 2, self.height // 2)
        self.logo_visible_bound_rect.center = (self.width // 2, self.height // 2)
        self.current_logo_index = 0
        self.logo_frames = []

        self.info_text = self.text_renderer.render("OS Info", False, (255, 255, 255))
        self.target_environment = self.text_renderer.render(
            "Target", False, (255, 255, 255)
        )
        self.target_environment_rect = self.target_environment.get_rect()
        self.target_environment_rect.topright = (self.width - 10, 10)

        for (
            i,
            x,
        ) in (
            self.logo_information.items()
        ):  # Render static components of stageselect to convert CPU consumption to RAM consumption
            frame = pygame.Surface((self.width, self.height))
            frame.fill((0, 0, 0))
            frame.blit(self.logos[i], self.logo_visible_rect)
            pygame.draw.rect(frame, (255, 255, 255), self.logo_visible_bound_rect, 1)
            info = x
            nl = "\n\t* "
            info_to_show = f"""Company: {info["company"]}
Release: {info["year"]}
Name: {info["name"]}

Security Level: [{('='*int(info["security-level"])).ljust(10)}]
Security Measures:{nl+nl.join(info["security-measures"])}"""
            info2 = f"""ISA: {nl+nl.join(info["isa"])}

Weakness: {nl+nl.join(info["weakness"])}"""
            info2 = info2.splitlines()
            surf2 = pygame.Surface((self.width, self.height))
            info_to_show = info_to_show.splitlines()
            h = 20
            max_w = 0
            for line in info_to_show:
                surf = self.text_rendererh2.render(
                    line,
                    False,
                    (255, 255, 255),
                )
                frame.blit(surf, (20, h + self.ppcm + 10))
                h += surf.get_height()
                max_w = max(max_w, surf.get_width())
            max_w += 20
            info_rect = pygame.Rect(10, 20 + self.ppcm, max_w, h)
            pygame.draw.rect(frame, (255, 255, 255), info_rect, 1)
            h = 0
            max_w = 0
            for line in info2:
                surf = self.text_rendererh2.render(line, False, (255, 255, 255))
                surf2.blit(surf, (0, h))
                h += surf.get_height()
                max_w = max(max_w, surf.get_width())
            info2_rect = pygame.Rect(
                self.width - max_w - 30, 20 + self.ppcm, max_w + 20, h + 20
            )
            info2_dest = pygame.Rect(self.width - max_w - 20, 30 + self.ppcm, 0, 0)
            frame.blit(surf2, info2_dest)
            pygame.draw.rect(frame, (255, 255, 255), info2_rect, 1)
            frame.blit(self.info_text, (10, 10))
            frame.blit(self.target_environment, self.target_environment_rect)

            self.logo_frames.append(frame)

        # Stageselect Controls notifier
        self.controls_text = self.text_renderer.render("<-", False, (255, 255, 255))
        self.controls_text2 = self.text_renderer.render("->", False, (255, 255, 255))
        self.controls_text2_rect = self.controls_text2.get_rect()
        self.controls_text2_rect.bottomright = (self.width - 10, self.height - 10)
        self.controls_text_rect = self.controls_text.get_rect()
        self.controls_text_rect.bottomleft = (
            self.controls_text2_rect.left - 60,
            self.height - 10,
        )

        # Stageselect back to main menu
        def evt_main_menu():
            self.scene = "mainmenu"

        self.stageselect_back = TextButton(
            "Back",
            self.text_renderer,
            dest=(10, self.height - 10),
            padding_h=0,
            padding_w=10,
            centering=False,
            bottom_aligned=True,
            event=evt_main_menu,
        )

        # End of loading
        time.sleep(2)
        pygame.mixer.music.pause()
        pygame.mixer.music.load("assets/music/startup_end.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.music.unload()

    def start(self):
        pygame.mixer.music.load("assets/music/background_retro_art_music.mp3")
        pygame.mixer.music.play(-1)
        pygame.mouse.set_visible(False)

        self.running = True
        while self.running:
            self.window.fill((0, 0, 0))
            for x in pygame.event.get():
                if x.type == pygame.QUIT:
                    self.running = False
                elif x.type == pygame.KEYUP:
                    if (
                        x.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL
                    ):  # Ctrl-Q
                        self.running = False
                    if x.key == pygame.K_RIGHT and self.scene == "stageselect":
                        self.current_logo_index += 1
                        if self.current_logo_index == len(self.logos):
                            self.current_logo_index = 0
                    if x.key == pygame.K_LEFT and self.scene == "stageselect":
                        self.current_logo_index -= 1
                        if self.current_logo_index < 0:
                            self.current_logo_index = len(self.logos) - 1
                elif x.type == pygame.MOUSEMOTION:
                    x, y = x.pos
                    self.handle_hover(x, y)
                elif x.type == pygame.MOUSEBUTTONUP:
                    x, y = x.pos
                    self.cursor_state = "up"
                    self.handle_mouse(x, y, False)
                elif x.type == pygame.MOUSEBUTTONDOWN:
                    x, y = x.pos
                    self.cursor_state = "down"
                    self.handle_mouse(x, y, True)
            self.cursor_pos = (
                pygame.mouse.get_pos()[0] - self.cursor[0].get_height() // 2,
                pygame.mouse.get_pos()[1] - self.cursor[0].get_width() // 2,
            )
            self.clock.tick(self.fps)
            self.render()
            self.window.blit(
                self.cursor[self.cursor_name.index(self.cursor_state)], self.cursor_pos
            )
            pygame.display.update()
        pygame.quit()

    def render(self):
        if self.scene == "mainmenu":
            self.render_mainmenu_frame()
        elif self.scene == "stageselect":
            self.render_stageselect_frame()

    def handle_mouse(self, x, y, down):
        if self.scene == "mainmenu":
            for v in self.mainmenu_buttons.values():
                v.mouse_button(x, y, down)
        if (
            self.scene == "stageselect"
            and not down
            and self.controls_text_rect.collidepoint(x, y)
        ):
            self.current_logo_index -= 1
            if self.current_logo_index < 0:
                self.current_logo_index = len(self.logos) - 1
        if (
            self.scene == "stageselect"
            and not down
            and self.controls_text2_rect.collidepoint(x, y)
        ):
            self.current_logo_index += 1
            if self.current_logo_index == len(self.logos):
                self.current_logo_index = 0
        if self.scene == "stageselect":
            self.stageselect_back.mouse_button(x, y, down)

    def handle_hover(self, x, y):
        if self.scene == "mainmenu":
            for v in self.mainmenu_buttons.values():
                v.mouse_hover(x, y)
        if self.scene == "stageselect":
            self.stageselect_back.mouse_hover(x, y)

    def render_stageselect_frame(self):
        self.window.blit(self.logo_frames[self.current_logo_index], (0, 0))
        self.window.blit(self.controls_text, self.controls_text_rect)
        self.window.blit(self.controls_text2, self.controls_text2_rect)
        self.stageselect_back.render(self.window)

    def render_mainmenu_frame(self):
        for v in self.mainmenu_buttons.values():
            v.render(self.window)
        self.window.blit(self.version_text, self.version_text_rect)

    def handle_header_hover(self, x: int, y: int):
        pass

    def handle_header_mouse(self, x: int, y: int, down: bool):
        pass


def main():
    pygame.init()
    with open("settings.json") as f:
        settings = json.load(f)
    flags = 0
    if settings["window"]["fullscreen"]:
        flags |= pygame.FULLSCREEN
    if settings["window"]["native_res"]:
        settings["window"]["height"] = 0
        settings["window"]["width"] = 0

    window = pygame.display.set_mode(
        (settings["window"]["width"], settings["window"]["height"]), flags
    )
    pygame.display.set_caption("Progventures", "Progventures")

    game = Game(
        window,
        settings["window"]["fps"],
        settings["font"]["ppcm"],
        settings["font"]["font"],
    )
    game.start()


if __name__ == "__main__":
    main()
