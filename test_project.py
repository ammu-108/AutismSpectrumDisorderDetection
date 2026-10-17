from tkinter import Tk, Label, Button, Frame, StringVar, PhotoImage
from tkinter import filedialog
from PIL import Image, ImageTk
import logging
import os
import queue
import threading
import time
import test2

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


class _PredictionResult:
    def __init__(self, result_queue, prediction_id):
        self.result_queue = result_queue
        self.prediction_id = prediction_id
        self.reported = False

    def config(self, **options):
        report = options.get("text", "")
        if report.startswith("Report: "):
            self.reported = True
            result = report
            while result.startswith("Report: "):
                result = result.removeprefix("Report: ")
            self.result_queue.put(
                (self.prediction_id, "success", result)
            )


class create_gui:
    def __init__(self, window):
        self.window = window
        self.window.title("Autism Spectrum Disorder Detection")
        self.window.geometry("1180x760")
        self.window.minsize(980, 700)
        self.window.configure(bg="#f4f2fa")

        self.selected_path = ""
        self.preview_source = None
        self.pending_result_queue = queue.Queue()
        self.prediction_sequence = 0
        self.active_prediction_id = None
        self.prediction_worker_running = False

        self.icon = self._safe_load_png("icon.png")
        if self.icon is not None:
            self.window.iconphoto(True, self.icon)

        self.header = Frame(self.window, bg="#f4f2fa")
        self.header.pack(fill="x", padx=28, pady=(24, 18))

        self.title = Label(
            self.header,
            text="Autism Spectrum Disorder Detection",
            font=("Segoe UI", 24, "bold"),
            bg="#f4f2fa",
            fg="#382b59",
            anchor="w",
        )
        self.title.pack(anchor="w")

        self.subtitle = Label(
            self.header,
            text="Upload a valid image and run the current model analysis.",
            font=("Segoe UI", 11),
            bg="#f4f2fa",
            fg="#475569",
            anchor="w",
        )
        self.subtitle.pack(anchor="w", pady=(6, 0))

        self.content = Frame(self.window, bg="#f4f2fa")
        self.content.pack(fill="both", expand=True, padx=28, pady=(0, 28))

        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_columnconfigure(1, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.left_panel = Frame(self.content, bg="#f0edfa", highlightbackground="#d8d1e8", highlightthickness=1)
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

        self.preview_panel = Frame(self.content, bg="#fdfcff", highlightbackground="#d8d1e8", highlightthickness=1)
        self.preview_panel.grid(row=0, column=1, sticky="nsew")

        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure(5, weight=1)

        self.preview_panel.grid_columnconfigure(0, weight=1)
        self.preview_panel.grid_rowconfigure(1, weight=1)

        self.upload_section = Frame(self.left_panel, bg="#f0edfa")
        self.upload_section.grid(row=0, column=0, sticky="ew", padx=28, pady=(26, 20))

        self.upload_btn_img = self._load_asset('upload.png', (90, 90))
        self.upload_button = Button(
            self.upload_section,
            image=self.upload_btn_img,
            compound="top",
            text="Upload Image",
            font=("Segoe UI", 12, "bold"),
            bg="#594781",
            fg="#ffffff",
            activebackground="#49396d",
            activeforeground="#ffffff",
            relief="flat",
            bd=0,
            padx=18,
            pady=14,
            cursor="hand2",
            command=self.detection,
        )
        self.upload_button.pack(fill="x")
        self.upload_button.bind(
            "<Enter>",
            lambda _event: self.upload_button.configure(bg="#49396d"),
        )
        self.upload_button.bind(
            "<Leave>",
            lambda _event: self.upload_button.configure(bg="#594781"),
        )

        self.input_note = Label(
            self.upload_section,
            text=(
                "Upload brain MRI images only. The application does not "
                "automatically verify MRI content. Research demonstration "
                "only — not a clinical diagnosis."
            ),
            font=("Segoe UI", 9),
            bg="#f4f0fb",
            fg="#594d70",
            anchor="w",
            justify="left",
            wraplength=390,
            padx=12,
            pady=9,
            highlightbackground="#d9d0eb",
            highlightthickness=1,
        )
        self.input_note.pack(fill="x", pady=(8, 0))

        self.clear_button = Button(
            self.upload_section,
            text="Reset / Clear",
            font=("Segoe UI", 10, "bold"),
            bg="#e8e3f3",
            fg="#49396d",
            activebackground="#d9d0eb",
            activeforeground="#382b59",
            relief="flat",
            bd=0,
            padx=12,
            pady=9,
            cursor="hand2",
            command=self.reset,
        )
        self.clear_button.pack(fill="x", pady=(7, 0))
        self.clear_button.bind(
            "<Enter>",
            lambda _event: self.clear_button.configure(bg="#d9d0eb"),
        )
        self.clear_button.bind(
            "<Leave>",
            lambda _event: self.clear_button.configure(bg="#e8e3f3"),
        )

        self.status_title = Label(
            self.left_panel,
            text="Status",
            font=("Segoe UI", 12, "bold"),
            bg="#f0edfa",
            fg="#382b59",
            anchor="w",
        )
        self.status_title.grid(row=1, column=0, sticky="w", padx=28, pady=(0, 8))

        self.status_var = StringVar(value="Ready")
        self.status_label = Label(
            self.left_panel,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            bg="#e9e3f5",
            fg="#594781",
            anchor="w",
            justify="left",
            wraplength=420,
            bd=0,
            relief="flat",
            padx=14,
            pady=12,
            highlightbackground="#d8d1e8",
            highlightthickness=1,
        )
        self.status_label.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 18))

        self.result_title = Label(
            self.left_panel,
            text="Prediction",
            font=("Segoe UI", 12, "bold"),
            bg="#f0edfa",
            fg="#382b59",
            anchor="w",
        )
        self.result_title.grid(row=3, column=0, sticky="w", padx=28, pady=(0, 8))

        self.result_var = StringVar(value="Awaiting image selection")
        self.result_label = Label(
            self.left_panel,
            textvariable=self.result_var,
            font=("Segoe UI", 13, "bold"),
            bg="#e8e3f3",
            fg="#49396d",
            anchor="w",
            justify="left",
            wraplength=420,
            bd=0,
            relief="flat",
            padx=14,
            pady=12,
            highlightbackground="#d8d1e8",
            highlightthickness=1,
        )
        self.result_label.grid(row=4, column=0, sticky="ew", padx=28, pady=(0, 20))

        self.disclaimer_label = Label(
            self.left_panel,
            text="Research demonstration only — not a clinical diagnosis.",
            font=("Segoe UI", 9),
            bg="#f0edfa",
            fg="#64748b",
            anchor="w",
            justify="left",
            wraplength=420,
        )
        self.disclaimer_label.grid(row=5, column=0, sticky="sw", padx=28, pady=(0, 22))

        self.preview_title = Label(
            self.preview_panel,
            text="Selected Image",
            font=("Segoe UI", 12, "bold"),
            bg="#fdfcff",
            fg="#382b59",
            anchor="w",
            wraplength=500,
            justify="left",
        )
        self.preview_title.grid(row=0, column=0, sticky="nw", padx=22, pady=(18, 8))

        self.preview_container = Frame(
            self.preview_panel,
            bg="#f0edfa",
            highlightbackground="#d8d1e8",
            highlightthickness=1,
        )
        self.preview_container.grid(row=1, column=0, sticky="nsew", padx=22, pady=(0, 22))
        self.preview_container.grid_rowconfigure(0, weight=1)
        self.preview_container.grid_columnconfigure(0, weight=1)

        self.preview_label = Label(
            self.preview_container,
            text="Choose Upload Image to display a preview.",
            bg="#f0edfa",
            fg="#64748b",
            font=("Segoe UI", 15, "bold"),
            compound="center",
            image=None,
            anchor="center",
        )
        self.preview_label.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
        self.preview_label.bind("<Configure>", self._render_preview)

        self.set_status("Ready. Select an image to begin analysis.", "#0f766e")
        self.result_var.set("Awaiting image selection")

        self._poll_result_queue()

    def _safe_load_png(self, path):
        try:
            return PhotoImage(file=path)
        except Exception:
            return None

    def _load_asset(self, path, size):
        try:
            image = Image.open(path).convert("RGBA")
            image = image.resize(size, Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)
        except Exception:
            return None

    def set_status(self, message, color="#0f766e"):
        status_colors = {
            "#0f766e": ("#e9e3f5", "#594781"),
            "#dc2626": ("#fee2e2", "#b91c1c"),
            "#1d4ed8": ("#e8e3f3", "#49396d"),
        }
        self.status_var.set(message)
        background, foreground = status_colors.get(color, ("#e2e8f0", color))
        self.status_label.configure(bg=background, fg=foreground)

    def set_result(self, message, background="#e8e3f3", foreground="#49396d"):
        self.result_var.set(message)
        self.result_label.configure(bg=background, fg=foreground)

    def _poll_result_queue(self):
        try:
            while True:
                prediction_id, status, result = self.pending_result_queue.get_nowait()
                self.prediction_worker_running = False
                self.upload_button.configure(state="normal")
                if prediction_id != self.active_prediction_id:
                    if self.active_prediction_id is None:
                        self.set_status(
                            "Selection cleared. The previous prediction has finished.",
                            "#0f766e",
                        )
                    continue

                self.active_prediction_id = None
                if status == "success":
                    self.set_result(f"Report: {result}", "#dcfce7", "#166534")
                    self.set_status("Prediction completed successfully.", "#0f766e")
                else:
                    self.set_result("Prediction failed", "#fee2e2", "#b91c1c")
                    self.set_status(status, "#dc2626")
        except queue.Empty:
            pass

        self.window.after(100, self._poll_result_queue)

    def openfilename(self):
        filename = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tif;*.tiff"),
                ("All files", "*.*"),
            ],
        )
        return filename

    def open_img(self, heading):
        x = self.openfilename()
        if not x:
            logger.info("Image selection cancelled.")
            self.set_status("No image selected. Please choose an image to continue.", "#dc2626")
            return ""

        logger.info("Selected image: %s", os.path.basename(x))
        try:
            with Image.open(x) as img:
                width, height = img.size
                logger.info(
                    "Selected image details: format=%s size=%s mode=%s",
                    img.format,
                    img.size,
                    img.mode,
                )
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                if img.mode == "L":
                    img = img.convert("RGB")

                self.preview_source = img.copy()
                self.preview_label.configure(text="")
                self._render_preview()
                self.selected_path = x
                self.preview_title.configure(
                    text=f"Selected Image — {os.path.basename(x)} ({width} × {height})"
                )

            self.set_status(
                f"Image loaded: {os.path.basename(x)}. Ready to analyze.",
                "#0f766e",
            )
            return x
        except Exception:
            logger.exception("Unable to open the selected image.")
            self.set_status("Unable to open the selected file. Please choose a valid image file.", "#dc2626")
            return ""

    def _render_preview(self, event=None):
        if self.preview_source is None:
            return

        width = max(self.preview_label.winfo_width() - 36, 1)
        height = max(self.preview_label.winfo_height() - 36, 1)
        preview = self.preview_source.copy()
        preview.thumbnail(
            (width, height),
            Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.ANTIALIAS,
        )
        preview_image = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=preview_image)
        self.preview_label.image = preview_image

    def detection(self):
        if self.prediction_worker_running:
            self.set_status(
                "A prediction is still finishing. Please wait before starting another.",
                "#1d4ed8",
            )
            return

        image_path = self.open_img(None)
        if not image_path:
            return

        self.prediction_sequence += 1
        prediction_id = self.prediction_sequence
        self.active_prediction_id = prediction_id
        self.set_result("Processing...", "#e8e3f3", "#49396d")
        self.set_status("Processing image...", "#1d4ed8")
        self.upload_button.configure(state="disabled")

        thread = threading.Thread(
            target=self.run_prediction,
            args=(image_path, prediction_id),
            daemon=True,
        )
        try:
            self.prediction_worker_running = True
            thread.start()
        except RuntimeError:
            logger.exception("Unable to start the prediction worker.")
            self.prediction_worker_running = False
            self.active_prediction_id = None
            self.upload_button.configure(state="normal")
            self.set_result("Prediction failed", "#fee2e2", "#b91c1c")
            self.set_status("Unable to start prediction. Please try again.", "#dc2626")

    def run_prediction(self, image_path, prediction_id):
        started_at = time.perf_counter()
        logger.info("Prediction worker started for %s.", os.path.basename(image_path))
        try:
            result_label = _PredictionResult(self.pending_result_queue, prediction_id)
            test2.detect(image_path, result_label)
            if not result_label.reported:
                self.pending_result_queue.put(
                    (
                        prediction_id,
                        "The model returned without a prediction result.",
                        "",
                    )
                )
            logger.info(
                "Prediction worker returned after %.2f seconds.",
                time.perf_counter() - started_at,
            )
        except Exception:
            logger.exception("Prediction failed.")
            self.pending_result_queue.put(
                (
                    prediction_id,
                    "Prediction failed. Check that the model file and image are available, then try again.",
                    "",
                )
            )

    def reset(self):
        self.prediction_sequence += 1
        self.active_prediction_id = None
        self.selected_path = ""
        self.preview_source = None
        self.preview_title.configure(text="Selected Image")
        self.preview_label.configure(image="", text="No image selected")
        self.preview_label.image = None
        self.set_result("Awaiting image selection")
        self.upload_button.configure(
            state="disabled" if self.prediction_worker_running else "normal"
        )

    def reset(self):
        self._clear_selection()
        if self.prediction_worker_running:
            self.set_status(
                "Selection cleared. Wait for the current prediction to finish before uploading again.",
                "#1d4ed8",
            )
        else:
            self.set_status("Ready. Select an image to begin analysis.", "#0f766e")


window = Tk()
create_gui(window)
window.mainloop()
