import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms, models
from torch.utils.tensorboard import SummaryWriter
import numpy as np
import time
from config import config

class CropLeafClassifier(nn.Module):
    def __init__(self, num_classes=3):
        super(CropLeafClassifier, self).__init__()
        self.resnet = models.resnet18(pretrained=True)
        
        for param in self.resnet.parameters():
            param.requires_grad = False
        
        num_ftrs = self.resnet.fc.in_features
        self.resnet.fc = nn.Sequential(
            nn.Linear(num_ftrs, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )
    
    def forward(self, x):
        return self.resnet(x)

def get_data_transforms():
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(config.IMAGE_SIZE[0]),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(30),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_test_transform = transforms.Compose([
        transforms.Resize(config.IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_test_transform

def get_dataloaders(train_transform, val_test_transform):
    train_dataset = datasets.ImageFolder(
        root=os.path.join(config.AUGMENTED_DATA_DIR, 'train'),
        transform=train_transform
    )
    
    val_dataset = datasets.ImageFolder(
        root=os.path.join(config.PROCESSED_DATA_DIR, 'val'),
        transform=val_test_transform
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=config.SHUFFLE,
        num_workers=config.NUM_WORKERS,
        pin_memory=config.PIN_MEMORY
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=config.NUM_WORKERS,
        pin_memory=config.PIN_MEMORY
    )
    
    return train_loader, val_loader, train_dataset.classes

def train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, num_epochs):
    os.makedirs(config.LOG_DIR, exist_ok=True)
    writer = SummaryWriter(log_dir=config.LOG_DIR)
    
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)
    
    best_val_acc = 0.0
    early_stop_count = 0
    
    for epoch in range(num_epochs):
        print(f'\nEpoch {epoch+1}/{num_epochs}')
        print('-' * 10)
        
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        start_time = time.time()
        
        for inputs, labels in train_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            train_correct += torch.sum(preds == labels.data)
            train_total += inputs.size(0)
        
        train_loss = train_loss / train_total
        train_acc = train_correct.double() / train_total
        
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)
                
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += torch.sum(preds == labels.data)
                val_total += inputs.size(0)
        
        val_loss = val_loss / val_total
        val_acc = val_correct.double() / val_total
        
        if config.USE_LR_SCHEDULER:
            scheduler.step(val_loss)
        
        writer.add_scalar('Loss/train', train_loss, epoch)
        writer.add_scalar('Loss/val', val_loss, epoch)
        writer.add_scalar('Accuracy/train', train_acc, epoch)
        writer.add_scalar('Accuracy/val', val_acc, epoch)
        
        epoch_time = time.time() - start_time
        print(f'Train Loss: {train_loss:.4f} Acc: {train_acc:.4f}')
        print(f'Val Loss: {val_loss:.4f} Acc: {val_acc:.4f}')
        print(f'Epoch Time: {epoch_time:.2f}s')
        
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            early_stop_count = 0
            os.makedirs(config.MODEL_SAVE_DIR, exist_ok=True)
            best_model_path = os.path.join(config.MODEL_SAVE_DIR, 'best_model.pth')
            torch.save(model.state_dict(), best_model_path)
            print(f'New best model saved with accuracy: {best_val_acc:.4f}')
        else:
            early_stop_count += 1
            if early_stop_count >= config.EARLY_STOP_PATIENCE:
                print(f'Early stopping after {config.EARLY_STOP_PATIENCE} epochs without improvement')
                break
    
    writer.close()
    return model

def main():
    print("Initializing training...")
    
    train_transform, val_test_transform = get_data_transforms()
    train_loader, val_loader, classes = get_dataloaders(train_transform, val_test_transform)
    
    print(f"Classes found: {classes}")
    print(f"Training samples: {len(train_loader.dataset)}")
    print(f"Validation samples: {len(val_loader.dataset)}")
    
    model = CropLeafClassifier(num_classes=config.NUM_CLASSES)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECAY)
    
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=config.LR_DECAY_FACTOR, 
        patience=config.LR_DECAY_PATIENCE, verbose=True
    )
    
    model = train_model(model, train_loader, val_loader, criterion, optimizer, scheduler, config.EPOCHS)
    
    print("Training complete!")

if __name__ == '__main__':
    main()