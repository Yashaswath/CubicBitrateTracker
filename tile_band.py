import os
import subprocess

# Function to get video duration
def get_video_duration(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "csv=p=0", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return float(result.stdout.strip())

def get_video_segements(file_path,segement_dir,segement_time=0.5):
    # Ensure segments directory exists
    os.makedirs(output_segments_dir, exist_ok=True)
    command = [
    "ffmpeg",
    "-i", f"{file_path}",
    "-c:v", "libx264",
    "-c:a", "aac",
    "-strict", "experimental",
    "-b:a", "192k",
    "-force_key_frames", f"expr:gte(t,n_forced*{segement_time})",
    "-f", "segment",
    "-segment_time", f"{segement_time}",
    "-reset_timestamps", "1",
    "-map", "0",
    f"{segement_dir}/output_part_%d.mp4"
    ]
    subprocess.run(command,check=True)

# Function to calculate bitrate
def calculate_bitrate(file_path):
    # file_size_bytes = os.path.getsize(file_path)
    # duration_seconds = get_video_duration(file_path)
    # file_size_bits = file_size_bytes * 8
    # return file_size_bits / duration_seconds
    command = [
    "ffprobe",
    "-v", "error",
    "-select_streams", "v",
    "-show_entries", "stream=bit_rate",
    "-of", "default=noprint_wrappers=1",
    f"{file_path}"
    ]
    result= subprocess.run(command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True)
    # print(result.stdout.strip().split('=')[1])
    return int(result.stdout.strip().split('=')[1])


# Function to get video duration
def get_video_resolution(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    result= result.stdout.strip().split('x')
    return (int(result[0])//3,int(result[1])//2)
  
# Extract tiles and calculate bitrates
input_video = "output_cube_london_10s.mp4"
tile_width=100
width,height=get_video_resolution(input_video)

# output_tile = "tile.mp4"
output_segments_dir = f"{input_video.replace('.mp4','_')}segments"
tile_dict={
    "tile_1_left.mp4":f"{tile_width}:{height}:0:0",
    "tile_2_left.mp4":f"{tile_width}:{height}:{width}:0",
    "tile_3_left.mp4":f"{tile_width}:{height}:{2*width}:0",
    "tile_4_left.mp4":f"{tile_width}:{height}:0:{height}",
    "tile_5_left.mp4":f"{tile_width}:{height}:{width}:{height}",
    "tile_6_left.mp4":f"{tile_width}:{height}:{2*width}:{height}",
    "tile_1_right.mp4":f"{tile_width}:{height}:{width-tile_width}:0",
    "tile_2_right.mp4":f"{tile_width}:{height}:{2*width-tile_width}:0",
    "tile_3_right.mp4":f"{tile_width}:{height}:{3*width-tile_width}:0",
    "tile_4_right.mp4":f"{tile_width}:{height}:{width-tile_width}:{height}",
    "tile_5_right.mp4":f"{tile_width}:{height}:{2*width-tile_width}:{height}",
    "tile_6_right.mp4":f"{tile_width}:{height}:{3*width-tile_width}:{height}"
}

# Split the tile video into 10-frame segments
get_video_segements(input_video,output_segments_dir)

bitrates=[]
diff_bitrates=[[0,0,0,0,0,0,0,0,0,0,0,0],]
#Structure 
#[segement_0 values, segment_1 values, ...]
#Each segement_no values=list of tile value differences
# Calculate bitrate for each segment
# os.makedirs(output_segments_dir, exist_ok=True)
# segments = [os.path.join(output_segments_dir, f) for f in os.listdir(output_segments_dir)]
segments = [f"output_part_{i}.mp4" for i in range(0,len(os.listdir(output_segments_dir)))]
for index,segment in enumerate(segments):
    bitrate_dict={}
    diff_bitrate_segment=[]
    for tile_name,crop_value in tile_dict.items():
        # Extract the tile_width x (height_resolution/2) size tiles
        # subprocess.run(["ffmpeg", "-i", input_video, "-vf", "crop=16:16:1024:1536", output_tile])
        # print(segment.replace('.mp4','_')+tile_name)
        # input()
        subprocess.run(["ffmpeg", "-i", output_segments_dir+'/'+segment, "-vf", f"crop={crop_value}", output_segments_dir+'/'+segment.replace('.mp4','_')+tile_name])
        bitrate=calculate_bitrate(output_segments_dir+'/'+segment.replace('.mp4','_')+tile_name)
        bitrate_dict[tile_name]=bitrate
        if index > 0:
             diff_bitrate_segment.append(bitrate - bitrates[index-1][tile_name])
    bitrates.append(bitrate_dict)
    if index >0 :
        diff_bitrates.append(diff_bitrate_segment)
for bitrate in bitrates:
    print(bitrate)
for diff_bitrate in diff_bitrates:
    print(diff_bitrate)

