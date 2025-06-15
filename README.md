# RigMaster UI

**RigMaster UI** is a custom rigging interface for Autodesk Maya, developed using PySide6. It simplifies and streamlines common rigging operations like control creation, FK/IK setups, UV pinning, and skinCluster management. Designed for rigging artists and TDs, it combines flexibility with ease-of-use to accelerate the rigging workflow.

---

## 🌟 Features

* **Auto Naming**: Automatically names controls, joints, and groups.
* **Control Type Selection**: Choose from predefined shapes like `Circle`, `Cube`, `Sphere`, and `Arrow`.
* **FK/IK Rigging Tools**: Easily create FK chains with optional root and offset groups.
* **Constraint Management**: Add and manage world/local parent constraints.
* **UV Pin Setup**: Automate the process of creating UV pin constraints for better deformation control.
* **SkinCluster Support**: Connect new joints to existing or new skinClusters.

---

## 📁 Project Structure

```
rig_master/
├── gui/
│   └── uvPin_ui.py            # UI layout for UVPin setup (converted from Qt Designer)
├── src/
│   ├── maya_operations.py     # Maya command wrappers
│   └── uv_pin_setup.py        # Logic for UV Pin setup, connects to UI
├── rig_master_ui.py           # RigMaster main UI class and logic
├── RigMasterUi.py             # Main window UI (converted from Qt Designer)
└── images/
    ├── rigmaster_main_ui.png
    ├── fk_controls.png
    └── constraint_setup.png
```

---

## 🔧 Installation

1. Copy all Python files into your Maya scripts directory or project folder.
2. Open Maya and run the following in the Script Editor:

```python
from rig_master.rig_master_ui import RigMasterSetup
window = RigMasterSetup()
window.show()
```

---


## 🚀 Tech Stack

* Autodesk Maya 2022+
* Python 3.x
* PySide6

---

## 👨‍💼 Author

**Vivek Dixit**
Pipeline TD | 6+ years in the VFX industry

---

## 📄 License

This project is intended for internal studio use and learning purposes. Contact the author for commercial use or contributions.

---
