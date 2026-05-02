import os
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, precision_score, recall_score, f1_score
import matplotlib.pyplot as plt
import seaborn as sns
from train_model import CropLeafClassifier
from config import config

def evaluate_model(model_path, test_loader, classes, device):
    model = CropLeafClassifier(num_classes=config.NUM_CLASSES)
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)
    model.eval()
    
    all_preds = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            outputs = model(inputs)
            probs = F.softmax(outputs, dim=1)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.extend(probs.cpu().numpy())
    
    return np.array(all_labels), np.array(all_preds), np.array(all_probs)

def plot_confusion_matrix(y_true, y_pred, classes, save_path):
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=classes, yticklabels=classes)
    plt.title('Confusion Matrix')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def calculate_metrics(y_true, y_pred):
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision_macro': precision_score(y_true, y_pred, average='macro'),
        'precision_micro': precision_score(y_true, y_pred, average='micro'),
        'recall_macro': recall_score(y_true, y_pred, average='macro'),
        'recall_micro': recall_score(y_true, y_pred, average='micro'),
        'f1_macro': f1_score(y_true, y_pred, average='macro'),
        'f1_micro': f1_score(y_true, y_pred, average='micro'),
    }
    
    per_class_metrics = {}
    cr = classification_report(y_true, y_pred, target_names=config.CLASSES, output_dict=True)
    for class_name in config.CLASSES:
        if class_name in cr:
            per_class_metrics[class_name] = {
                'precision': cr[class_name]['precision'],
                'recall': cr[class_name]['recall'],
                'f1': cr[class_name]['f1-score'],
                'support': cr[class_name]['support']
            }
    
    return metrics, per_class_metrics

def print_metrics(metrics, per_class_metrics, classes):
    print("\n=== Overall Metrics ===")
    for metric, value in metrics.items():
        print(f"{metric}: {value:.4f}")
    
    print("\n=== Per-class Metrics ===")
    print(f"{'Class':<15} {'Precision':<10} {'Recall':<10} {'F1':<10} {'Support':<10}")
    print("-" * 55)
    for class_name, metrics_dict in per_class_metrics.items():
        print(f"{class_name:<15} {metrics_dict['precision']:<10.4f} {metrics_dict['recall']:<10.4f} {metrics_dict['f1']:<10.4f} {metrics_dict['support']:<10}")
    
    print("\n=== Classification Report ===")
    print(classification_report(classes, classes, output_dict=False))

def main():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    
    transform = transforms.Compose([
        transforms.Resize(config.IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    test_dataset = datasets.ImageFolder(
        root=os.path.join(config.PROCESSED_DATA_DIR, 'test'),
        transform=transform
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=config.BATCH_SIZE,
        shuffle=False,
        num_workers=config.NUM_WORKERS,
        pin_memory=config.PIN_MEMORY
    )
    
    model_path = os.path.join(config.MODEL_SAVE_DIR, 'best_model.pth')
    
    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return
    
    y_true, y_pred, y_probs = evaluate_model(model_path, test_loader, config.CLASSES, device)
    
    metrics, per_class_metrics = calculate_metrics(y_true, y_pred)
    
    print_metrics(metrics, per_class_metrics, config.CLASSES)
    
    if config.CONFUSION_MATRIX_PLOT:
        os.makedirs(config.LOG_DIR, exist_ok=True)
        cm_path = os.path.join(config.LOG_DIR, 'confusion_matrix.png')
        plot_confusion_matrix(y_true, y_pred, config.CLASSES, cm_path)
        print(f"\nConfusion matrix saved to: {cm_path}")
    
    results = {
        'overall_metrics': metrics,
        'per_class_metrics': per_class_metrics,
        'confusion_matrix': confusion_matrix(y_true, y_pred).tolist()
    }
    
    import json
    results_path = os.path.join(config.LOG_DIR, 'evaluation_results.json')
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"Evaluation results saved to: {results_path}")

if __name__ == '__main__':
    main()