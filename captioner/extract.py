import magnet as mag

def Extractor(architecture):
	import torchvision.models

	architecture = getattr(torchvision.models, architecture)
	model = architecture(pretrained=True).to(mag.device)
	_detach_head(model)

	return model

@mag.eval
def extract(extractor, dataloader):
	import torch

	from utils import get_tqdm
	tqdm = get_tqdm()
	
	batch_size = dataloader.batch_size
	num_images = len(dataloader.dataset)
	feature_size = _feature_size(extractor, dataloader)

	features = torch.zeros(num_images, feature_size).to(mag.device)

	for i, (x, _) in enumerate(tqdm(iter(dataloader))):
		y = extractor(x.to(mag.device))
		features[i * batch_size: min((i + 1) * batch_size, num_images)] = y

	return features

def _detach_head(model):
	from types import MethodType
	from torch.nn import AdaptiveAvgPool2d

	def extractor_forward(self, x):
		    x = self.conv1(x)
		    x = self.bn1(x)
		    x = self.relu(x)
		    x = self.maxpool(x)

		    x = self.layer1(x)
		    x = self.layer2(x)
		    x = self.layer3(x)
		    x = self.layer4(x)

		    x = self.avgpool(x)
		    x = x.view(x.size(0), -1)

		    return x

	model.feature_size = model.fc.in_features
	del model.fc
	model.avgpool = AdaptiveAvgPool2d(1)
	model.forward = MethodType(extractor_forward, model)

def __main():
	import torch

	from pathlib import Path
	from hparams import image_shape, architecture, num_workers
	from hparams import extractor_batch_size as batch_size

	DIR_DATA = Path('~/.data/COCO').expanduser()

	#if (DIR_DATA / 'train/features.pt').exists(): return

	dataloader = get_dataloaders(DIR_DATA, image_shape, batch_size, num_workers)
	extractor = Extractor(architecture)

	for mode in ('train', ):
		print(f'Extracting features for set {mode}')
		features = extract(extractor, dataloader[mode])
		torch.save(features.to('cpu'), DIR_DATA / mode / 'features.pt')
		
if __name__ == '__main__': __main()