'''
This file contains supplementary functions that won't be part of the original flow
'''
from pdf2image import convert_from_path
import os
import tempfile
import cv2
import argparse
from util1 import return_data
from util2 import rearrange_words
from semantic_paragraphs import word2line, line2para
import shutil
import img2pdf
import json

def create_nested_dirs(output_dir):
    if not output_dir:
        tempdir = tempfile.mkdtemp()
    else:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        tempdir = output_dir
    assert os.path.exists(tempdir)
    
    if not os.path.exists(os.path.join(tempdir, "images")):
        os.mkdir(os.path.join(tempdir, "images"))
    if not os.path.exists(os.path.join(tempdir, "grid")):
        os.mkdir(os.path.join(tempdir, "grid"))

    return tempdir


def convert_to_png(pdf_file, output_dir=None, dpi=72, pages=None):
    '''
    Convert the images to PNG.
    PNG is needed as input for VGT fine-tuned on DocLaynet.
    Change it to jpg or something else if a different model needs to be used

    DPI is set to 72 since PDFPlumber uses the same dpi
    '''
    # download poppler and add the path below, if poppler error is faced
    images = convert_from_path(pdf_file, dpi=dpi)#, poppler_path=r"C:\Users\Yash\Downloads\Release-23.10.0-0\poppler-23.10.0\Library\bin")
    output_dir = create_nested_dirs(output_dir)

    for ind,img in enumerate(images):
        #only save the required images
        if pages:
            if ind in pages:
                base_name, _ = os.path.splitext(os.path.basename(pdf_file))
                img.save(os.path.join(output_dir,'images',f'{base_name}_page{ind}.png'))
        else:
            base_name, _ = os.path.splitext(os.path.basename(pdf_file))
            img.save(os.path.join(output_dir,'images',f'{base_name}_page{ind}.png'))
        
    return output_dir


def plot_boxes_on_image(image, coordinates, color=(0,255,0)):
    
    for box in coordinates:
        x0,y0,x1,y1 = box
        cv2.rectangle(image, (int(x0), int(y0)), (int(x1), int(y1)), color, 1)
    return image

if __name__=="__main__":
    args = argparse.ArgumentParser()

    args.add_argument("--pdf-file", type=str, help = "Path of input PDF file")
    args.add_argument("--pages", type=str, default="all", help="pass a single page number or a list of them separated by commas like 0,4,5. Default is all - will process all pages")
    args.add_argument("--output", type=str, help="Location of the output folder where to store json and output PDF")

    args.add_argument("--plot-type", type=str, choices=["semantic", "raw", "word", "semanticWord"], help="Which style to use to plot words on images. Raw will plot the coordinates for paragraphs obtained from pdfplumber. Word will plot the coordinates of each word obtained from PDFPlumber. Semantic will apply the rules given in rules.txt on coordinates from PDFPlumber (raw). SemanticWords will plot semantic+word.")

    arguments = args.parse_args()

    if arguments.pages!="all":
        pages = [int(i) for i in arguments.pages.split(",")] #convert string to integer
    else:
        pages = None # this will convert and save all pages in the input folder
        
    plot_type = arguments.plot_type

    temp_out_dirname = "temp_output"
    image_dir = convert_to_png(arguments.pdf_file, "temp", pages=pages)
    
    
    output_images_dir = os.path.join(temp_out_dirname, "plotted_images")
    output_json_dir = os.path.join(temp_out_dirname, "json")
    if not os.path.exists(temp_out_dirname):
        os.mkdir(temp_out_dirname)
        os.mkdir(output_images_dir)
        os.mkdir(output_json_dir)
    
    out_json={"pages":{}}
    for ind, img in enumerate(os.listdir(os.path.join("temp", "images"))):

        page_number = os.path.basename(os.path.basename(img.split("_page")[-1])).replace(".png", "")
        paragraph, words = return_data(arguments.pdf_file, int(page_number))

        if arguments.plot_type == "raw":
            page = rearrange_words(paragraph, words)
            coordinates = [block["bounds"][:-2] for block in page]
            out_json["pages"].update({str(ind):page})

        elif arguments.plot_type == "word":
            coordinates = [[word["x0"], word["top"], word["x1"], word["bottom"]] for word in words]
            out_json["pages"].update({str(ind):words})
        elif "semantic" in arguments.plot_type:
            page = rearrange_words(paragraph, words)
            merged_words = word2line(page)
            merged_words_with_kids = rearrange_words(merged_words, words)
            merged_paragraph = line2para(merged_words_with_kids)
            
            if arguments.plot_type=="semanticWord":
                # print(merged_words_with_kids)
                merged_paragraph = rearrange_words(merged_paragraph, words)

            coordinates = [block["bounds"][:-2] for block in merged_paragraph]
            out_json["pages"].update({str(ind):merged_paragraph})
        
        img_file = cv2.imread(os.path.join("temp","images", img))
        out_img = plot_boxes_on_image(img_file, coordinates)
        
        if arguments.plot_type == "semanticWord":
            word_coordinates = [[word["x0"], word["top"], word["x1"], word["bottom"]] for word in words]
            out_img = plot_boxes_on_image(out_img, word_coordinates, color=(0,0,255))
            
        cv2.imwrite(os.path.join(temp_out_dirname, "plotted_images", img), out_img)
    shutil.rmtree("temp")


    imgs = []
    for fname in os.listdir(temp_out_dirname+"/plotted_images"):
        if not fname.endswith(".png"):
            continue
        path = os.path.join(temp_out_dirname+"/plotted_images", fname)
        if os.path.isdir(path):
            continue
        imgs.append(path)
    out_pdf_file, suffix = os.path.splitext(os.path.basename(arguments.pdf_file))

    out_pdf = out_pdf_file+"_"+arguments.plot_type
    if not os.path.exists(arguments.output):
        os.mkdir(arguments.output)
    with open(f"{arguments.output}/{out_pdf}.pdf","wb") as f:
        f.write(img2pdf.convert(imgs))

    with open(f'{arguments.output}/{out_pdf}.json', 'w') as fp:
        json.dump(out_json, fp)

    shutil.rmtree(temp_out_dirname)