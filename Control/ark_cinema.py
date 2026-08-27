import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import subprocess
import threading
import sys
import time
import json
import os

# ============================================================
# ARK X CINEMA
# PRODUCTION CONTROL CENTER
# ============================================================

ARK = Path(__file__).resolve().parents[1]

ENGINE = ARK / "Engine" / "orchestrator.py"
MOVIES = ARK / "Movies"
FINISHED = ARK / "Finished"
PROJECTS = ARK / "Projects"
LOGS = ARK / "Logs"

LOG_FILE = LOGS / "orchestrator.log"

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
    ".ogv",
}

STAGES = [
    "SOURCE INSPECTION",
    "SUBTITLE INGESTION",
    "SCENE DETECTION",
    "AUDIO DESCRIPTION",
    "MODEL EVALUATION",
    "FULL MOVIE INTELLIGENCE",
    "RECAP GENERATION",
    "NARRATION",
    "VIDEO RENDER",
    "QUALITY ASSURANCE",
]


class ARKCinema:

    def __init__(self, root):

        self.root = root

        self.root.title("ARK X Cinema — Production Control Center")
        self.root.geometry("900x850")
        self.root.resizable(False, False)

        self.process = None
        self.start_time = None
        self.current_movie = None
        self.current_project = None

        self.stage_labels = []

        self.build_ui()
        self.refresh_source()
        self.update_runtime()

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        title = tk.Label(
            self.root,
            text="ARK X CINEMA",
            font=("Segoe UI", 25, "bold")
        )
        title.pack(pady=(20, 0))

        subtitle = tk.Label(
            self.root,
            text="STORIES BEYOND THE SCREEN",
            font=("Segoe UI", 10)
        )
        subtitle.pack(pady=(0, 15))

        # ----------------------------------------------------
        # SOURCE
        # ----------------------------------------------------

        source_frame = tk.LabelFrame(
            self.root,
            text=" SOURCE PACKAGE ",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=10
        )

        source_frame.pack(
            fill="x",
            padx=25,
            pady=5
        )

        self.source_var = tk.StringVar(
            value="Checking Movies folder..."
        )

        tk.Label(
            source_frame,
            textvariable=self.source_var,
            font=("Segoe UI", 11),
            justify="left",
            anchor="w"
        ).pack(fill="x")

        # ----------------------------------------------------
        # MAIN CONTROLS
        # ----------------------------------------------------

        controls = tk.Frame(self.root)
        controls.pack(pady=12)

        self.start_button = tk.Button(
            controls,
            text="▶  START PRODUCTION",
            font=("Segoe UI", 15, "bold"),
            width=25,
            height=2,
            command=self.start_production
        )

        self.start_button.grid(
            row=0,
            column=0,
            padx=8
        )

        self.stop_button = tk.Button(
            controls,
            text="■  STOP PRODUCTION",
            font=("Segoe UI", 12, "bold"),
            width=20,
            height=2,
            command=self.stop_production,
            state="disabled"
        )

        self.stop_button.grid(
            row=0,
            column=1,
            padx=8
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        status_frame = tk.Frame(self.root)
        status_frame.pack(pady=3)

        tk.Label(
            status_frame,
            text="STATUS:",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        self.status_var = tk.StringVar(
            value="READY"
        )

        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            font=("Segoe UI", 11, "bold")
        )

        self.status_label.pack(side="left", padx=6)

        self.runtime_var = tk.StringVar(
            value="Elapsed: 00:00:00"
        )

        tk.Label(
            self.root,
            textvariable=self.runtime_var,
            font=("Consolas", 10)
        ).pack()

        # ----------------------------------------------------
        # PIPELINE
        # ----------------------------------------------------

        pipeline_frame = tk.LabelFrame(
            self.root,
            text=" PRODUCTION PIPELINE ",
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=8
        )

        pipeline_frame.pack(
            fill="x",
            padx=25,
            pady=8
        )

        for index, stage in enumerate(STAGES, start=1):

            label = tk.Label(
                pipeline_frame,
                text=f"○ {index}. {stage}",
                font=("Segoe UI", 9),
                anchor="w"
            )

            label.pack(
                fill="x",
                pady=1
            )

            self.stage_labels.append(label)

        # ----------------------------------------------------
        # LIVE LOG
        # ----------------------------------------------------

        log_frame = tk.LabelFrame(
            self.root,
            text=" LIVE PRODUCTION LOG ",
            font=("Segoe UI", 10, "bold"),
            padx=8,
            pady=8
        )

        log_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=8
        )

        text_frame = tk.Frame(log_frame)
        text_frame.pack(
            fill="both",
            expand=True
        )

        scrollbar = tk.Scrollbar(
            text_frame
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        self.output = tk.Text(
            text_frame,
            height=13,
            width=105,
            state="disabled",
            font=("Consolas", 8),
            yscrollcommand=scrollbar.set
        )

        self.output.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.config(
            command=self.output.yview
        )

        # ----------------------------------------------------
        # UTILITY BUTTONS
        # ----------------------------------------------------

        buttons = tk.Frame(self.root)
        buttons.pack(pady=(0, 15))

        tk.Button(
            buttons,
            text="📁 Movies",
            width=14,
            command=lambda: self.open_folder(MOVIES)
        ).grid(row=0, column=0, padx=3)

        tk.Button(
            buttons,
            text="🎬 Finished",
            width=14,
            command=lambda: self.open_folder(FINISHED)
        ).grid(row=0, column=1, padx=3)

        tk.Button(
            buttons,
            text="📂 Project",
            width=14,
            command=self.open_project
        ).grid(row=0, column=2, padx=3)

        tk.Button(
            buttons,
            text="📋 QA Report",
            width=14,
            command=self.open_qa
        ).grid(row=0, column=3, padx=3)

        tk.Button(
            buttons,
            text="📜 Log",
            width=14,
            command=self.open_log
        ).grid(row=0, column=4, padx=3)

        tk.Button(
            buttons,
            text="🔄 Refresh",
            width=14,
            command=self.refresh_source
        ).grid(row=0, column=5, padx=3)

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
    # SOURCE DETECTION
    # ========================================================

    def find_movie_sources(self):

        sources = []

        if not MOVIES.exists():
            MOVIES.mkdir(
                parents=True,
                exist_ok=True
            )

        for item in MOVIES.iterdir():

            if item.is_file():

                if item.suffix.lower() in VIDEO_EXTENSIONS:
                    sources.append(item)

            elif item.is_dir():

                video_files = [
                    p for p in item.rglob("*")
                    if p.is_file()
                    and p.suffix.lower() in VIDEO_EXTENSIONS
                ]

                if video_files:
                    sources.append(item)

        return sources

    def refresh_source(self):

        sources = self.find_movie_sources()

        if not sources:

            self.current_movie = None

            self.source_var.set(
                "NO VALID MOVIE FOUND\n\n"
                "Place a movie video file or movie package inside:\n"
                f"{MOVIES}\n\n"
                "Accepted video types: "
                + ", ".join(
                    sorted(VIDEO_EXTENSIONS)
                )
            )

            return

        if len(sources) == 1:

            self.current_movie = sources[0]

            self.source_var.set(
                "MOVIE READY\n\n"
                + str(sources[0])
            )

        else:

            self.current_movie = sources[0]

            names = "\n".join(
                str(x.name)
                for x in sources[:10]
            )

            self.source_var.set(
                "MULTIPLE MOVIE SOURCES DETECTED\n\n"
                + names
                + "\n\n"
                + "ARK X Cinema processes ONE movie per run."
            )

    # ========================================================
    # PIPELINE STATUS
    # ========================================================

    def reset_stages(self):

        for index, label in enumerate(
            self.stage_labels
        ):

            label.config(
                text=f"○ {index + 1}. {STAGES[index]}"
            )

    def update_stage_from_line(self, line):

        lower = line.lower()

        keywords = [
            [
                "source inspection",
                0
            ],
            [
                "subtitle ingestion",
                1
            ],
            [
                "scene detection",
                2
            ],
            [
                "audio description",
                3
            ],
            [
                "model evaluation",
                4
            ],
            [
                "full movie intelligence",
                5
            ],
            [
                "recap generation",
                6
            ],
            [
                "narration",
                7
            ],
            [
                "video render",
                8
            ],
            [
                "quality assurance",
                9
            ],
        ]

        for keyword, index in keywords:

            if keyword in lower:

                for i, label in enumerate(
                    self.stage_labels
                ):

                    if i < index:
                        label.config(
                            text=f"✓ {i + 1}. {STAGES[i]}"
                        )

                    elif i == index:
                        label.config(
                            text=f"▶ {i + 1}. {STAGES[i]}"
                        )

                    else:
                        label.config(
                            text=f"○ {i + 1}. {STAGES[i]}"
                        )

                break

    # ========================================================
    # START
    # ========================================================

    def start_production(self):

        if self.process and self.process.poll() is None:

            messagebox.showwarning(
                "Production Already Running",
                "ARK X Cinema is already processing a movie."
            )

            return

        self.refresh_source()

        sources = self.find_movie_sources()

        if not sources:

            messagebox.showerror(
                "No Movie",
                "No valid movie video was found.\n\n"
                "Place a movie inside:\n"
                + str(MOVIES)
            )

            return

        if len(sources) > 1:

            answer = messagebox.askyesno(
                "Multiple Sources",
                "Multiple valid movie sources were detected.\n\n"
                "ARK X Cinema processes ONE movie per run.\n\n"
                f"The engine will select its normal first package.\n\n"
                "Continue?"
            )

            if not answer:
                return

        if not ENGINE.exists():

            messagebox.showerror(
                "Engine Missing",
                f"Could not find:\n{ENGINE}"
            )

            return

        self.reset_stages()

        self.output.config(
            state="normal"
        )

        self.output.delete(
            "1.0",
            "end"
        )

        self.output.config(
            state="disabled"
        )

        self.start_time = time.time()

        self.start_button.config(
            state="disabled",
            text="⏳  PRODUCTION RUNNING..."
        )

        self.stop_button.config(
            state="normal"
        )

        self.status_var.set(
            "PRODUCTION RUNNING"
        )

        self.write(
            "\n"
            + "=" * 90
            + "\n"
            + "ARK X CINEMA — PRODUCTION STARTED\n"
            + "=" * 90
            + "\n"
        )

        self.write(
            f"SOURCE: {sources[0]}\n"
        )

        self.write(
            f"ENGINE: {ENGINE}\n\n"
        )

        thread = threading.Thread(
            target=self.run_engine,
            daemon=True
        )

        thread.start()

    # ========================================================
    # ENGINE
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
                    self.handle_engine_line,
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

    def handle_engine_line(self, line):

        self.write(line)
        self.update_stage_from_line(line)

    # ========================================================
    # STOP
    # ========================================================

    def stop_production(self):

        if not self.process:
            return

        if self.process.poll() is not None:
            return

        answer = messagebox.askyesno(
            "Stop Production?",
            "This will terminate the current production process.\n\n"
            "The movie will NOT be considered successfully completed.\n\n"
            "Stop now?"
        )

        if not answer:
            return

        try:

            self.process.terminate()

            self.write(
                "\n"
                + "=" * 70
                + "\n"
                + "PRODUCTION STOP REQUESTED BY USER\n"
                + "=" * 70
                + "\n"
            )

            self.status_var.set(
                "STOPPING..."
            )

        except Exception as exc:

            messagebox.showerror(
                "Stop Error",
                str(exc)
            )

    # ========================================================
    # COMPLETION
    # ========================================================

    def production_finished(self, code):

        self.start_button.config(
            state="normal",
            text="▶  START PRODUCTION"
        )

        self.stop_button.config(
            state="disabled"
        )

        self.process = None

        elapsed = self.get_elapsed()

        if code == 0:

            self.status_var.set(
                "✅ PRODUCTION COMPLETE — READY FOR HUMAN QA"
            )

            self.write(
                "\n"
                + "=" * 90
                + "\n"
                + "ARK X CINEMA — PRODUCTION COMPLETE\n"
                + "=" * 90
                + "\n"
                + f"Elapsed: {elapsed}\n"
                + "\n"
                + "NEXT STEP: Review the finished video manually.\n"
                + "=" * 90
                + "\n"
            )

            messagebox.showinfo(
                "ARK X Cinema",
                "Production completed successfully.\n\n"
                f"Elapsed time: {elapsed}\n\n"
                "Open Finished to review the video."
            )

        else:

            self.status_var.set(
                "❌ PRODUCTION FAILED — CHECK LOG"
            )

            self.write(
                "\n"
                + "=" * 90
                + "\n"
                + "ARK X CINEMA — PRODUCTION FAILED\n"
                + "=" * 90
                + "\n"
                + f"Exit code: {code}\n"
                + f"Elapsed: {elapsed}\n"
                + "\n"
                + f"Check: {LOG_FILE}\n"
                + "=" * 90
                + "\n"
            )

            messagebox.showerror(
                "ARK X Cinema",
                "Production failed.\n\n"
                "Open the log to determine what happened."
            )

        self.refresh_source()

    def production_error(self, error):

        self.start_button.config(
            state="normal",
            text="▶  START PRODUCTION"
        )

        self.stop_button.config(
            state="disabled"
        )

        self.process = None

        self.status_var.set(
            "❌ CONTROL CENTER ERROR"
        )

        self.write(
            "\nCONTROL CENTER ERROR:\n"
            + error
            + "\n"
        )

    # ========================================================
    # RUNTIME
    # ========================================================

    def get_elapsed(self):

        if not self.start_time:
            return "00:00:00"

        seconds = int(
            time.time() - self.start_time
        )

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def update_runtime(self):

        if self.start_time and self.process:

            self.runtime_var.set(
                "Elapsed: "
                + self.get_elapsed()
            )

        self.root.after(
            1000,
            self.update_runtime
        )

    # ========================================================
    # FOLDERS / REPORTS
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

    def open_project(self):

        if self.current_project and self.current_project.exists():

            self.open_folder(
                self.current_project
            )

            return

        projects = [
            x for x in PROJECTS.iterdir()
            if x.is_dir()
        ] if PROJECTS.exists() else []

        if projects:

            latest = max(
                projects,
                key=lambda x: x.stat().st_mtime
            )

            self.current_project = latest

            self.open_folder(
                latest
            )

            return

        messagebox.showinfo(
            "Project",
            "No project has been created yet."
        )

    def open_qa(self):

        projects = [
            x for x in PROJECTS.iterdir()
            if x.is_dir()
        ] if PROJECTS.exists() else []

        reports = []

        for project in projects:

            report = project / "qa_report.json"

            if report.exists():
                reports.append(report)

        if not reports:

            messagebox.showinfo(
                "QA Report",
                "No QA report exists yet."
            )

            return

        latest = max(
            reports,
            key=lambda x: x.stat().st_mtime
        )

        subprocess.Popen(
            [
                "notepad.exe",
                str(latest)
            ]
        )

    def open_log(self):

        if LOG_FILE.exists():

            subprocess.Popen(
                [
                    "notepad.exe",
                    str(LOG_FILE)
                ]
            )

        else:

            messagebox.showinfo(
                "Log",
                "No orchestrator log exists yet."
            )


# ============================================================
# ENTRY
# ============================================================

if __name__ == "__main__":

    MOVIES.mkdir(
        parents=True,
        exist_ok=True
    )

    FINISHED.mkdir(
        parents=True,
        exist_ok=True
    )

    PROJECTS.mkdir(
        parents=True,
        exist_ok=True
    )

    LOGS.mkdir(
        parents=True,
        exist_ok=True
    )

    root = tk.Tk()

    app = ARKCinema(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        root.destroy
    )

    root.mainloop()
