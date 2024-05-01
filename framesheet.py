import cv2
import os
import argparse


# Settings

# Font settings

font = cv2.FONT_HERSHEY_DUPLEX

detail_font_scale = 1
detail_font_colour = (0, 0, 0)
detail_line_thickness = 2

time_font_scale = 3
time_font_colour = (255, 255, 255)
time_line_thickness = 4
time_stroke_thickness = 10

# Image settings

background_color = (255, 255, 255)
frame_gap = 20
sheet_width = 1080
# sheet_width = None

class Details:
    def __init__(self, video_path):
        self.path = video_path
        self.file_name = self.get_file_name()
        self.file_size = None
        self.file_size_string = None
        self.resolution = self.get_resolution()
        self.duration_seconds = self.get_duration()
        self.duration_string = self.get_duration_string()
        self.frame_rate = None
        
        self.get_file_size()
        
    def get_file_name(self):
        return os.path.basename(self.path)
        
    def get_resolution(self):
        video = cv2.VideoCapture(self.path)
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return f"{width}x{height}"
    
    def get_duration(self):
        video = cv2.VideoCapture(self.path)
        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_rate = int(video.get(cv2.CAP_PROP_FPS))
        duration = total_frames / frame_rate
        return duration
    
    def get_duration_string(self):
        return hms_string(self.duration_seconds)
    
    def get_file_size(self):
        self.file_size = os.path.getsize(self.path)
        self.file_size_string = bytes_to_string(self.file_size)
        
