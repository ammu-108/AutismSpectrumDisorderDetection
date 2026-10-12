# Autism Spectrum Disorder Detection — Project Context

## Original project
GitHub repository: https://github.com/ammu-108/AutismSpectrumDisorderDetection

This is an academic final-year project for ASD detection using preprocessed ABIDE data, a MobileNet CNN model, Python, TensorFlow/Keras, and a Tkinter GUI.

## Environment
- OS: Windows
- Python: 3.10.8
- Git: 2.42.0
- IDE: Visual Studio Code
- Original model: `abide.h5`

## Important original files
- `test_project.py` — Tkinter GUI and image upload flow
- `test2.py` — model loading, image preprocessing, and prediction
- `abide.h5` — saved model
- `images.jpg`, `icon.png`, `upload.png` — existing UI assets

## Current status
- Repository cloned and opened in VS Code.
- Application launches successfully.
- Upload Image opens the file picker.
- No suitable model test input is currently available.
- Python and Git are installed.
- The UI needs improvement.

## Main goal
Preserve the original project unchanged in a separate backup or original Git branch. Develop improvements on a separate branch or clone.

## Development plan
1. Inspect the existing code, dependencies, model input/output shapes, and repository structure.
2. Make the application compatible with the installed Python libraries.
3. Fix cancellation, invalid-file, and error-handling cases.
4. Improve the Tkinter interface while preserving the existing model integration.
5. Identify valid test inputs matching the model's actual training data.
6. Test preprocessing, inference, and GUI behavior separately.
7. Evaluate the model only with appropriate labelled data; report measured results honestly.
8. Add tests, dependency documentation, setup instructions, screenshots, and a clear README.
9. Keep all changes version-controlled and avoid committing credentials or unnecessary large files.

## Rules for AI coding assistance
- Inspect existing code before editing.
- Explain which files will change and why.
- Make small, reviewable changes.
- Do not overwrite or retrain the model without justification.
- Do not fabricate test results or accuracy.
- Do not use random photographs as evidence of model validity.
- Treat predictions as experimental research outputs, not clinical diagnoses.
- After each change, explain how to test it and wait for the result before moving to the next risky change.