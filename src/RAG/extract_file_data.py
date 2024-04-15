# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 16:35:01 2024

@author: kaiser
"""

pdf_path = 'C:/Users/kaiser/Desktop/Bionik_Marktplatz/example_files/Kaiser et al. - 2023 - Experimentally characterization and theoretical mo.pdf'
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader(pdf_path)
pages = loader.load_and_split()