def hms_string(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{int(hours)}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"
    
def bytes_to_string(byte):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if byte < 1024:
            return f"{byte:.2f} {unit}"
        byte /= 1024

class Frame:
    def __init__(self, frame, frame_number, frame_rate):
        self.frame = frame
        self.frame_number = frame_number
        self.frame_rate = frame_rate
        self.timestamp = self.get_timestamp()
        
    def get_timestamp(self):
        seconds = self.frame_number / self.frame_rate
        return hms_string(seconds)
    


    
def create_frame_images(selected_frame_data, frame_rate, rows, columns, framesheet):
    images = []
    for i, frame in enumerate(selected_frame_data):
        frame_image = frame.frame
        timestamp = frame.get_timestamp()
        
        auto_line_thickness = time_line_thickness * time_font_scale
        auto_stroke_thickness = time_stroke_thickness * time_font_scale
        
        # create an image with the timestamp
        timestamp_text = timestamp
        
        text_position = (10, int(30 * time_font_scale))
        
        # add a stroke to the timestamp
        cv2.putText(frame_image, timestamp_text, text_position, font, time_font_scale, (0, 0, 0), auto_line_thickness+auto_stroke_thickness)
        
        # add the timestamp
        cv2.putText(frame_image, timestamp_text, text_position, font, time_font_scale, time_font_colour, auto_line_thickness)
        
        images.append(frame_image)
        
    return images
    
def create_framesheet_grid(images, rows, columns):
    framesheet = None
    for i in range(0, len(images), columns):
        row = images[i:i+columns]
        
        # Add a gap between the frames in a row
        row = [cv2.copyMakeBorder(img, 0, 0, 0, frame_gap, cv2.BORDER_CONSTANT, value=background_color) for img in row]
        
        row = cv2.hconcat(row)
        
        if framesheet is None:
            framesheet = row
        else:
            try:
                framesheet = cv2.vconcat([framesheet, row])
            except:
                break
        
        # Add a gap between the rows
        framesheet = cv2.copyMakeBorder(framesheet, 0, frame_gap, 0, 0, cv2.BORDER_CONSTANT, value=background_color)
    
    # add the border to the top and left of the framesheet
    framesheet = cv2.copyMakeBorder(framesheet, frame_gap, 0, frame_gap, 0, cv2.BORDER_CONSTANT, value=background_color)
        
    return framesheet
    
def add_detail_space(framesheet):
    # add a blank space at the top of the framesheet
    framesheet = cv2.copyMakeBorder(framesheet, int(30 * detail_font_scale * 4) + frame_gap, 0, 0, 0, cv2.BORDER_CONSTANT, value=background_color)
    
    return framesheet
    
def add_details(framesheet, video_path):
    # add the video details to the framesheet at the top
        details = Details(video_path)
        detail_text = {
            f"File Name: ": f"{details.file_name}",
            f"File Size: ": f"{details.file_size_string} ({details.file_size} bytes)",
            f"Resolution:": f"{details.resolution}",
            f"Duration:  ": f"{details.duration_string}",
        }
        
        for i, (label, value) in enumerate(detail_text.items()):                       
            text_position = (frame_gap, frame_gap + int(frame_gap * detail_font_scale) + (i * int(30 * detail_font_scale)))
                       
            # add the text, making each label have the same width
            cv2.putText(framesheet, label, text_position, font, detail_font_scale, detail_font_colour, detail_line_thickness)
            cv2.putText(framesheet, value, (text_position[0] + int(200 * detail_font_scale), text_position[1]), font, detail_font_scale, detail_font_colour, detail_line_thickness)
            
        return framesheet

def add_watermark(framesheet, watermark_text):
    transparency = 0.98
    
    # add the watermark to the framesheet at the top right
    # make the text right aligned, and slightly transparent
    watermark_font_scale = 5
    watermark_font_base_colour = (0, 0, 0)
    
    # calculate the transparency based on the background_color
    watermark_font_colour = tuple([int((1 - transparency) * watermark_font_base_colour[i] + transparency * background_color[i]) for i in range(3)])
    
    watermark_line_thickness = 10
    watermark_text = watermark_text
    
    text_size = cv2.getTextSize(watermark_text, font, watermark_font_scale, watermark_line_thickness)
    text_position = (framesheet.shape[1] - text_size[0][0] - frame_gap, frame_gap + text_size[0][1])
    
    # add the watermark
    cv2.putText(framesheet, watermark_text, text_position, font, watermark_font_scale, watermark_font_colour, watermark_line_thickness)
    
    return framesheet


def create_framesheet(video_path, output_path, rows, columns):
    # Load the video
    video = cv2.VideoCapture(video_path)
    
    # get the folder that the video is in
    video_folder = os.path.dirname(video_path)
    
    # set the output path to the video folder if not provided
    if output_path == "framesheet.png":
        output_path = f"{video_folder}/framesheet.png"
        
    # if the output path is a folder, save the framesheet in the folder
    if os.path.isdir(output_path):
        output_path = f"{output_path}/framesheet.png"
        
        # if the folder does not exist, create it
        if not os.path.exists(output_path):
            os.makedirs(output_path)
    
    # Check if video is opened successfully
    if not video.isOpened(): 
        print("Error opening video file")
        return None

    # Get total number of frames in the video
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    # get video frame rate
    frame_rate = video.get(cv2.CAP_PROP_FPS)

    # If total_frames is 0, then the video might not be compatible with cv2
    if total_frames == 0:
        print("The video might not be compatible with cv2")
    else:
        print(f"Total frames: {total_frames}")
        print(f"Frame rate: {frame_rate}")

    # Calculate the step size to evenly spread the frames
    step_size = total_frames // ((rows * columns)+1)
    print(f"Step size: {step_size}")

    # Create a list to store the selected frames
    selected_frames = []
    selected_frame_data = []
    
    frames_to_grab = rows * columns

    print("\nSelecting frames...", end="\r")
    # Iterate through the frames and select the ones to include in the framesheet
    for i in range(0, total_frames, step_size):
        # Set the current frame position
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        
        # skip the first frame
        if i == 0:
            continue

        # Read the frame
        ret, frame = video.read()

        # If the frame was read successfully, add it to the selected frames list
        if ret:
            selected_frames.append(frame)
            frame_object = Frame(frame, i, frame_rate)
            selected_frame_data.append(frame_object)
            print(f"Selecting frames... {len(selected_frames)}/{frames_to_grab}", end="\r")
            
    # scrap the first frame
    # selected_frames = selected_frames[1:]
    # selected_frame_data = selected_frame_data[1:]
    print("Frames selected successfully")
            
    # save the selected frames to a folder
    if not os.path.exists('selected_frames'):
        os.makedirs('selected_frames')
    for i, frame in enumerate(selected_frames):
        cv2.imwrite(f"selected_frames/frame_{i}.png", frame)

    # Initialize the framesheet image
    framesheet = None
    
    # Generate the images with timestamps
    images = create_frame_images(selected_frame_data, frame_rate, rows, columns, framesheet)
        
    # rescale the images to fit the sheet width
    if sheet_width is not None:
        image_width = (sheet_width // columns) - frame_gap
        image_height = int(image_width * (images[0].shape[0] / images[0].shape[1]))
            
        print(f"\nSheet width: {sheet_width}")
        print(f"Original image width: {images[0].shape[1]}")
        print(f"Image width: {image_width}")
        print(f"Original image height: {images[0].shape[0]}")
        print(f"Image height: {image_height}")
        
        images = [cv2.resize(img, (image_width, image_height)) for img in images]   
    
    # Create the framesheet grid image
    framesheet = create_framesheet_grid(images, rows, columns)
    
    # Add the details to the framesheet
    framesheet = add_detail_space(framesheet)
    framesheet = add_watermark(framesheet, "Bane")
    framesheet = add_details(framesheet, video_path)

    # Save the framesheet image
    cv2.imwrite(output_path, framesheet)

    # Release the video capture object
    video.release()

    print(f"\nFramesheet created successfully at {output_path}")
    
    # delete the selected frames folder
    for file in os.listdir('selected_frames'):
        os.remove(f"selected_frames/{file}")
    os.rmdir('selected_frames')


def validate_input(video_path, output_path, rows, columns):
    if video_path is None or video_path == "":
        video_path = input("Enter the video file path: ")
    
    if output_path is None or output_path == "":
        output_path = "framesheet.png"
        
    if rows is None or rows == "":
        rows = 10
    else:
        rows = int(rows)
        
    if rows < 1:
        print("Rows must be greater than 0")
        raise ValueError
        
    if columns is None or columns == "":
        columns = 4
    else:
        columns = int(columns)
        
    if columns < 1:
        print("Columns must be greater than 0")
        raise ValueError
    
    return video_path, output_path, rows, columns

if __name__ == "__main__":
    # set up the argument parser
    parser = argparse.ArgumentParser(description="Create a framesheet from a video file")
    parser.add_argument("video", help="Path to the video file")
    parser.add_argument("-o", "--output", help="Path to save the framesheet", default="framesheet.png")
    parser.add_argument("-r", "--rows", help="Number of rows in the framesheet", default=10, type=int)
    parser.add_argument("-c", "--columns", help="Number of columns in the framesheet", default=4, type=int)
    
    # parse the arguments
    args = parser.parse_args()
    
    # get the arguments, set the default values if not provided
    video_path = args.video
    output_path = args.output
    rows = args.rows
    columns = args.columns
    
    if not os.path.exists(video_path):
        print(f"Video file not found at {video_path}")
        raise FileNotFoundError
    
    video_path, output_path, rows, columns = validate_input(video_path, output_path, rows, columns)
        

    create_framesheet(video_path, output_path, rows, columns)