import os
import sys
import shutil
from datetime import datetime

name_mapping = {
    "F_Cu": "Gerber_TopLayer.GTL",
    "B_Cu": "Gerber_BottomLayer.GBL",
    "F_Mask": "Gerber_TopSolderMaskLayer.GTS",
    "B_Mask": "Gerber_BottomSolderMaskLayer.GBS",
    "F_Paste": "Gerber_TopPasteMaskLayer.GTP",
    "B_Paste": "Gerber_BottomPasteMaskLayer.GBP",
    "F_Silkscreen": "Gerber_TopSilkscreenLayer.GTO",
    "B_Silkscreen": "Gerber_BottomSilkscreenLayer.GBO",
    "Edge_Cuts": "Gerber_BoardOutlineLayer.GKO",
    "In1_Cu": "Gerber_InnerLayer1.GP1",
    "In2_Cu": "Gerber_InnerLayer2.GP2",
    "job": "FlyingProbeTesting.json"
}

def insert_header(file_path, layer_name, version, timestamp):
    header = f"""G04 Layer: {layer_name}*
G04 EasyEDA Pro {version}, {timestamp}*
G04 Gerber Generator version 0.3*
G04 Scale: 100 percent, Rotated: No, Reflected: No*
G04 Dimensions in millimeters*
G04 Leading zeros omitted, absolute positions, 3 integers and 5 decimals*

"""

    with open(file_path, 'r') as original_file:
        content = original_file.read()

    with open(file_path, 'w') as modified_file:
        modified_file.write(header + content)

def rename_files(input_dir, output_dir, version="v2.2.27.1", timestamp=None):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for filename in os.listdir(input_dir):
        name, ext = os.path.splitext(filename)

        if ext == ".DRL":
            shutil.copy(os.path.join(input_dir, filename), os.path.join(output_dir, filename))
            print(f"Copied (no modification): {filename}")
            continue

        for key, new_name in name_mapping.items():
            if key in name:
                new_filename = new_name
                old_filepath = os.path.join(input_dir, filename)
                new_filepath = os.path.join(output_dir, new_filename)

                shutil.copy(old_filepath, new_filepath)

                name_parts = os.path.splitext(new_name)[0].split('_')
                if len(name_parts) > 1:
                    layer_name = name_parts[1]
                else:
                    layer_name = "UnknownLayer"

                insert_header(new_filepath, layer_name, version, timestamp)

                print(f"Copied and converts: {filename} -> {new_filename}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: kicadGerber2lcedaGerber.py <input path> <output path> [version] [timestamp]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else "v2.2.27.1"
    timestamp = sys.argv[4] if len(sys.argv) > 4 else None

    rename_files(input_path, output_path, version, timestamp)
