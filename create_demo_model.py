import torch
import torch.nn as nn
from torchvision import models

def create_demo_model():
    class LeafMaturityModel(nn.Module):
        def __init__(self, num_classes=4):
            super(LeafMaturityModel, self).__init__()
            self.base_model = models.resnet50(pretrained=False)
            self.base_model.fc = nn.Linear(self.base_model.fc.in_features, 512)
            self.dropout = nn.Dropout(0.5)
            self.classifier = nn.Linear(512, num_classes)
        
        def forward(self, x):
            x = self.base_model(x)
            x = self.dropout(x)
            x = self.classifier(x)
            return x
    
    model = LeafMaturityModel(num_classes=4)
    torch.save(model.state_dict(), 'models/leaf_maturity_model.pth')
    
    print("演示模型已创建成功！")
    print("模型路径: models/leaf_maturity_model.pth")
    print("支持类别: 幼嫩期, 成熟期, 过熟期, 衰老期")

if __name__ == '__main__':
    create_demo_model()