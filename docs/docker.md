

---

# 🚀 Docker Guide for OverCast-Cric

This document explains how to containerize, build, and run the complete **OverCast-Cric** project using Docker. This setup provides a consistent and reproducible environment for development, data processing, and model training.

---

##  Prerequisites

Before you begin, ensure you have **Docker Desktop** installed and running on your system.

*   [Download Docker](https://www.docker.com/products/docker-desktop)

---

## 📁 Project Structure

The project is organized as follows. All Docker commands should be run from the `OverCast-Cric/` root directory.

```text
OverCast-Cric/
├── data/
│   ├── processed/    # Cleaned and transformed data
│   ├── raw/
│   │   ├── matches/  # Match JSON files
│   │   ├── players/  # Player performance data
│   │   ├── teams/    # Team performance data
│   │   └── weather/  # Weather data for match days
│   └── squads/       # Team squad information
├── notebooks/
│   └── prediction_model.py # ML model training and predictions
├── scripts/
│   ├── fetch_matches.py
│   ├── fetch_players.py
│   ├── fetch_teams.py
│   ├── fetch_weather.py
│   ├── process_pipeline.py
│   └── test_weather.py
├── requirements.txt
├── Dockerfile
└── docs/
    └── docker.md     # This file
```

---

## 🛠️ Build the Docker Image

This command builds the Docker image from the `Dockerfile` in the project root. It will install all dependencies listed in `requirements.txt` and copy the project files into the image.

#### Command:

```bash
docker build -t overcast-cric-full .
```

*   `-t overcast-cric-full`: Assigns a memorable tag (name) to the image.
*   `.`: Specifies that the build context (including the `Dockerfile`) is the current directory.

---

## ▶️ Run the Docker Container

Once the image is built, you can run it as a container. This command starts the container, maps the necessary ports for Jupyter, and mounts the project directory as a volume for live code changes.

#### Command:

```bash
docker run -it --rm -p 8888:8888  overcast-cric-full
```

*   `-it`: Runs the container in interactive mode with a pseudo-TTY.
*   `--rm`: Automatically removes the container when it exits, keeping your system clean.
*   `-p 8888:8888`: Maps port `8888` on your host machine to port `8888` inside the container, allowing you to access Jupyter Notebook.
**This is crucial for development**, as changes to your local code will be immediately reflected inside the container.

---

## 🔧 Troubleshooting

If you encounter any issues, refer to the table below for common solutions.

| Issue | Solution / Tips |
| :--- | :--- |
| `Dockerfile not found` | Ensure you are in the project's root directory (`OverCast-Cric/`) when running the `docker build` command. |
| `invalid reference format` | Image names must be lowercase. Ensure the tag (e.g., `overcast-cric-full`) does not contain uppercase letters or quotes. |
| `Permission denied` on volume mount | On Linux, you may need to run Docker commands with `sudo`. On Windows/macOS, check your Docker Desktop file-sharing settings. |
| Jupyter Notebook not loading | The host port `8888` might be in use. Try mapping to a different port, e.g., `-p 8890:8888`, and access it via `http://localhost:8890`. |

---

## 📦 Notes

*   **All-in-One Environment**: This Docker setup includes all scripts, data handling logic, and the machine learning training environment in a single container.
  
*   **Development Ready**: Use this container as a full-featured development and execution environment to ensure consistency across different machines.

## 📌 Future Improvements

*   This Docker guide is primarily aimed at local development and reproducible experiments. Future versions may split the image into separate, more lightweight containers for training and prediction tasks.