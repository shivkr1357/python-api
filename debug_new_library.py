#!/usr/bin/env python3
"""
Debug script for the new library approach
"""

import os
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image

def debug_pdf_conversion():
    """Debug the PDF conversion process"""
    pdf_path = "/Users/pratikranpariya/Downloads/20220929183711.pdf"
    
    print("🔍 Debugging PDF Conversion with New Libraries")
    print("=" * 60)
    
    try:
        # Step 1: Convert PDF to images
        print("📄 Step 1: Converting PDF to images...")
        images = convert_from_path(pdf_path, dpi=300, fmt='PNG')
        print(f"✅ Converted {len(images)} page(s) to images")
        
        for i, image in enumerate(images):
            print(f"\n📸 Page {i+1}:")
            print(f"   Size: {image.size}")
            print(f"   Mode: {image.mode}")
            
            # Save debug image
            debug_path = f"debug_page_{i+1}.png"
            image.save(debug_path)
            print(f"   Saved debug image: {debug_path}")
            
            # Step 2: Preprocess for OCR
            print("🔧 Step 2: Preprocessing image for OCR...")
            img_array = np.array(image)
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            print(f"   Grayscale shape: {gray.shape}")
            
            # Apply preprocessing
            denoised = cv2.medianBlur(gray, 3)
            binary = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # Save preprocessed image
            preprocessed_path = f"debug_preprocessed_{i+1}.png"
            cv2.imwrite(preprocessed_path, binary)
            print(f"   Saved preprocessed image: {preprocessed_path}")
            
            # Step 3: OCR
            print("🔤 Step 3: Running OCR...")
            try:
                text = pytesseract.image_to_string(binary, config='--psm 6')
                print(f"   OCR text length: {len(text)} characters")
                print(f"   First 200 chars: {text[:200]}...")
                
                if text.strip():
                    print("✅ OCR successful - text extracted")
                else:
                    print("⚠️ OCR returned empty text")
                    
            except Exception as e:
                print(f"❌ OCR error: {e}")
                
            # Step 4: Content analysis
            print("📊 Step 4: Analyzing content...")
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
            
            has_lines = lines is not None and len(lines) > 20
            print(f"   Detected lines/tables: {has_lines}")
            
            # Text density
            text_pixels = np.sum(binary == 0)
            total_pixels = binary.size
            text_density = text_pixels / total_pixels
            print(f"   Text density: {text_density:.3f}")
            
    except Exception as e:
        print(f"❌ Error in PDF conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_pdf_conversion()
