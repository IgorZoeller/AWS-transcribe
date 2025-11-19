import yt_dlp
from pydub import AudioSegment
import os

## Check if data folder exists and create it if not
data_folder = 'data'
if not os.path.exists(data_folder):
	os.makedirs(data_folder)

def download_audio(url, output_codec='mp3', output_path='data/audio'):
	'''
	Function to download audio from a given URL and return the file path
	'''
	ydl_opts = {
		'retries': 10,
		'no_warnings': True,
		'extract_audio': True,
		'outtmpl': output_path,
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': output_codec
		}],
	}

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		ydl.extract_info(url, download=True)
	
	return f'{output_path}.{output_codec}'


def split_audio(audio_file, timestamps, output_dir='data/sections'):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	audio = AudioSegment.from_file(audio_file)
	print(f"Loaded audio! Total audio length: {len(audio) / 1000:.2f} seconds")
	for start_sec, end_sec, section_name in timestamps:
		start_ms = start_sec * 1000
		end_ms = end_sec * 1000
		if end_ms < 0:
			end_ms = len(audio)
		print(f"Exporting section '{section_name}' from {start_sec} to {end_sec} seconds...")
		cut_audio = audio[start_ms:end_ms]
		cut_audio.export(f'{output_dir}/{section_name}.mp3', format='mp3')


def split_audio_v2(audio_file, timestamps, output_dir='data/sections'):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	for start_sec, end_sec, section_name in timestamps:
		if os.path.exists(output_dir + '/' + section_name + '.mp3'):
			print(f"Section '{section_name}' already exists. Skipping...")
			continue
		print(f"Exporting section '{section_name}'. Duration = {end_sec - start_sec if end_sec > 0 else f'{start_sec}s to FINISH'} seconds...")
		audio = AudioSegment.from_file(audio_file, start_second=start_sec, duration=end_sec - start_sec if end_sec > 0 else None)
		audio.export(f'{output_dir}/{section_name}.mp3', format='mp3')