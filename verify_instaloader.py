import instaloader
import re

# Initialize Instaloader object
L = instaloader.Instaloader()

def download_instagram_video(instagram_url):
    try:
        # Extract the shortcode from the Instagram URL
        shortcode = re.findall(r'\/(p|reel)\/([a-zA-Z0-9-_]+)', instagram_url)[0][1]

        # Load the post using the shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)

        # Check if the post is a video and return the video URL
        if post.is_video:
            video_url = post.video_url
            return video_url
        else:
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Test with a valid Instagram URL (Replace this with the Instagram Reel URL you want to test)
instagram_url = 'https://www.instagram.com/reel/C_qA3ySN9Vj/?igsh=eG1xanAyeHQzdnEy'  # Example URL
video_url = download_instagram_video(instagram_url)

if video_url:
    print(f"Video URL: {video_url}")
else:
    print("No video found in the provided Instagram URL.")
