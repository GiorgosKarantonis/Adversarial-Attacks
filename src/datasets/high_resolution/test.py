# Adversarial Attacks with AdvGAN and AdvRaGAN
# Copyright(C) 2020 Georgios (Giorgos) Karantonis
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import shutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import torch
import torchvision.models as models
import torch.nn.functional as F

from torch.utils.data import Dataset
from torchvision import datasets, transforms
from torch.utils.data.sampler import SubsetRandomSampler

from PIL import Image



class HighResolutionDataset(Dataset):
    def __init__(self, main_dir, transform):
        self.main_dir = main_dir
        self.transform = transform

        self.all_imgs = [file for file in os.listdir(main_dir) if file.endswith('.png')]
        self.df = pd.read_csv('images.csv', header=0)

    def __len__(self):
        return len(self.all_imgs)

    def __getitem__(self, idx):
        img_loc = os.path.join(self.main_dir, self.all_imgs[idx])
        image = Image.open(img_loc).convert("RGB")
        tensor_image = self.transform(image)

        img_name = self.all_imgs[idx].replace('.png', '')
        img_df = self.df.loc[self.df['ImageId'] == img_name]

        true_label = img_df['TrueLabel'].item() - 1
        target_label = img_df['TargetClass'].item() - 1

        return tensor_image, true_label, target_label


def split_dataset(dataset, test_size=.1, shuffle=True):
    random_seed = 42
    dataset_size = len(dataset)
    
    indices = list(range(dataset_size))
    split = int(np.floor(test_size * dataset_size))
    
    if shuffle:
        np.random.seed(random_seed)
        np.random.shuffle(indices)
    
    return indices[split:], indices[:split]



use_cuda = True
print('CUDA Available: ', torch.cuda.is_available())
device = torch.device('cuda' if (use_cuda and torch.cuda.is_available()) else 'cpu')


model = models.inception_v3(pretrained=True)#.to(device)
model.eval()

transform = transforms.Compose([
					transforms.Resize(299), 
					transforms.ToTensor(), 
					transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
				])


dataset = HighResolutionDataset('img', transform=transform)

train_set, test_set = split_dataset(dataset)
train_sampler = SubsetRandomSampler(train_set)
test_sampler = SubsetRandomSampler(test_set)

dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=False)
train_dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=False, sampler=train_sampler)
test_dataloader = torch.utils.data.DataLoader(dataset, batch_size=128, shuffle=False, sampler=test_sampler)
