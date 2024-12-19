import streamlit as st
import pandas as pd
import os
from PIL import Image
import shutil
import datetime


def load_images(image_folder):
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                   if f.lower().endswith(('png', 'jpg', 'jpeg'))]
    return sorted(image_paths)


def check_already_labeled(df, image_index, column_name):
    cell_content = df.loc[image_index, column_name]

    # If the labeling is finished, the cell content is expected to be a list.
    if isinstance(cell_content, list):
        return True
    # If the labeling is not finished, the cell content is expected to be None.
    elif pd.isna(cell_content):
        return False
    else:
        raise ValueError(f"Unexpected cell content: {cell_content}")


st.set_page_config(page_title="Image Labeling Tool", page_icon="🌟")

with st.sidebar:
    st.header("Image Labeling Tool")
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    image_folder = st.text_input("Enter the path to the image folder:", value="./images")
    label_input = st.text_area("Enter class labels (one per line):", value="label1\nlabel2\nlabel3")
    output_filename = st.text_input("Output Filename:", value=f"{current_time}.csv")
    start_button = st.button("Start Labeling")

if start_button:
    st.session_state.started = True
    st.session_state.image_index = 0
    st.session_state.image_paths = load_images(image_folder)
    st.session_state.label_candidates = [label.strip() for label in label_input.splitlines() if label.strip()]
    st.session_state.labeling_df = pd.DataFrame({
        'Image': st.session_state.image_paths,
        'Label': None,
    })

    if not os.path.exists(image_folder):
        st.error("The specified folder does not exist. Please provide a valid folder path.")
    
    if not label_input:
        st.error("Please provide at least one class label.")
    
    if not output_filename:
        st.error("Please provide an output filename.")

    if not st.session_state.image_paths:
        st.error("No images found in the specified folder.")
    

# If started, show the labeling page
if "started" in st.session_state and st.session_state.image_index < len(st.session_state.image_paths):
    st.title(f"Progress: {st.session_state.image_index + 1} / {len(st.session_state.image_paths)}")

    # Get current image information
    image_index = st.session_state.image_index
    image_path = st.session_state.image_paths[image_index]
    image = Image.open(image_path)

    # Display current image
    st.image(image, caption=os.path.basename(image_path), use_column_width=True)

    # Check if the image is already labeled
    df = st.session_state.labeling_df
    is_already_labeled = check_already_labeled(df, image_index, 'Label')
    st.write(f"is_already_labeled: {is_already_labeled}")

    if is_already_labeled:
        st.write("### Previously selected labels:")
        prev_selected_labels = df.loc[image_index, 'Label']
        selected_labels = []
        for label in st.session_state.label_candidates:
            checked = label in prev_selected_labels
            if st.checkbox(label, value=checked, key=label):
                selected_labels.append(label)
        
    else:
        st.write("### Select class labels:")
        selected_labels = []
        for label in st.session_state.label_candidates:
            if st.checkbox(label, key=f"{image_index}_{label}"):
                selected_labels.append(label)

    st.write("Selected Labels:", selected_labels)
    st.write(df)

    if st.button("Next"):
        # Save labels to dataframe
        df.loc[image_index, 'Label'] = selected_labels
        st.session_state.labeling_df = df

        # Update index & rerun
        st.session_state.image_index += 1
        st.rerun()  

    if st.button("Back"):
        # Save labels to dataframe
        df.loc[image_index, 'Label'] = selected_labels
        st.session_state.labeling_df = df

        # Update index & rerun
        st.session_state.image_index -= 1
        st.rerun()
    
# If all images are labeled, show the download page
# if "started" in st.session_state and st.session_state.index == len(st.session_state.image_paths):
#     st.title("All images labeled!")
#     st.write("Showing the summary of your labeling:")
#     st.write(st.session_state.labeling_df)
#     st.download_button(
#         label="Download CSV",
#         data=st.session_state.labeling_df.to_csv(index=False),
#         file_name=output_filename,
#         mime="text/csv"
#     )


