import os
from audio import download_audio, split_audio, split_audio_v2
import whisper


def parse_timestamp(timestamp_str):
	"""
	Parse timestamp string in format 'H:MM:SS' to seconds
	"""
	parts = timestamp_str.strip().split(':')
	hours = int(parts[0])
	minutes = int(parts[1])
	seconds = int(parts[2])
	return hours * 3600 + minutes * 60 + seconds


def read_youtube_url(url_file='data/misc/youtube_watch.txt'):
	"""
	Read the YouTube URL from the specified file
	"""
	with open(url_file, 'r') as f:
		url = f.read().strip()
	return url


def create_sections_by_timestamp(timestamps_file='data/misc/timestamps.txt'):
	"""
	Parse the timestamps file and extract the start and end times of
	"Follow Along" / "Hands-On" / "Lab" sections
	
	Returns a list of tuples [(start_seconds, end_seconds), ...]
	"""
	sections_to_cut = []
	
	with open(timestamps_file, 'r') as f:
		lines = f.readlines()
	
	for i, line in enumerate(lines):
		stripped_line = line.strip()
		
		# Check if this line contains "Follow Along"
		if 'Follow Along' not in stripped_line and 'End' not in stripped_line:
			# Extract timestamp from the beginning of the line
			timestamp_part = stripped_line.split()[0]
			timestamp_name = ' '.join(stripped_line.split()[1:]).replace('/', '_')
			start_time = parse_timestamp(timestamp_part)
			
			# Find the end time (start of next section)
			end_time = -1
			for j in range(i + 1, len(lines)):
				next_line = lines[j].strip()
				if next_line:
					next_timestamp = next_line.split()[0]
					end_time = parse_timestamp(next_timestamp)
					break
			
			sections_to_cut.append((start_time, end_time, timestamp_name))
	
	return sections_to_cut


def get_audio():
	"""
	Main function to:
	1. Download audio from YouTube URL
	2. Split into sections
	3. Remove "Follow Along" and "Hands-On" sections
	"""
	
	print("Step 1: Reading YouTube URL...")
	url = read_youtube_url()
	print(f"URL: {url}")
	
	print("\nStep 2: Downloading audio...")
	audio_file = r'/workspaces/speech-to-text/data/audio.mp3'
	if os.path.exists(audio_file):
		print(f"Audio file already exists at {audio_file}. Skipping download.")
	else:
		download_audio(url, output_path=audio_file)
		print(f"Downloaded audio saved to: {audio_file}")
	
	print("\nStep 3: Extracting sections based on timestamps...")
	sections = create_sections_by_timestamp()
	print(f"{len(sections)} sections:")
	for start, end, section_name in sections:
		hours_start = int(start // 3600)
		minutes_start = int((start % 3600) // 60)
		seconds_start = int(start % 60)
		hours_end = int(end // 3600)
		minutes_end = int((end % 3600) // 60)
		seconds_end = int(end % 60)
		print(f"  {hours_start}:{minutes_start:02d}:{seconds_start:02d} - {hours_end}:{minutes_end:02d}:{seconds_end:02d} > {section_name}")
	
	print("\nStep 4: Removing follow alongs from audio and splitting into sections...")
	split_audio_v2(r'/workspaces/speech-to-text/data/audio.mp3', sections)
	
	print("\nDone!")


def transcript_audio_sections(source_dir='data/sections', output_dir='data/transcripts'):
	print("\nTranscribing audio sections...")
	model = whisper.load_model("medium.en")
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	for file_name in os.listdir(source_dir):
		if not file_name.endswith('.mp3'):
			continue
		## If transcript already exists, skip
		output_path = os.path.join(output_dir, file_name.replace('.mp3', '.txt'))
		if os.path.exists(output_path):
			print(f"Transcript for {file_name} already exists. Skipping...")
			continue
		#rewrite the code below with a try catch as to not stop processing if an error occurs
		audio_path = os.path.join(source_dir, file_name)
		print(f"Transcribing {audio_path}...")
		try:
			result = model.transcribe(audio_path)
			with open(output_path, 'w') as f:
				f.write(result['text'])
		except Exception as e:
			print(f"Error transcribing {audio_path}: {e}\n Skipping to next file.")
	return 0


if __name__ == "__main__":
	get_audio()
	transcript_audio_sections()
