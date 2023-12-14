This repo contains the code for plotting bounding boxes on PDF pages that are passed as arguments.

### Inference
For simple inference on the give sample PDF file, run:
```
python main_function.py --pdf-file sample_pdf\iebe102.pdf --output output --plot-type raw --pages all
```
### More information
For information about the different fields used, use `python main_function.py -h`, which gives:

```
usage: main_function.py [-h] [--pdf-file PDF_FILE] [--pages PAGES] [--output OUTPUT] [--plot-type {semantic,raw,word,semanticWord}]

options:
  -h, --help            show this help message and exit
  --pdf-file PDF_FILE   Path of input PDF file
  --pages PAGES         pass a single page number or a list of them separated by commas like 0,4,5. Default is all - will process all pages
  --output OUTPUT       Location of the output folder where to store json and output PDF
  --plot-type {semantic,raw,word,semanticWord}
                        Which style to use to plot words on images. 
                        - Raw will plot the coordinates for paragraphs obtained from pdfplumber. 
                        - Word will plot the coordinates of each word obtained from PDFPlumber. 
                        - Semantic will apply the rules given in rules.txt on coordinates from PDFPlumber (raw). 
                        - SemanticWords will plot semantic+word.
```

### Installation
For installation, run:
1. Clone the repository: ```git clone https://github.com/yashsandansing/pdfParser.git```
2. Install the requirements: ```pip install requirements.txt -- no-cache-dir```
3. Run inference command given above
4. If `poppler` error occurs, install poppler by using `sudo apt-get install -y poppler-utils` on linux.


### Colab notebook
Colab notebook link to run a pdf - https://colab.research.google.com/drive/1_CmvYs2V7biCSjzkYqkAOvrF-ySq9EiU?usp=sharing
