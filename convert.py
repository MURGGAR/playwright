from moviepy.editor import VideoFileClip

# Function to convert WebM to MP4
def convert_webm_to_mp4(webm_path, mp4_path):
    # Load the WebM file
    video = VideoFileClip(webm_path)
    
    # Write the video to MP4 format
    video.write_videofile(mp4_path, codec='libx264')

# Paths to the input WebM file and output MP4 file
webm_path = 'test.webm'
mp4_path = 'output_video.mp4'

# Perform the conversion
convert_webm_to_mp4(webm_path, mp4_path)
