# Autism Spectrum Disorder Detection

This final-year project demonstrates Autism Spectrum Disorder (ASD)
classification from brain MRI images using an existing trained,
MobileNet-based model. The Tkinter interface runs the model stored in
`abide.h5`; this project does not automatically verify that a selected image
is a brain MRI.

## Project technologies

- Python and Tkinter for the desktop interface
- TensorFlow/Keras for model loading and inference
- Pillow for image decoding and preview
- NumPy for preprocessing arrays
- The existing trained model file `abide.h5`

## Current application workflow

Run the application from the project directory so that `abide.h5`, `icon.png`,
and `upload.png` can be found:

```powershell
python test_project.py
```

The user selects a PNG, JPG/JPEG, BMP, GIF, TIF, or TIFF image. The interface
checks that the path exists, that the file extension is supported, that Pillow
can verify and load the image, that its decoded format matches its extension,
and that its dimensions are positive. These are basic file/image checks; they
do **not** establish that the image contains a brain MRI.

For prediction, `test2.py` loads the selected image as RGB at 224 × 224,
converts it to a NumPy array, adds the batch dimension, and divides pixel
values by 255. It loads `abide.h5` with Keras and calls `model.predict`.
The two output indices are mapped in the existing code to `Autism` and
`Control`. Prediction runs on a background thread; Tkinter widget updates are
handled on the main thread.

The interface accepts any supported, readable image, including non-MRI
images. The ASD classifier has no MRI/non-MRI input class, so a prediction
from an unrelated image may be meaningless. The displayed class is therefore
identified as an unverified model output. This application is for research
and demonstration only; it is not a clinical diagnostic tool.

## Requirements and files

Use a Python environment with TensorFlow, Keras, NumPy, and Pillow installed.
Tkinter is included with many standard Python installations. The repository
does not currently include a `requirements.txt`; use package versions
compatible with the existing environment and model.

Keep `abide.h5` and the UI image assets in the project directory when
launching `test_project.py`. The application does not retrain or modify the
trained model.

## Planned future work: MRI input verification

A future extension could screen selected images with a separately evaluated
MRI-vs-non-MRI verifier before passing accepted inputs to the existing ASD
classifier. This verifier has **not** been implemented and is not part of the
current prediction workflow.

Such work would require suitable, labeled MRI and non-MRI datasets, training
and tuning the verifier, and independent evaluation on data not used for
training or tuning. Evaluation should specifically measure false acceptance
of non-MRI images and false rejection of valid MRI images, with patient/study
overlap controlled between data splits. Until that work is completed and
validated, the current application cannot automatically confirm MRI content.
