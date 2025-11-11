import torch

print(f"PyTorch: {torch.__version__}")
print(f"CUDA Available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"Device: {torch.cuda.get_device_name(0)}")
    capability = torch.cuda.get_device_capability(0)
    print(f"Compute Capability: {capability[0]}.{capability[1]} (sm_{capability[0]}{capability[1]})")
    print(f"Device Count: {torch.cuda.device_count()}")
    print("\n✅ GPU détecté et opérationnel")
else:
    print("CUDA not available!")
