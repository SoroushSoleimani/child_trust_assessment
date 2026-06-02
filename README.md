# Child Trust Assessment Software

This repository contains a specialized research application developed in Python for conducting trust assessment experiments among primary school children (grades 1-2). The software provides a structured, child-friendly, and distraction-free environment to display video stimuli, collect responses, and automate data logging into Excel files.

## Overview

The software is designed to meet strict research requirements, ensuring data integrity and participant focus. It features two distinct test modules for male and female participants, with randomized video sequences to eliminate bias.

## Key Features

### 1. Research Design
- **Randomization:** Each participant receives 8 videos in a completely randomized order.
- **Structured Assessment:** Four mandatory questions (Correctness, Niceness, Trust, Self-Disclosure) are presented after each video. Navigation is locked until all responses are recorded.
- **Rest Period:** A 30-second automated break is provided after the fourth video, featuring a countdown timer and a manual 'Skip' option.

### 2. User Interface
- **Child-Friendly Design:** Minimalist, neutral, and distraction-free UI to ensure focus on the experiment.
- **Environment:** Background imagery is limited to simple nature themes to maintain a calm atmosphere.

### 3. Participant Management
- **Automated Registration:** The system includes an entry form for Name, Surname, Age, and Grade.
- **Automatic ID Generation:** Participant codes (e.g., 1, 2, 3) are generated automatically by scanning the last registered entry.

### 4. Data Collection and Security
- **Excel Integration:** All data is exported to an Excel (.xlsx) file.
- **Data Persistence:** Responses are saved immediately to prevent data loss due to system failures or power outages.
- **Detailed Logs:** Tracks scenario ID, presentation order, responses, response times, and the date/time of the session.
- **Recovery Mode:** Designed to handle interruptions and allow session resumption.

## Technical Requirements
- **Language:** Python
- **IDE:** Visual Studio Code
- **Format:** Supports automated Excel generation for research analysis.

## Usage

1. Clone the repository:
   `git clone https://github.com/SoroushSoleimani/child_trust_assessment.git`

2. Install dependencies:
   `pip install -r requirements.txt`

3. Run the application:
   `python main.py`

Upon launch, the application will prompt the user to select between the 'Male' or 'Female' test modules before proceeding to the participant registration form.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.