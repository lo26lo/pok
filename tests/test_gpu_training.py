import torch

print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    device = torch.device("cuda:0")
    print(f"Device: {torch.cuda.get_device_name(0)}")
    print(f"Compute Capability: {torch.cuda.get_device_capability(0)}")
    
    # Test d'allocation mémoire GPU
    try:
        print("\n🧪 Test d'allocation mémoire GPU...")
        x = torch.randn(1000, 1000, device=device)
        y = torch.randn(1000, 1000, device=device)
        z = torch.matmul(x, y)
        print(f"✅ Multiplication matricielle GPU réussie!")
        print(f"   Résultat shape: {z.shape}")
        print(f"   Device: {z.device}")
        
        # Test de transfert CPU <-> GPU
        print("\n🧪 Test de transfert CPU <-> GPU...")
        cpu_tensor = torch.randn(100, 100)
        gpu_tensor = cpu_tensor.to(device)
        back_to_cpu = gpu_tensor.cpu()
        print(f"✅ Transfert CPU <-> GPU réussi!")
        
        print("\n✅ LE GPU EST PLEINEMENT FONCTIONNEL!")
        print("✅ Vous pouvez lancer l'entraînement YOLO avec device='0'")
        
    except Exception as e:
        print(f"\n❌ Erreur lors du test GPU: {e}")
        print("❌ Le GPU n'est pas utilisable pour l'entraînement")
else:
    print("❌ CUDA non disponible!")
