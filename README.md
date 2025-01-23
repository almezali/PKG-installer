# Arch Linux Package Installer

## Overview
A user-friendly PyQt5-based graphical package management tool specifically designed for Arch Linux systems. This application simplifies package installation, removal, and troubleshooting processes through an intuitive interface.

## Features
- Install remote packages from Arch repositories
- Install local package files (.pkg.tar.zst)
- Remove existing packages
- View detailed package information
- Terminal output logging
- Progress tracking
- Package lock file troubleshooting

## Screenshots
![Main Interface](https://github.com/almezali/PKG-installer/raw/main/Screenshot_S1.png)
![Package Details](https://github.com/almezali/PKG-installer/raw/main/Screenshot_S2.png)

## Prerequisites
- Python 3.x
- PyQt5
- Arch Linux (pacman package manager)
- sudo privileges

## Installation
1. Clone the repository
```bash
git clone https://github.com/almezali/PKG-installer.git
cd PKG-installer
```

2. Install required dependencies
```bash
pip install PyQt5
```

## Usage
1. Run the application
```bash
python package_installer.py
```

2. Package Installation Methods:
- Enter package name and click "Install"
- Browse and select local .pkg.tar.zst file
- Confirm installation in popup dialog

3. Package Removal:
- Enter package name
- Click "Remove"
- Confirm removal in popup dialog

## Troubleshooting
Use the "Solve Problem" button to remove package manager lock files if installation gets stuck.

## Dependencies
- PyQt5
- subprocess
- os

## License
FREE

## Contributing
Contributions are welcome! Please submit pull requests or open issues.

## Author
[almezali]
