import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess
import threading
import sys
import re


# ============================================================
# ARK X CINEMA — CONTROL PANEL
# ============================================================

ARK = Path(__file__).resolve().parents[1]

ENGINE = ARK / "Engine" / "orchestrator.py"
MOVIES = ARK / "Movies"
FINISHED = ARK / "Finished"
LOGS = ARK / "Logs"
LOG = LOGS / "orchestrator.log"


# ============================================================
# SUPPORTED MOVIE TYPES
# ============================================================

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".webm",
    ".m4v",
    ".ts",
    ".mts",
    ".m2ts",
    ".wmv",
    ".flv",
    ".ogv"
}

SUBTITLE_EXTENSIONS = {
    ".srt",
    ".vtt",
    ".ass",
    ".ssa",
    ".sub",
    ".sbv",
    ".dfxp",
    ".ttml"
}

AUDIO_EXTENSIONS = {
    ".wav",
    ".mp3",
    ".m4a",
    ".aac",
    ".flac",
    ".ogg",
    ".opus",
    ".wma",
    ".ac3",
    ".eac3"
}

AD_KEYWORDS = {
    "audio description",
    "audio_description",
    "audiodescription",
    "descriptive audio",
    "descriptive",
    "description"
}


# ============================================================
# PIPELINE STAGES
# ============================================================

STAGES = [
    ("1", "SOURCE INSPECTION", "SOURCE"),
    ("2", "SUBTITLE INGESTION", "SUBTITLE"),
    ("3", "SCENE DETECTION", "SCENE"),
    ("4", "AUDIO DESCRIPTION", "AUDIO DESCRIPTION"),
    ("5", "MODEL EVALUATION", "MODEL EVALUATION"),
    ("6", "FULL MOVIE INTELLIGENCE", "FULL MOVIE INTELLIGENCE"),
    ("7", "RECAP GENERATION", "RECAP"),
    ("8", "NARRATION", "NARRATION"),
    ("9", "VIDEO RENDER", "VIDEO RENDER"),
    ("10", "QUALITY ASSURANCE", "QA"),
]


# ============================================================
# MAIN APPLICATION
# ============================================================

