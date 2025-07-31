# BiomimeticsMarketplace
## Transferplattform für Biologie und Technik Teilvorhaben C

Funded by BMFTR --> Förderkennzeichen 01IO2306C

## Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Steps](#steps)
- [Usage](#usage)
- [Architecture and Technology](#architecture-and-technology)
- [License](#license)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)

## About the Project

The BMFTR-funded project ["Transferplattform für Biologie und Technik"](https://www.transferwerkstatt.de/vorhaben/2023/transferplattform)  aims to strengthen the transfer of knowledge between different scientific disciplines. Our project specifically targets the collaboration between various scientific disciplines and uses the exchange between biology and engineering as a demonstration.

### Project Partners

- **Senckenberg Gesellschaft für Naturforschung (SGN)**
- **Technische Hochschule Mittelhessen (THM)**
- **Leibniz-Institut für Verbundwerkstoffe (LIVW)**

### Project Duration

The project has a runtime of 3 years, with the kickoff scheduled for early 2024.

### Project Goals

To demonstrate how knowledge transfer can be optimized, we have chosen the transfer between the relatively unrelated scientific disciplines of biology (represented by SGN) and engineering (represented by THM and LIVW). The prototype for this transfer was developed and implemented as part of the sub-project C "Technische Herausforderungen im Bereich Verbundwerkstoffe" at the Leibniz-Institut für Verbundwerkstoffe.

### Transfer Process

The transfer process occurs in three sequential steps, with the BiomimeticsMarketplace serving as a prototype for the implementation of the first step. The primary goal is to enable experts from one scientific discipline to find and collaborate with experts from the other discipline to solve specific issues.

### How It Works

The platform operates through a user-friendly, browser-based application that allows users to input a query into a search field. For engineers, the focus is on finding smarter, often more resource-efficient solutions to technical problems. By describing their technical issue, they can search for biologists who study organisms facing similar challenges, which can serve as natural role models for innovative engineering solutions.

For biologists, the focus is more on finding engineers that can help explain observed phenomena through their knowledge in areas such as FEM or CFD simulation and material properties. It is also possible to describe a phenomenon observed in nature and search for a partner that can help implement the underlying effect into an innovative product.

### Query Translation and Search

The platform first translates the query by breaking it down to its core and adding relevant terms related to the opposite discipline. This enhanced query is then used to perform a semantic search in the databases of SGN and LIVW to find relevant experts. The search results provide the expert's name, their institution, a brief description of how they can contribute to solving the query, and the underlying resources, including DOI and links to publications.

## Features

- User-friendly interface

## Installation

#### Prerequisites

Additionally, you need to clone and install the `ragpipeline` module from GitLab.

#### Steps

1. **Clone the repository:**
```bash
https://github.com/KaiMa92/BiomimeticsMarketplace.git
```

2. **Set API Keys:**
Rename `.env.example` to `.env` and paste your API Keys here.

3. **Clone and install the ragpipeline repository:**

Clone the [ragpipeline](https://gitlab.rhrk.uni-kl.de/wisskomm/ragpipeline) repository and install dependencies:

```bash
git clone git@gitlab.rhrk.uni-kl.de:wisskomm/ragpipeline.git
cd ragpipeline
```
```
python -m pip install .
```
4. **Install further dependencies**:

```bash
cd biomimeticsmarketplace
pip install -r requirements.txt
```

5. **Add directorys for agents**: 

This directory hold the system prompts in plain text with .txt extension
```bash
cd biomimeticsmarketplace
mkdir agents
```
to run the app at least the following files are mandatory: bio_documents_explain.txt, bio_expert_summarize.txt, categorize.txt, eng_documents_explain.txt, eng_expert_summarize.txt, enrich_bio_query.txt, enrich_eng_query.txt

6. **Add directorys for datasets**: 
```bash
cd biomimeticsmarketplace
mkdir datasets
```
to create datasets use the IndexManager class from ragpipeline.

### Usage

1. **Start the application and server**
```bash
cd biomimeticsmarketplace
python run.py
```
2. **Open development server**

Open developmentserver in your browser: http://127.0.0.1:5000/

## Architecture and Technology

- **Embedding Model and Large Language Model (LLM)**
The embedding model (e5-mistral-7b-instruct) and large language model (mistral-large-instruct) used in this project are hosted by the Gesellschaft für wissenschaftliche Datenverarbeitung mbh Göttingen (GWDG), ensuring compliance with the General Data Protection Regulation (DSGVO).

- **RAG Framework**
The Retrieval-Augmented Generation (RAG) framework used in this project is [ragpipeline](https://gitlab.rhrk.uni-kl.de/wisskomm/ragpipeline), which relies on llama-index. This framework enables efficient and accurate retrieval of relevant information from large datasets.

- **Frontend**
The frontend of the web application is built using JavaScript and Slick, providing a smooth and responsive user interface.

## License

## Contact

For questions or feedback, please contact max.kaiser@leibniz-ivw.de

## Acknowledgments

- **Funded by BMFTR under Förderkennzeichen 01IO2306C**
- **Thanks to Andreas Gebhard for all the frontend support**
- **Thank you very much for the freedom and trust you have given me, Matze**
- **Thanks to the Gesellschaft für wissenschaftliche Datenverarbeitung mbH Göttingen for hosting the DSGVO-compliant language models**
- **Thanks to the project partners**