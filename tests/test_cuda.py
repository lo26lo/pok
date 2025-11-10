import torch

print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
    capability = torch.cuda.get_device_capability(0)
    print(f"Compute Capability: {capability[0]}.{capability[1]} (sm_{capability[0]}{capability[1]})")
    print(f"Device Count: {torch.cuda.device_count()}")
    
    # Test si besoin de CPU fallback
    if capability[0] >= 12:
        print("\n⚠️  Ce GPU nécessite un basculement vers CPU")
        print("⚠️  PyTorch stable ne supporte que jusqu'à sm_90")
        print("⚠️  Votre GPU a compute capability sm_120")
    else:
        print("\n✅ Ce GPU est compatible avec PyTorch stable")
else:
    print("CUDA not available!")