class ARKCinema:

    def __init__(self, root):

        self.root = root

        self.root.title("ARK X Cinema")
        self.root.geometry("900x820")
        self.root.resizable(False, False)

        self.process = None
        self.running = False
        self.current_stage = None

        self.movie_path = None


        # ====================================================
        # HEADER
        # ====================================================

        title = tk.Label(
            root,
            text="ARK X CINEMA",
            font=("Segoe UI", 26, "bold")
        )
        title.pack(pady=(20, 0))

        subtitle = tk.Label(
            root,
            text="STORIES BEYOND THE SCREEN",
            font=("Segoe UI", 10)
        )
        subtitle.pack(pady=(0, 12))


        # ====================================================
        # SOURCE PANEL
        # ====================================================

        source_frame = tk.LabelFrame(
            root,
            text=" SOURCE PACKAGE ",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )
        source_frame.pack(
            padx=20,
            pady=5,
            fill="x"
        )

        self.movie_var = tk.StringVar(
            value="Scanning Movies folder..."
        )

        tk.Label(
            source_frame,
            textvariable=self.movie_var,
            justify="left",
            anchor="w",
            font=("Segoe UI", 10),
            wraplength=820
        ).pack(
            fill="x"
        )


        # ====================================================
        # START BUTTON
        # ====================================================

        self.start_button = tk.Button(
            root,
            text="▶  START PRODUCTION",
            font=("Segoe UI", 16, "bold"),
            width=30,
            height=2,
            command=self.start_production
        )

        self.start_button.pack(
            pady=12
        )


        # ====================================================
        # STATUS
        # ====================================================

        status_frame = tk.LabelFrame(
            root,
            text=" STATUS ",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8
        )

        status_frame.pack(
            padx=20,
            fill="x"
        )

        self.status_var = tk.StringVar(
            value="READY"
        )

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 13, "bold")
        )

        self.status_label.pack()


        # ====================================================
        # PIPELINE
        # ====================================================

        pipeline_frame = tk.LabelFrame(
            root,
            text=" PRODUCTION PIPELINE ",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8
        )

        pipeline_frame.pack(
            padx=20,
            pady=8,
            fill="x"
        )

        self.stage_labels = {}

        for number, name, key in STAGES:

            row = tk.Frame(
                pipeline_frame
            )

            row.pack(
                fill="x",
                pady=1
            )

            label = tk.Label(
                row,
                text=f"○  {number}. {name}",
                anchor="w",
                font=("Segoe UI", 9),
                width=38
            )

            label.pack(
                side="left"
            )

            self.stage_labels[key] = label


        # ====================================================
        # LIVE ENGINE OUTPUT
        # ====================================================

        output_frame = tk.LabelFrame(
            root,
            text=" LIVE PRODUCTION LOG ",
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )

        output_frame.pack(
            padx=20,
            pady=5,
            fill="both",
            expand=True
        )

        self.output = tk.Text(
            output_frame,
            height=13,
            width=105,
            state="disabled",
            font=("Consolas", 8)
        )

        self.output.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            output_frame,
            command=self.output.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.output.config(
            yscrollcommand=scrollbar.set
        )


        # ====================================================
        # BOTTOM BUTTONS
        # ====================================================

        buttons = tk.Frame(
            root
        )

        buttons.pack(
            pady=8
        )

        tk.Button(
            buttons,
            text="📁 Open Movies",
            width=18,
            command=lambda: self.open_folder(MOVIES)
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            buttons,
            text="🎬 Open Finished",
            width=18,
            command=lambda: self.open_folder(FINISHED)
        ).pack(
            side="left",
            padx=5
        )

        tk.Button(
            buttons,
            text="📋 Open Log",
            width=18,
            command=self.open_log
        ).pack(
            side="left",
            padx=5
        )


        # ====================================================
        # INITIAL SCAN
        # ====================================================

        self.refresh_movie()


    # ========================================================
    # OUTPUT
    # ========================================================

    def write(self, text):

        self.output.config(
            state="normal"
        )

        self.output.insert(
            "end",
            text
        )

        self.output.see(
            "end"
        )

        self.output.config(
            state="disabled"
        )


    # ========================================================
    # FIND VALID MOVIES
    # ========================================================

    def find_movies(self):

        results = []

        if not MOVIES.exists():
            return results

        for item in MOVIES.iterdir():

            # Direct video file
            if (
                item.is_file()
                and item.suffix.lower()
                in VIDEO_EXTENSIONS
            ):

                results.append(item)

                continue


            # Movie package directory
            if item.is_dir():

                videos = [
                    x
                    for x in item.rglob("*")
                    if (
                        x.is_file()
                        and x.suffix.lower()
                        in VIDEO_EXTENSIONS
                    )
                ]

                if videos:
                    results.append(item)

        return results


    # ========================================================
    # PACKAGE INFORMATION
    # ========================================================

    def inspect_package(self, package):

        subtitles = []
        ad_files = []

        if package.is_file():

            parent = package.parent

            candidates = [
                x
                for x in parent.iterdir()
                if x.is_file()
            ]

        else:

            candidates = [
                x
                for x in package.rglob("*")
                if x.is_file()
            ]

        for item in candidates:

            suffix = item.suffix.lower()
            name = item.name.lower()

            if suffix in SUBTITLE_EXTENSIONS:
                subtitles.append(item)

            if suffix in AUDIO_EXTENSIONS:

                if any(
                    keyword in name
                    for keyword in AD_KEYWORDS
                ):
                    ad_files.append(item)


        return subtitles, ad_files


    # ========================================================
    # REFRESH MOVIE DISPLAY
    # ========================================================

    def refresh_movie(self):

        movies = self.find_movies()

        if not movies:

            self.movie_path = None

            self.movie_var.set(
                "NO VALID MOVIE FOUND\n\n"
                "Place a movie video file or movie package inside:\n"
                + str(MOVIES)
                + "\n\n"
                "Accepted video types: "
                + ", ".join(sorted(VIDEO_EXTENSIONS))
            )

            return


        # One movie at a time.
        selected = movies[0]

        self.movie_path = selected

        subtitles, ad_files = self.inspect_package(
            selected
        )

        if selected.is_file():

            movie_name = selected.name

        else:

            movie_name = selected.name + " (package)"


        subtitle_status = (
            "DETECTED"
            if subtitles
            else "NOT DETECTED"
        )

        ad_status = (
            "DETECTED"
            if ad_files
            else "NOT DETECTED"
        )


        display = (
            f"MOVIE: {movie_name}\n"
            f"SUBTITLES: {subtitle_status}\n"
            f"AUDIO DESCRIPTION: {ad_status}\n\n"
            f"SOURCE: {selected}"
        )

        self.movie_var.set(
            display
        )


    # ========================================================
    # RESET PIPELINE
    # ========================================================

    def reset_pipeline(self):

        self.current_stage = None

        for label in self.stage_labels.values():

            label.config(
                text=label.cget("text")
                .replace("✓", "○")
                .replace("▶", "○")
                .replace("✗", "○")
            )


    # ========================================================
    # UPDATE PIPELINE STAGE
    # ========================================================

    def update_stage(self, key):

        self.current_stage = key

        found_current = False

        for number, name, stage_key in STAGES:

            label = self.stage_labels[stage_key]

            if stage_key == key:

                label.config(
                    text=f"▶  {number}. {name}"
                )

                found_current = True

            elif not found_current:

                label.config(
                    text=f"✓  {number}. {name}"
                )

            else:

                label.config(
                    text=f"○  {number}. {name}"
                )


    # ========================================================
    # DETECT PIPELINE STAGE FROM ENGINE OUTPUT
    # ========================================================

    def detect_stage(self, line):

        upper = line.upper()

        stage_map = {

            "=== 1/10": "SOURCE",

            "=== 2/10": "SUBTITLE",

            "=== 3/10": "SCENE",

            "=== 4/10": "AUDIO DESCRIPTION",

            "=== 5/10": "MODEL EVALUATION",

            "=== 6/10": "FULL MOVIE INTELLIGENCE",

            "=== 7/10": "RECAP",

            "=== 8/10": "NARRATION",

            "=== 9/10": "VIDEO RENDER",

            "=== 10/10": "QA",
        }


        for marker, key in stage_map.items():

            if marker in upper:

                self.root.after(
                    0,
                    self.update_stage,
                    key
                )

                return


    # ========================================================
    # START PRODUCTION
    # ========================================================

    def start_production(self):

        if (
            self.process
            and self.process.poll() is None
        ):

            messagebox.showwarning(
                "Already Running",
                "ARK X Cinema is already processing a movie."
            )

            return


        self.refresh_movie()


        if self.movie_path is None:

            messagebox.showerror(
                "No Movie",
                "No valid movie was found.\n\n"
                "Place an actual video file or movie package "
                "inside the Movies folder."
            )

            return


        if not ENGINE.exists():

            messagebox.showerror(
                "Engine Missing",
                f"Could not find:\n{ENGINE}"
            )

            return


        self.running = True

        self.reset_pipeline()


        self.start_button.config(
            state="disabled",
            text="⏳  PRODUCTION RUNNING..."
        )


        self.status_var.set(
            "PRODUCTION RUNNING"
        )


        self.write(
            "\n"
            + "=" * 80
            + "\n"
            + "ARK X CINEMA — PRODUCTION STARTED\n"
            + "=" * 80
            + "\n"
            + f"SOURCE: {self.movie_path}\n"
            + "\n"
        )


        thread = threading.Thread(
            target=self.run_engine,
            daemon=True
        )

        thread.start()


    # ========================================================
    # RUN ENGINE
    # ========================================================

    def run_engine(self):

        try:

            self.process = subprocess.Popen(

                [
                    sys.executable,
                    str(ENGINE)
                ],

                cwd=str(ARK),

                stdout=subprocess.PIPE,

                stderr=subprocess.STDOUT,

                text=True,

                encoding="utf-8",

                errors="replace",

                bufsize=1
            )


            for line in self.process.stdout:

                self.root.after(
                    0,
                    self.write,
                    line
                )

                self.detect_stage(
                    line
                )


            code = self.process.wait()


            self.root.after(
                0,
                self.production_finished,
                code
            )


        except Exception as exc:

            self.root.after(
                0,
                self.production_error,
                str(exc)
            )


    # ========================================================
    # PRODUCTION FINISHED
    # ========================================================

    def production_finished(self, code):

        self.running = False

        self.start_button.config(
            state="normal",
            text="▶  START PRODUCTION"
        )


        if code == 0:

            # Mark all stages complete.
            for number, name, key in STAGES:

                self.stage_labels[key].config(
                    text=f"✓  {number}. {name}"
                )


            self.status_var.set(
                "✅ PRODUCTION COMPLETE — HUMAN QA REQUIRED"
            )


            self.write(
                "\n"
                + "=" * 80
                + "\n"
                + "✅ ARK X CINEMA — PRODUCTION COMPLETE\n"
                + "\n"
                + "HUMAN ACTION REQUIRED:\n"
                + "Review the finished video before uploading.\n"
                + "=" * 80
                + "\n"
            )


            messagebox.showinfo(

                "ARK X Cinema — Complete",

                "Production completed successfully.\n\n"

                "The machine has finished its job.\n\n"

                "NEXT STEP:\n"
                "Open the Finished folder and review the video.\n\n"

                "Human QA is required before upload."
            )


        else:

            self.status_var.set(
                "❌ PRODUCTION FAILED — CHECK LOG"
            )


            self.write(
                "\n"
                + "=" * 80
                + "\n"
                + "❌ ARK X CINEMA — PRODUCTION FAILED\n"
                + "\n"
                + "Check the log for the exact error.\n"
                + "=" * 80
                + "\n"
            )


            messagebox.showerror(

                "ARK X Cinema — Production Failed",

                "The production pipeline failed.\n\n"

                "Open the Log and find the first error.\n\n"

                "The movie has NOT been approved for upload."
            )


        self.refresh_movie()


    # ========================================================
    # CONTROL PANEL ERROR
    # ========================================================

    def production_error(self, error):

        self.running = False

        self.start_button.config(
            state="normal",
            text="▶  START PRODUCTION"
        )


        self.status_var.set(
            "❌ CONTROL PANEL ERROR"
        )


        self.write(
            "\n"
            + "=" * 80
            + "\n"
            + "CONTROL PANEL ERROR:\n"
            + error
            + "\n"
            + "=" * 80
            + "\n"
        )


        messagebox.showerror(
            "Control Panel Error",
            error
        )


    # ========================================================
    # OPEN FOLDER
    # ========================================================

    def open_folder(self, folder):

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        subprocess.Popen(
            [
                "explorer.exe",
                str(folder)
            ]
        )


    # ========================================================
    # OPEN LOG
    # ========================================================

    def open_log(self):

        if LOG.exists():

            subprocess.Popen(
                [
                    "notepad.exe",
                    str(LOG)
                ]
            )

        else:

            messagebox.showinfo(
                "Log",
                "No orchestrator log exists yet."
            )


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ARKCinema(
        root
    )

    root.mainloop()
