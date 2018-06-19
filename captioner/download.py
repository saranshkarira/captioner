from pathlib import Path
from captioner.utils import working_directory

image_url = lambda mode: f'http://images.cocodataset.org/zips/{mode}2017.zip'
annotations_url = 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip'

def download_images(mode, path):
	"""
	Downloads the images from the COCO website and extracts them.

	:param mode: 'train' or 'val' according to whether you want to download the training or validation set respectively.
	:param path: Path in which to download the images.
	"""
	try:
		next((path / mode).glob('*.jpg'))
		print('Already downloaded.')
		return # Why bother. Job already done
	except: pass

	_download_and_extract(image_url(mode), path, lambda: os.rename(f'{mode}2017', f'{mode}'))

def download_captions(path):
	"""
	Downloads the captions from the COCO website.

	:param path: Path in which to download the captions. This needs to be the root path to the 'train' and 'val' directories.
	"""
	if (path / 'train' / 'captions.json').exists():
		print('Already downloaded.')
		return # Why bother. Job already done

	def extras():
		import shutil

		for mode in ('train', 'val'):
			os.rename(f'annotations/captions_{mode}2017.json', f'{mode}/captions.json')
		shutil.rmtree('annotations')

	_download_and_extract(annotations_url, path, extras)

@working_directory
def _download_and_extract(url, path, extras=None):
	import wget, os

	from zipfile import ZipFile

	filename = Path(url).name

	# Download if not yet done
	if not Path(filename).exists():
		print('Downloading...')
		wget.download(url)

	print('Extracting...')
	ZipFile(filename).extractall() # Extract

	os.remove(filename) # Remove the zip file since it's no longer needed

	if extras is not None: extras()

def __main():
	from captioner.utils import DIR_DATA

	for mode, name in (('val', 'Validation'), ('train', 'Training')):
		print(f'\n{name} set:')
		download_images(mode, DIR_DATA)

	print('\nCaptions:')
	download_captions(DIR_DATA)

	print('\nDone')

if __name__ == '__main__':
	from utils import launch
	launch(__main)

