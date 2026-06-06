import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
import os
import numpy as np
import json

class LeafDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.image_paths = []
        self.labels = []
        self.label_to_idx = {'幼嫩期': 0, '成熟期': 1, '过熟期': 2, '衰老期': 3}
        
        for maturity in os.listdir(root_dir):
            maturity_path = os.path.join(root_dir, maturity)
            if os.path.isdir(maturity_path):
                for img_name in os.listdir(maturity_path):
                    if img_name.endswith(('.jpg', '.jpeg', '.png')):
                        self.image_paths.append(os.path.join(maturity_path, img_name))
                        self.labels.append(self.label_to_idx.get(maturity, 0))
    
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        image = Image.open(img_path).convert('RGB')
        label = self.labels[idx]
        
        if self.transform:
            image = self.transform(image)
        
        return image, label

class LeafMaturityModel(nn.Module):
    def __init__(self, num_classes=4, pretrained=True):
        super(LeafMaturityModel, self).__init__()
        self.base_model = models.resnet50(pretrained=pretrained)
        self.base_model.fc = nn.Linear(self.base_model.fc.in_features, 512)
        self.dropout = nn.Dropout(0.5)
        self.classifier = nn.Linear(512, num_classes)
    
    def forward(self, x):
        x = self.base_model(x)
        x = self.dropout(x)
        x = self.classifier(x)
        return x

class DeepLearningMaturityDetector:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_classes = 4
        self.idx_to_label = {0: '幼嫩期', 1: '成熟期', 2: '过熟期', 3: '衰老期'}
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        self.model = LeafMaturityModel(num_classes=self.num_classes, pretrained=False)
        self.model.to(self.device)
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print("未加载预训练模型，将使用默认颜色分析算法")
    
    def load_model(self, model_path):
        try:
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            print(f"成功加载模型: {model_path}")
        except Exception as e:
            print(f"模型加载失败: {e}")
    
    def predict(self, image_path):
        try:
            image = Image.open(image_path).convert('RGB')
            image = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(image)
                probabilities = torch.softmax(outputs, dim=1)
                confidence, predicted = torch.max(probabilities, 1)
            
            maturity = self.idx_to_label[predicted.item()]
            confidence_score = confidence.item()
            
            return {
                'maturity': maturity,
                'confidence': confidence_score,
                'probabilities': {
                    self.idx_to_label[i]: float(probabilities[0][i]) 
                    for i in range(self.num_classes)
                }
            }
        except Exception as e:
            print(f"预测错误: {e}")
            return None
    
    def predict_batch(self, image_paths):
        results = []
        for path in image_paths:
            result = self.predict(path)
            if result:
                results.append({'image_path': path, **result})
        return results
    
    def train_model(self, data_dir, epochs=20, batch_size=32, lr=0.0001):
        transform_train = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(15),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        dataset = LeafDataset(data_dir, transform=transform_train)
        
        train_size = int(0.7 * len(dataset))
        val_size = int(0.15 * len(dataset))
        test_size = len(dataset) - train_size - val_size
        
        train_dataset, val_dataset, test_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size, test_size]
        )
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        test_loader = DataLoader(test_dataset, batch_size=batch_size)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.Adam(self.model.parameters(), lr=lr)
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'val_loss', patience=3, factor=0.1)
        
        best_val_acc = 0.0
        training_history = []
        
        for epoch in range(epochs):
            self.model.train()
            train_loss = 0.0
            train_correct = 0
            train_total = 0
            
            for images, labels in train_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(images)
                loss = criterion(outputs, labels)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs.data, 1)
                train_total += labels.size(0)
                train_correct += (predicted == labels).sum().item()
            
            train_acc = train_correct / train_total
            train_loss = train_loss / train_total
            
            self.model.eval()
            val_loss = 0.0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for images, labels in val_loader:
                    images, labels = images.to(self.device), labels.to(self.device)
                    outputs = self.model(images)
                    loss = criterion(outputs, labels)
                    
                    val_loss += loss.item() * images.size(0)
                    _, predicted = torch.max(outputs.data, 1)
                    val_total += labels.size(0)
                    val_correct += (predicted == labels).sum().item()
            
            val_acc = val_correct / val_total
            val_loss = val_loss / val_total
            
            scheduler.step(val_loss)
            
            training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'train_acc': train_acc,
                'val_loss': val_loss,
                'val_acc': val_acc
            })
            
            print(f"Epoch [{epoch+1}/{epochs}], "
                  f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f}, "
                  f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}")
            
            if val_acc > best_val_acc:
                best_val_acc = val_acc
                torch.save(self.model.state_dict(), 'best_model.pth')
                print("保存最佳模型")
        
        print(f"训练完成，最佳验证准确率: {best_val_acc:.4f}")
        
        self.model.load_state_dict(torch.load('best_model.pth'))
        self.model.eval()
        
        test_correct = 0
        test_total = 0
        with torch.no_grad():
            for images, labels in test_loader:
                images, labels = images.to(self.device), labels.to(self.device)
                outputs = self.model(images)
                _, predicted = torch.max(outputs.data, 1)
                test_total += labels.size(0)
                test_correct += (predicted == labels).sum().item()
        
        test_acc = test_correct / test_total
        print(f"测试准确率: {test_acc:.4f}")
        
        with open('training_history.json', 'w', encoding='utf-8') as f:
            json.dump(training_history, f, ensure_ascii=False, indent=2)
        
        return {
            'best_val_acc': best_val_acc,
            'test_acc': test_acc,
            'training_history': training_history
        }

def train_model_main(data_dir, model_save_path='leaf_maturity_model.pth'):
    detector = DeepLearningMaturityDetector()
    result = detector.train_model(data_dir, epochs=20)
    torch.save(detector.model.state_dict(), model_save_path)
    print(f"模型已保存到: {model_save_path}")
    return result

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, required=True, help='数据集目录')
    parser.add_argument('--save_path', type=str, default='leaf_maturity_model.pth', help='模型保存路径')
    args = parser.parse_args()
    
    train_model_main(args.data_dir, args.save_path)